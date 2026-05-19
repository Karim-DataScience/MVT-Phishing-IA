# Cyber Detection Pipeline v6 — Rapport Final
Date: 2026-05-14 15:43

## Résultats par format

| Format | Modèle | AUC | F1 | Latence | Statut |
|--------|--------|-----|----|---------|---------|| HTML | LightGBM+Platt | 0.9878 | 0.9441 | 0.49ms | ✅ PROD-READY |
| HTML | Stacking | 0.9894 | 0.9441 | 2ms | ✅ PROD-READY |
| QR | LightGBM URL | 0.9814 | 0.9400 | 0.49ms | ✅ PROD-READY |
| QR | CNN Hybride TTA | 0.9775 | 0.9100 | ~50ms GPU | ✅ |
| PDF | LightGBM | 0.9999 | 0.9983 | 0.49ms | ✅ avec réserves |
| Word | LightGBM | 1.0000 | 1.0000 | 0.49ms | ⚠ CONFOUND |
| Excel | LightGBM | 1.0000 | 1.0000 | 0.49ms | ⚠ CONFOUND |
