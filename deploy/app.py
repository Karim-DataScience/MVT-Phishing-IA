"""
Cyber Detection API - v7 Production
FastAPI endpoint pour la détection de fichiers malveillants.
"""
import os, math, time, json, hashlib, warnings
from pathlib import Path
from typing import Literal, Optional
from contextlib import asynccontextmanager

import numpy as np
import joblib
import shap
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")

# ── Modèles chargés au démarrage ──────────────────────────────
MODELS_DIR = Path(os.getenv("MODELS_DIR", "./models_v7"))
MODELS = {}
SCALERS = {}
FEATURES = {}
CALIBRATION = {}

def load_models():
    """Charge tous les modèles au démarrage de l'API."""
    for fmt in ["pdf", "html", "word", "excel", "qr"]:
        try:
            MODELS[fmt]   = joblib.load(MODELS_DIR / f"lgbm_all_{fmt}.pkl")
            SCALERS[fmt]  = joblib.load(MODELS_DIR / f"scaler_all_{fmt}.pkl")
            with open(MODELS_DIR / f"features_all_{fmt}.json") as f:
                FEATURES[fmt] = json.load(f)
            cal_path = MODELS_DIR / f"calibration_{fmt}.json"
            if cal_path.exists():
                with open(cal_path) as f:
                    CALIBRATION[fmt] = json.load(f)
            print(f"✅ {fmt}: {len(FEATURES[fmt])} features chargées")
        except FileNotFoundError:
            print(f"⚠ Modèle {fmt} non trouvé dans {MODELS_DIR}")

# ── Drift Monitor ──────────────────────────────────────────────
DRIFT_HISTORY = {fmt: [] for fmt in ["pdf","html","word","excel","qr"]}
REFERENCE_SCORES = {}  # chargé depuis fichier de référence

def psi(expected, actual, n_bins=10):
    bins=np.percentile(expected,np.linspace(0,100,n_bins+1))
    bins[0]-=1e-6; bins[-1]+=1e-6
    e=np.histogram(expected,bins=bins)[0]/len(expected)
    a=np.histogram(actual,  bins=bins)[0]/len(actual)
    e=np.where(e==0,1e-6,e); a=np.where(a==0,1e-6,a)
    return float(np.sum((a-e)*np.log(a/e)))

# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield

# ── API ───────────────────────────────────────────────────────
app = FastAPI(
    title="Cyber Detection API",
    description="Détection de fichiers malveillants — CIC Trap4Phish 2025",
    version="7.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ── Modèles Pydantic ─────────────────────────────────────────
class PredictRequest(BaseModel):
    format: Literal["pdf","html","word","excel","qr"] = Field(
        ..., description="Format du fichier analysé")
    features: dict[str, float] = Field(
        ..., description="Features extraites par le module d'extraction statique")
    calibrate: bool = Field(True, description="Appliquer la calibration Platt")
    return_shap: bool = Field(False, description="Retourner les top-5 SHAP features")

class PredictResponse(BaseModel):
    format: str
    label: Literal["benign","malicious"]
    risk_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    action: Literal["ALLOW","REVIEW","BLOCK"]
    calibrated: bool
    inference_ms: float
    top_features: list[dict] = []
    warnings: list[str] = []

class HealthResponse(BaseModel):
    status: str
    models_loaded: list[str]
    version: str

class DriftRequest(BaseModel):
    format: str
    scores: list[float]

class DriftResponse(BaseModel):
    format: str
    psi: float
    alert: bool
    level: str
    n_samples: int

# ── Endpoints ────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status":"healthy","models_loaded":list(MODELS.keys()),"version":"7.0.0"}

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest, bg: BackgroundTasks):
    fmt = req.format
    if fmt not in MODELS:
        raise HTTPException(404, f"Modèle '{fmt}' non disponible")

    t0 = time.perf_counter()
    fn = FEATURES[fmt]
    X  = np.array([[req.features.get(f, 0) for f in fn]], dtype=np.float64)
    Xs = SCALERS[fmt].transform(X)
    p  = float(MODELS[fmt].predict_proba(Xs)[0, 1])

    # Calibration Platt
    is_cal = False
    if req.calibrate and fmt in CALIBRATION:
        cal = CALIBRATION[fmt]
        a, b = cal.get("a", 1.0), cal.get("b", 0.0)
        eps = 1e-10
        logit = math.log(max(p,eps)/max(1-p,eps))
        p = float(1/(1+math.exp(-(a*logit+b))))
        is_cal = True

    label  = "malicious" if p >= 0.5 else "benign"
    action = "BLOCK" if p > 0.80 else ("REVIEW" if p > 0.50 else "ALLOW")
    inf_ms = (time.perf_counter()-t0)*1000

    # SHAP (optionnel, ralentit ~5ms)
    top_feats = []
    if req.return_shap and fmt in MODELS:
        exp = shap.TreeExplainer(MODELS[fmt])
        sv  = exp.shap_values(Xs)[0]
        for j in np.argsort(np.abs(sv))[::-1][:5]:
            top_feats.append({"feature":fn[j],"shap":round(float(sv[j]),4),
                               "direction":"→ malicious" if sv[j]>0 else "→ benign"})

    warns = []
    if fmt in ("word","excel"):
        warns.append("⚠ Confound dataset — valider sur données mixtes avant production")

    # Background: enregistrer le score pour le drift monitoring
    async def record_score():
        DRIFT_HISTORY[fmt].append(p)
    bg.add_task(record_score)

    return PredictResponse(format=fmt,label=label,risk_score=round(p,4),
                            confidence=round(abs(p-0.5)*2,4),action=action,
                            calibrated=is_cal,inference_ms=round(inf_ms,3),
                            top_features=top_feats,warnings=warns)

@app.post("/drift", response_model=DriftResponse)
async def drift_check(req: DriftRequest):
    fmt = req.format
    scores = np.array(req.scores)
    if fmt not in REFERENCE_SCORES or len(REFERENCE_SCORES[fmt])==0:
        return DriftResponse(format=fmt,psi=0.0,alert=False,
                              level="⚠ Pas de référence — entraîner d\'abord",n_samples=len(scores))
    psi_val = psi(REFERENCE_SCORES[fmt], scores)
    alert   = psi_val > 0.10
    level   = ("🔴 CRITIQUE — Retrain!" if psi_val>0.20 else
                "🟠 ATTENTION" if psi_val>0.10 else "✅ STABLE")
    return DriftResponse(format=fmt,psi=round(psi_val,4),alert=alert,level=level,n_samples=len(scores))

@app.get("/metrics")
async def metrics():
    """Métriques de monitoring (format Prometheus-compatible)."""
    lines = [
        "# HELP cyber_drift_psi PSI drift score by format",
        "# TYPE cyber_drift_psi gauge"
    ]
    for fmt, hist in DRIFT_HISTORY.items():
        if hist:
            # Calcul du PSI entre les 1000 premiers éléments historiques (référence) et les 100 derniers (actuels)
            psi_val = psi(hist[:1000], hist[-100:]) if len(hist) > 100 else 0.0
            lines.append(f'cyber_drift_psi{{format="{fmt}"}} {psi_val:.4f}')
            
    return "\n".join(lines)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, workers=4)