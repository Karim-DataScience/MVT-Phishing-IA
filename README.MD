
# Cyber Detection Pipeline & Production API — CIC Trap4Phish 2025

Ce dépôt contient l'infrastructure complète de recherche, d'entraînement et de déploiement d'une solution d'intelligence artificielle dédiée à la détection de menaces cyber multiformats. Le système est conçu pour analyser et classifier de manière robuste cinq vecteurs d'attaque majeurs : PDF, HTML, Word (Docx), Excel (Xlsx) et les attaques par QR Codes (Quishing).

---

## 1. Contexte, Enjeux et Objectifs

### Le contexte
Avec la complexification des méthodes de hameçonnage (phishing), les attaquants délaissent les simples liens textuels au profit de vecteurs plus sophistiqués : documents bureautiques infectés, PDF contenant des redirections obfusquées, ou encore le "Quishing" (utilisation de QR codes malveillants). 

### Les enjeux
L'utilisation de jeux de données académiques en cybersécurité se heurte souvent au problème de la fuite de données (Data Leakage) et des facteurs de confusion (Confounding Factors). Un modèle peut sembler performant en laboratoire tout en étant inutilisable en production s'il a appris à classifier des artefacts de génération plutôt que de réelles menaces.

### Les objectifs du projet
1. **Auditer et assainir** le jeu de données récent *CIC Trap4Phish 2025*.
2. **Développer des modèles spécialisés** par format de fichier, capables de généraliser sur de nouvelles menaces.
3. **Calibrer les probabilités** pour fournir à un Centre Opérationnel de Sécurité (SOC) des indicateurs de risque fiables.
4. **Déployer la solution** sous forme de micro-service (API REST conteneurisée) prêt pour la production.

---

## 2. Source des Données (Dataset)

Les données utilisées pour entraîner et évaluer ces modèles proviennent de l'Institut Canadien de Cybersécurité (CIC).

* **Nom du dataset :** CIC Trap4Phish 2025
* **Informations générales :** [Présentation du dataset](https://www.unb.ca/cic/datasets/trap4phish2025.html)

**Modalités d'accès :**
Le téléchargement de l'ensemble des données brutes nécessite de remplir un formulaire institutionnel (à des fins de statistiques internes pour le CIC).
* **Lien de téléchargement :** [Formulaire d'accès CIC](https://cicresearch.ca/IOTDataset/CIC_Trap4Phish_2025_Dataset/)

*Note : Les données tabulaires pré-traitées nécessaires à l'exécution de l'API sont incluses dans le dossier `Final CSV/`. Les images brutes des QR Codes sont exclues du dépôt (voir section 5).*

---

## 3. Architecture du Dépôt

Le projet est structuré pour séparer distinctement la phase de recherche (R&D) de la phase de production.

```text
.
├── .gitattributes                  # Configuration Git LFS (modèles .pkl, .pt)
├── .gitignore                      # Filtre d'exclusion pour les données brutes lourdes
├── README.md                       # Documentation générale
│
├── cyber_detection_pipeline.ipynb  # (v1) Évaluation initiale des données
├── cyber_pipeline_v2.ipynb         # (v2) Analyse de leakage et CNN Vision
├── cyber_pipeline_v3.ipynb         # (v3) Structuration du code de production
├── cyber_pipeline_v4.ipynb         # (v4) Stratégie de découpage par Payload Hash
├── cyber_pipeline_v5.ipynb         # (v5) Calibration de probabilités (Platt Scaling)
├── cyber_pipeline_v6.ipynb         # (v6) Architectures d'Ensemble & Stacking
├── cyber_pipeline_v7.ipynb         # (v7) Version finale de référence et d'audit
│
├── deploy/                         # Infrastructure de Déploiement Production (FastAPI)
│   ├── app.py                      # Serveur d'API asynchrone 
│   ├── Dockerfile                  # Environnement de conteneurisation
│   ├── docker-compose.yml          # Orchestration (API + Monitoring)
│   ├── prometheus.yml              # Configuration de la télémétrie
│   └── requirements.txt            # Dépendances logicielles strictes
│
├── Feature Extraction Code/        # Code source d'extraction des caractéristiques
├── Final CSV/                      # Jeux de données tabulaires nettoyés
├── models_v6/                      # Artefacts finaux de modélisation (Modèles figés)
└── Source Files/
    └── QR Codes/                   # Point de montage des images volumineuses
        └── README.md               # Guide spécifique aux QR Codes

```

---

## 4. Méthodologie et Évolution de la Recherche

La progression des notebooks (de la v1 à la v7) documente notre démarche scientifique :

1. **Diagnostic Anti-Leakage (v1-v3) :** Identification et suppression des variables biaisées par la génération du dataset (ex. `macro_present` dans les documents Word qui séparait artificiellement les classes de manière parfaite).
2. **Découpage par Empreinte (v4) :** Implémentation d'un partitionnement Train/Validation/Test fondé sur l'empreinte cryptographique de la charge utile (Payload Hash). Cela garantit l'absence totale de contamination entre les ensembles.
3. **Calibration pour le SOC (v5-v7) :** Ajustement des scores de sortie via la méthode de *Platt Scaling*. Les scores représentent désormais de véritables probabilités, permettant la mise en place de seuils d'action stricts :
* **Score > 0.80 :** Blocage Immédiat (BLOCK).
* **Score 0.50 - 0.80 :** Inspection Manuelle (REVIEW).
* **Score < 0.50 :** Fichier Sain (ALLOW).



---

## 5. Déploiement Opérationnel

L'environnement d'inférence est isolé sous forme de micro-services via Docker, intégrant une API REST (FastAPI) et un exportateur de métriques pour Prometheus.

### Lancement de l'infrastructure

Grâce à Git LFS, les modèles pré-entraînés sont inclus dans le dépôt. Aucune phase d'entraînement n'est requise pour lancer l'API.

```bash
cd deploy
docker-compose up -d --build

```

### Endpoints de l'API

* `GET /health` : Vérification de l'état du service et des modèles chargés en mémoire.
* `POST /predict` : Point d'entrée principal pour l'analyse d'un fichier (routage dynamique selon le type MIME).
* `GET /metrics` : Exposition des indicateurs de dérive (Data Drift) et de performance pour Prometheus et Grafana.



***


