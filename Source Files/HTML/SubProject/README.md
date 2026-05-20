# HTML Dataset Parser for Machine Learning (CIC-style)

Ce projet permet d’extraire et de nettoyer des fichiers HTML contenus dans des archives ZIP afin de construire un dataset pour des modèles de Machine Learning (ex: DistilBERT, classification phishing vs benign).

---

# Pipeline global

```text
ZIP HTML Files
      ↓
Docker container (environment isolé)
      ↓
Extraction des fichiers HTML
      ↓
Nettoyage HTML (scripts, styles, tags)
      ↓
Décodage robuste (UTF-8 / CP1252 / Latin-1)
      ↓
Normalisation texte
      ↓
Suppression des doublons (SHA256)
      ↓
Export dataset TSV
      ↓
Machine Learning (DistilBERT / modèles classiques)
````

---

# Pourquoi Docker ?

Docker est utilisé pour :

* Isolation complète de l’environnement
* Installation propre des dépendances
* Reproductibilité du pipeline
* Compatibilité Windows / Linux / WSL

---

# Installation & Build

## 1. Build de l’image

```bash
docker build -t html-parser .
```

---

## 2. Lancer le container

```bash
docker run --rm --network none \
  -v "...\Source Files\HTML:/input:ro" \
  -v "${PWD}\output:/output" \
  html-parser
```

---

# Structure attendue

```text
HTML/
 ├── Benign_HTML.zip
 ├── Malicious_HTML.zip

SubProject/
 ├── Dockerfile
 ├── parser.py
 ├── output/
```

---

# Fonctionnement du parser

Le script fait :

## 1. Extraction ZIP

* Parcourt tous les fichiers `.html` et `.htm`

## 2. Décodage robuste

* UTF-8
* CP1252
* Latin-1 fallback

## 3. Nettoyage HTML

* suppression de :

  * `<script>`
  * `<style>`
  * tags HTML
* suppression du bruit (cookies, login, navigation)

## 4. Normalisation

* conversion en lowercase
* suppression des espaces multiples

## 5. Anti-doublons

* hash SHA256 pour supprimer les contenus identiques

## 6. Export dataset

* format TSV (séparateur tabulation)


---

#  Output dataset

Format :

```text
text    label
```

Exemple :

```text
login to your account enter password secure page    malicious
welcome to official company website information      benign
```

---

# Statistiques affichées

Le script fournit :

* nombre total de fichiers traités
* nombre de fichiers gardés
* distribution des données
* statistiques de longueur (min / max / moyenne / médiane)

---

#  Notes importantes

* Les HTML contiennent beaucoup de bruit (UI, scripts, tracking)
* Le parsing est optimisé pour la vitesse et la robustesse
* Le dataset est destiné à la classification sécurité web

---

# Améliorations possibles

* Feature engineering (URLs, forms, scripts)
* Détection phishing avancée
* Multi-threading pour accélération
* Export HuggingFace dataset format
* Training DistilBERT complet

---

# Auteur

Projet orienté :

* Cybersecurity ML
* Phishing detection
* NLP preprocessing

---

# Licence

Usage éducatif et recherche uniquement.
