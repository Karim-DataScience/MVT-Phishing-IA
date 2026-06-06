# 🛡️ Cyber Detection Pipeline — CIC Trap4Phish 2025

> **Détection multi-format de fichiers malveillants par IA** — PDF, HTML, Word, Excel, QR Code (Quishing)  
> Pipeline de recherche et déploiement production · v1 → vFinale · LightGBM · DistilBERT · MobileBERT

---

## 📌 Contexte et objectifs

Face à la sophistication croissante des cyberattaques — notamment le phishing multi-vecteur, le quishing (QR codes malveillants) et les documents bureautiques piégés — les mécanismes de sécurité statiques (blacklists, règles heuristiques) montrent leurs limites. Ce projet conçoit et déploie un pipeline de détection basé sur l'IA, capable d'analyser simultanément cinq formats d'attaque distincts avec des garanties de performance mesurées.

Ce dépôt documente **10 versions itératives** d'un système de détection, depuis l'audit initial du dataset jusqu'à une API REST containérisée et monitorée en production.

---

## 📊 Résultats finaux mesurés (vFinale — test set)

| Modèle | Format | AUC | F1 | ECE | Latence | Statut |
|--------|--------|-----|-----|-----|---------|--------|
| **LightGBM + Platt** | HTML features | **0.9881** | **0.9475** | **0.044** | **1.26ms** | ✅ Prod-Ready |
| LightGBM 5-fold CV | HTML features | 0.9855 ± 0.0023 | — | — | — | IC95% [0.981, 0.990] |
| TF-IDF word+char + Platt | HTML texte | 0.9790 | 0.8966 | 0.078 | 0.11ms | ✅ Edge/CPU |
| DistilBERT v9 (512tok, 5ep) | HTML texte | 0.9795 | 0.9050 | 0.126 | ~4ms GPU | ✅ GPU prod |
| MobileBERT v9 (512tok, 5ep) | HTML texte | 0.9744 | 0.8723 | 0.131 | ~58ms CPU | ✅ Edge |
| LightGBM URL features | QR Quishing | 0.9814 | 0.9325 | 0.026 | 0.5ms | ✅ Prod-Ready |
| LightGBM | PDF | 0.9999 | 0.9983 | — | 0.5ms | ⚠️ Réserves |
| LightGBM | Word/Excel | 1.000 | 1.000 | N/A | 0.5ms | ⚠️ Confond |

> **⚠️ Word/Excel AUC=1.000** : confond de format (OOXML vs VBA), non un vrai signal. À valider sur dataset mixte avant déploiement.

---

## 🏗️ Architecture du système

```
FICHIER ENTRANT (PDF / HTML / DOCX / XLSX / QR PNG)
        │
        ├─ Détection de format (magic bytes + extension)
        │
        ├─ PDF    → 40 features statiques  → LightGBM + Platt
        ├─ HTML   → 40 features DOM/URL    → LightGBM + Platt  ← RECOMMANDÉ
        │          Texte brut              → TF-IDF / DistilBERT
        ├─ Word   → 40 features OLE/XML    → LightGBM (⚠ confond)
        ├─ Excel  → 48 features macros     → LightGBM (⚠ confond)
        └─ QR     → 34 URL features        → LightGBM + CNN EfficientNet-B0
                │
        COUCHE DE DÉCISION SOC
        ┌──────────────────────────────────────┐
        │ score > 0.80 → BLOCK                │
        │ score 0.50–0.80 → REVIEW            │
        │ score < 0.50 → ALLOW                │
        │ + SHAP top-5 features               │
        │ + PSI drift monitoring              │
        └──────────────────────────────────────┘
```

---

## 📂 Structure du dépôt

```
.
├── README.md
├── .gitignore
│
├── notebooks/                        # Pipeline de recherche (v1 → vFinale)
│   ├── cyber_pipeline_v1.ipynb       # Évaluation initiale + audit leakage
│   ├── cyber_pipeline_v2.ipynb       # Fix QR CSV + split SHA-256
│   ├── cyber_pipeline_v3.ipynb       # LightGBM + SHAP + Platt v1
│   ├── cyber_pipeline_v4.ipynb       # Stacking + Platt manuel (fix crash)
│   ├── cyber_pipeline_v5.ipynb       # ECE=0.044, MLP convergence fix
│   ├── cyber_pipeline_v6.ipynb       # XGBoost + LGB/XGB/RF/MLP stack
│   ├── cyber_pipeline_v7.ipynb       # MC-Dropout QR CNN + FastAPI
│   ├── cyber_pipeline_v8.ipynb       # DistilBERT / MobileBERT (HTML texte)
│   ├── cyber_pipeline_v9.ipynb       # Fix MAX_CHARS + 5 epochs BERT
│   ├── cyber_pipeline_v10.ipynb      # Fix label bug + PSI ref=val
│   └── cyber_pipeline_FINALE.ipynb   # Version consolidée production
│
├── deploy/                           # Infrastructure de déploiement
│   ├── app.py                        # API FastAPI asynchrone
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── requirements.txt
│
├── models_final/                     # Artefacts de modélisation (Git LFS)
│   ├── lgb_html_feat.pkl             # LightGBM HTML features (6.7 MB)
│   ├── sc_html_feat.pkl              # StandardScaler
│   ├── fn_html_feat.json             # Noms des 40 features
│   ├── cal_lgb.json                  # Paramètres Platt scaling
│   ├── lgb_metrics.json              # Métriques finales mesurées
│   ├── tfidf_word.pkl                # TF-IDF word n-grams
│   ├── tfidf_char.pkl                # TF-IDF char n-grams
│   ├── lr_tfidf.pkl                  # Logistic Regression (texte)
│   ├── cal_tfidf.json
│   ├── rapport_final.json            # Rapport complet JSON
│   └── historique_v1_vfinal.csv      # Tableau comparatif toutes versions
│
├── models_v9/                        # Modèles BERT & Historique complet complet (Externalisés)
│   └── ⚠️ [À TÉLÉCHARGER VIA LE DRIVE] Modèles complets DistilBERT / MobileBERT (>1.5 Go)
│
├── Feature Extraction Code/          # Scripts d'extraction par format
│   ├── HTML_Feature_Extraction.ipynb
│   ├── PDF_Feature_Extraction.ipynb
│   ├── Excel_Feature_Extraction.ipynb
│   └── Doc_Feature_Extraction.ipynb
│
└── Source Files/
    ├── HTML/
    │   └── SubProject/output/dataset.tsv   # 13 054 textes HTML extraits
    └── QR Codes/
        ├── QR_All_benign/                  # 429 976 PNG (Git LFS)
        └── QR_All_Malicious/               # 575 762 PNG (Git LFS)
```

---

## ⚙️ Installation et lancement

### Prérequis

```bash
Python 3.11+
CUDA 12.0+ (recommandé pour DistilBERT/MobileBERT)
Docker + Docker Compose (pour le déploiement)
Git LFS (pour les modèles .pkl/.pt et les images QR)
```

### Installation

```bash
git lfs install
git clone https://github.com/Karim-DataScience/MVT-Phishing-IA.git
cd cyber-detection-pipeline
pip install -r deploy/requirements.txt
```
### Téléchargement des modèles entraînés (Fine-tunés)

Pour éviter d'alourdir le dépôt GitHub, seuls les fichiers tabulaires légers de la **v10 et vFinale** sont inclus directement ici. L'historique complet de toutes les versions ainsi que les architectures BERT lourdes (~1.5 Go) sont hébergés à l'extérieur.

1. Accédez au dossier de stockage :
👉 **[Télécharger l'ensemble des modèles sur Google Drive](https://drive.google.com/drive/folders/1y-oYiO9r7iwRb3rnNDxkcGhG0Owhr6yg?usp=sharing)**
2. Pour utiliser les modèles de Deep Learning (v8/v9), téléchargez les répertoires BERT et placez-les dans le dossier `models_v9/` à la racine du projet pour obtenir la structure suivante :

```text
models_v9/
├── distilbert_v9_final/
├── distilbert_v9_tokenizer/
├── mobilebert_v9_final/
└── mobilebert_v9_tokenizer/

```


### Lancer l'API de production

```bash
cd deploy
docker-compose up -d --build
```

Endpoints disponibles :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | État des modèles chargés |
| `/predict` | POST | Analyse d'un fichier (JSON avec features + texte) |
| `/drift` | POST | Vérification PSI pour monitoring |
| `/metrics` | GET | Métriques Prometheus |
| `/docs` | GET | Swagger UI auto-généré |

### Inférence rapide (sans Docker)

```python
from pathlib import Path
import joblib, json, numpy as np

# Charger le détecteur
lgb   = joblib.load('models_final/lgb_html_feat.pkl')
sc    = joblib.load('models_final/sc_html_feat.pkl')
fn    = json.load(open('models_final/fn_html_feat.json'))

# Prédire (features extraites par votre analyseur statique)
features = {'form_count': 2, 'embedded_js_count': 5, 'url_punct_char_count': 12}
X = np.array([[features.get(f, 0) for f in fn]])
score = lgb.predict_proba(sc.transform(X))[0, 1]
action = 'BLOCK' if score > 0.80 else ('REVIEW' if score > 0.50 else 'ALLOW')
print(f"Score: {score:.4f} → {action}")
```

---

## 🔬 Méthodologie de recherche — v1 à vFinale

| Version | Contribution principale | AUC HTML | Problème corrigé |
|---------|------------------------|----------|-----------------|
| v1 | Audit leakage initial | 0.987 | `file_path` encodait `/Malicious/` dans le chemin |
| v2 | Split QR par hash SHA-256 | 0.663→0.981 | CSV QR non chargé (char Bell 0x07) |
| v3 | LightGBM + SHAP + Platt v1 | 0.989 | Calibration ECE initiale |
| v4 | Stacking + Platt manuel | 0.989 | `CalibratedClassifierCV` incompatible LightGBM |
| v5 | ECE=0.044 stabilisé | 0.989 | MLP `n_iter_no_change=30` convergence |
| v6 | XGBoost + ensemble 4 modèles | 0.989 | P@R95 calcul corrigé |
| v7 | MC-Dropout QR CNN + FastAPI | 0.989 | `macro_present` r=0.9997 supprimé |
| v8 | DistilBERT / MobileBERT intro | 0.9754 | `MAX_CHARS=3000` tronquait tout |
| v9 | Fix BERT (MAX_CHARS=8000, 5ep) | 0.9795 | MobileBERT AUC 0.80→0.97 |
| v10 | Consolidation + fixes | 0.9875 | Label `int` vs `str`, PSI ref=val set |
| **vFinale** | **Production consolidated** | **0.9881** | **Tous les bugs précédents** |

### Insight clé — Signal asymétrique HTML

```
Malicious : médiane 467 chars  (~117 tokens)   → pages phishing minimalistes
Bénin     : médiane 5261 chars (~1315 tokens)  → vrais sites avec contenu

→ 80.7% des malicious tiennent entiers dans 512 tokens BERT
→ 23.5% seulement des bénins tiennent dans 512 tokens
→ Ce signal structurel est exploité par LightGBM ET DistilBERT
```

---

## 📊 Données — CIC Trap4Phish 2025

**Source :** Canadian Institute for Cybersecurity (UNB)  
**Accès :** [https://cicresearch.ca/IOTDataset/CIC_Trap4Phish_2025_Dataset/](https://cicresearch.ca/IOTDataset/CIC_Trap4Phish_2025_Dataset/)

| Format | Samples | Features | Labels |
|--------|---------|----------|--------|
| HTML | 19 997 | 40 | 0/1 (int) |
| PDF | 19 296 | 40 | 0/1 (int) |
| Word | 20 000 | 43 | 0/1 (int) |
| Excel | 20 000 | 48 | 0/1 (int) |
| QR PNG | ~1 005 738 | 34 URL features | 0/1 |
| HTML texte (Docker) | 13 054 | texte brut | benign/malicious |

Les données tabulaires **Final CSV/** sont incluses dans le dépôt.  
Les images QR PNG (~15 GB) hebergé par CIC Research et les modèles BERT (~1.5 GB) sont disponibles sur le [Google Drive du projet](https://drive.google.com/drive/folders/1y-oYiO9r7iwRb3rnNDxkcGhG0Owhr6yg?usp=sharing).

---

## 🔧 Monitoring et dérive

```python
# PSI (Population Stability Index)
# PSI < 0.10  → stable (rien à faire)
# PSI 0.10–0.20 → attention (surveiller)
# PSI > 0.20  → critique (retrain immédiat)

# Endpoint de vérification
POST /drift
{ "format": "html", "scores": [0.82, 0.15, 0.91, ...] }
```

---

## 📄 Licence et citation

Ce projet s'appuie sur le dataset CIC Trap4Phish 2025 :

```bibtex
@dataset{cic_trap4phish_2025,
  author    = {Nejati, H. and others},
  title     = {CIC Trap4Phish 2025},
  year      = {2025},
  publisher = {Canadian Institute for Cybersecurity, University of New Brunswick},
  url       = {https://www.unb.ca/cic/datasets/trap4phish2025.html}
}
```
