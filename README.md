# ORIENT'IA

Assistant intelligent d'orientation pédagogique — ISPM (Institut Supérieur
Polytechnique de Madagascar).

Combine un modèle de Machine Learning (score d'adéquation profil ↔ parcours),
une recherche documentaire (RAG) sur le corpus pédagogique ISPM, et un agent
conversationnel outillé capable de recueillir un profil, comparer des
parcours, justifier ses recommandations et reconnaître ses limites.

> ⚠️ ORIENT'IA est un outil d'aide à l'orientation. Ses recommandations ne
> remplacent ni l'avis d'un conseiller pédagogique, ni une décision
> officielle d'admission.

---

## Sommaire

- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration (.env)](#configuration-env)
- [Base de données](#base-de-données)
- [Lancer le backend](#lancer-le-backend)
- [Structure du projet](#structure-du-projet)
- [Modèle Machine Learning](#modèle-machine-learning)
- [Jeu de données synthétique](#jeu-de-données-synthétique)
- [Dépannage](#dépannage)
- [Équipe](#équipe)

---

## Architecture

```
Sources ISPM (site, brochures, maquettes)
        │
        ▼
Corpus structuré + registre des sources ──► Index vectoriel (RAG)
        │
Profils étudiants (synthétiques + enquête) ──► Modèle ML (RandomForest)
        │                                          │
        └──────────────► Agent conversationnel ◄───┘
                          (outils · RAG · règles)
                                  │
                                  ▼
                  Recommandation argumentée et traçable
```

- **Backend** : FastAPI (Python)
- **Base de données** : PostgreSQL
- **RAG / recherche documentaire** : ChromaDB (index vectoriel local)
- **LLM** : API Gemini (Google)
- **Machine Learning** : scikit-learn (RandomForestClassifier)

---

## Prérequis

- Python 3.11+ (le projet a été développé/testé avec un `venv`)
- PostgreSQL 14+ installé et démarré localement
- Une clé API Gemini (Google AI Studio)
- Git

---

## Installation

```bash
git clone https://github.com/Jakina24K/examen_clinique_m2_chill_team.git
cd examen_clinique_m2_chill_team/backend

# Créer et activer l'environnement virtuel
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

> Adaptez le nom du fichier de dépendances (`requirements.txt`) au nom réel
> utilisé dans le dépôt si différent.

---

## Configuration (.env)

Créez un fichier `.env` à la racine de `backend/` (**ne jamais le commiter**
— vérifiez qu'il est bien listé dans `.gitignore`) :

```properties
# Clé API Gemini (LLM)
GEMINI_API_KEY=votre_cle_gemini

# Répertoire de persistance de l'index vectoriel ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Connexion à la base PostgreSQL
DATABASE_URL=postgresql://postgres:votre_mot_de_passe@localhost:5432/clinique_db

# Authentification
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
APP_NAME=ORIENTIA
DEBUG=True
```

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Clé de l'API Gemini utilisée par l'agent conversationnel |
| `CHROMA_PERSIST_DIR` | Dossier local où ChromaDB persiste l'index vectoriel du corpus |
| `DATABASE_URL` | Chaîne de connexion PostgreSQL (utilisateur, mot de passe, hôte, port, base) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité des tokens d'authentification |
| `APP_NAME` | Nom affiché de l'application |
| `DEBUG` | Active les logs/erreurs détaillés en développement |

---

## Base de données

1. Vérifiez que le service PostgreSQL est démarré.
2. Créez la base si elle n'existe pas encore :

```bash
psql -U postgres -c "CREATE DATABASE clinique_db;"
```

3. Si le projet utilise des migrations (Alembic ou équivalent), appliquez-les :

```bash
alembic upgrade head
```

> Adaptez cette étape si les tables sont créées automatiquement au démarrage
> de l'application plutôt que via un outil de migration.

---

## Lancer le backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est alors disponible sur `http://localhost:8000`, et la documentation
interactive (Swagger) sur `http://localhost:8000/docs`.

---

## Structure du projet

```
backend/
├── app/
│   ├── main.py                     # Point d'entrée FastAPI
│   ├── routes_ml.py                # Endpoints exposant le modèle ML comme outils
│   └── services/
│       └── llm_onthology_service.py
├── ml/
│   └── src/
│       ├── extract_prompt.py
│       ├── generate_synthetic_profiles.py   # Génération du jeu de données synthétique
│       ├── inspect_model.py                 # Diagnostic du modèle .pkl avant intégration
│       ├── model_service.py                 # Chargement et inférence du modèle
│       └── modele/
│           └── random_forest.pkl
├── chroma_db/                      # Index vectoriel persistant (RAG)
├── .env                            # Configuration locale (non versionné)
├── .gitignore
└── requirements.txt
```

> Ajustez cette arborescence pour qu'elle reflète exactement l'organisation
> réelle du dépôt.

---

## Modèle Machine Learning

Le modèle (RandomForestClassifier) prédit un score d'adéquation par parcours
à partir du profil du candidat (matières préférées, compétences, centres
d'intérêt, environnement de travail souhaité, moyenne scolaire).

Avant toute intégration ou mise à jour du modèle, exécuter le diagnostic :

```bash
python ml/src/inspect_model.py ml/src/modele/random_forest.pkl
```

Il vérifie que le `.pkl` embarque bien `feature_names_in_` et `classes_`,
nécessaires pour reconstruire correctement le vecteur de features côté
backend sans dépendre d'un artefact séparé.

Outils exposés à l'agent (`app/routes_ml.py`) :

- `analyser_profil` — évalue la complétude du profil recueilli
- `calculer_adequation` — score d'adéquation pour chaque parcours
- `classer_parcours` — classement top-k des parcours les plus adaptés
- `identifier_points_forts` — croise le profil avec les features les plus
  déterminantes du modèle

---

## Jeu de données synthétique

Le jeu d'entraînement synthétique est généré par :

```bash
python ml/src/generate_synthetic_profiles.py
```

Voir `methodologie_generation.md` pour le détail de la méthode, des
hypothèses, des biais introduits et des contrôles de cohérence appliqués.
Rappel : ce jeu sert uniquement à l'**entraînement** ; la validation/le test
du modèle se font sur les réponses de l'enquête réelle (voir
`questionnaire_enquete.md`).

---

## Dépannage

**`'utf-8' codec can't decode byte 0xe9 ...` au démarrage** — vient
généralement d'un message serveur PostgreSQL en français mal décodé, ou d'un
échec d'authentification masqué. Voir la section `lc_messages` de
`postgresql.conf`, et vérifier le mot de passe avec `psql` en direct.

**`password authentication failed for user "postgres"`** — le mot de passe
dans `DATABASE_URL` ne correspond pas à celui configuré côté PostgreSQL.
Réinitialiser via `ALTER USER postgres WITH PASSWORD '...';` en psql.

**`InconsistentVersionWarning` au chargement du `.pkl`** — la version de
scikit-learn utilisée pour l'entraînement diffère de celle installée
localement. Non bloquant en général, mais réentraîner avec la même version
en cas de résultats incohérents.

---

## Équipe

*(à compléter — noms et contributions de chaque membre, comme demandé dans
les livrables du sujet)*
