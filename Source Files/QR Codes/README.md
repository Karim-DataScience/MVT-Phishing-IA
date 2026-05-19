# Gestion des Échantillons Volumineux de QR Codes

## 1. Raison de l'absence des images sur le dépôt Git

Ce répertoire est conçu pour accueillir l'ensemble des images de QR Codes utilisées dans le cadre de l'apprentissage profond (Deep Learning) pour la détection du "Quishing". 

Le jeu de données complet représente plus de **1 000 000 de fichiers PNG individuels**, pour un poids total brut d'environ **1,4 Go**. Pour des raisons d'optimisation technique, d'intégrité du système de contrôle de version, et pour respecter les limites imposées par GitHub, ces fichiers binaires ne sont pas inclus dans le dépôt de code source.

---

## 2. Accès et Téléchargement des Données

Les données originales proviennent du dataset **CIC Trap4Phish 2025**. Si vous souhaitez reproduire l'entraînement des modèles de vision par ordinateur, vous devez acquérir ces images depuis le serveur officiel du CIC.

1. Accédez à l'explorateur de fichiers du CIC pour ce dataset :
   [Parcourir les fichiers QR Codes - CIC Trap4Phish 2025](https://cicresearch.ca/IOTDataset/CIC_Trap4Phish_2025_Dataset/browse.php?p=Source+Files%2FQR+Codes)
2. *(Note : L'accès aux fichiers nécessite de remplir le formulaire d'inscription du CIC détaillant votre institution et votre adresse e-mail).*
3. Téléchargez les archives contenant les données d'entraînement.

---

## 3. Reconstruction de l'Arborescence Locale

Une fois les données téléchargées, il est impératif d'extraire les images en respectant scrupuleusement la structure de répertoires suivante. Les chemins relatifs au sein des notebooks Jupyter et des scripts d'extraction dépendent de cette organisation.

```text
Source Files/
└── QR Codes/
    ├── QR_All_benign/
    │   ├── all_generated_urls_20251015_161937.csv       # Déjà présent sur Git (Fichier de labels)
    │   └── qrs/                                         # [À CRÉER] Extrayez ici les images bénignes
    │        ├── ben_img_000001.png
    │        └── ... (~429 000 fichiers)
    │
    └── QR_All_Malicious/
        ├── all_generated_urls_20251015_184324.csv       # Déjà présent sur Git (Fichier de labels)
        └── qrs/                                         # [À CRÉER] Extrayez ici les images malveillantes
             ├── mal_img_000001.png
             └── ... (~575 000 fichiers)

```

## 4. Sécurité des commits (Rappel)

Le fichier `.gitignore` situé à la racine du projet est pré-configuré pour exclure automatiquement ces sous-dossiers (`/qrs/`). Cela vous garantit de ne pas saturer la mémoire de votre index Git local après avoir extrait les images.

