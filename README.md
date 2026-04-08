# P12 — Classification automatique de tickets consommateurs

Projet n°12 du parcours IA — OpenClassrooms.

## Contexte

**ZenAssist** est une plateforme de suivi de réclamations qui centralise la gestion des tickets de support pour plus de 200 entreprises. L'objectif est d'automatiser l'étiquetage des réclamations consommateurs (Consumer Financial Protection Bureau) afin de les router vers le bon service.

Ce notebook compare trois approches de classification en 11 catégories :

| Approche | Description |
|---|---|
| **LLM zero-shot** | Qwen3.5-122B via vLLM (ou Mistral AI) — aucun entraînement requis |
| **ML classique** | TF-IDF + classifieurs scikit-learn (LinearSVC, SGDClassifier, ComplementNB) |
| **ModernBERT fine-tuné** | [modernbert-large-consumer-finance-11cls](https://huggingface.co/WillisBack/modernbert-large-consumer-finance-11cls) — 395M paramètres |

## Résultats clés (1 000 tickets d'évaluation)

| Métrique | LLM (Qwen3.5) | ML (SGDClassifier) | ModernBERT |
|---|---|---|---|
| Accuracy | 0.820 | **0.828** | 0.787 |
| F1 macro | 0.662 | **0.685** | 0.636 |
| F1 weighted | **0.822** | 0.685 | 0.794 |
| Latence moyenne | ~2 100 ms | < 1 ms | ~1 600 ms |

## Structure du dépôt

```text
├── p12.ipynb                  # Notebook principal (exploration → évaluation → rapport)
├── pyproject.toml             # Dépendances Python (uv)
├── projet12_phase1_zenassist.pptx  # Présentation des résultats
├── docs/
│   └── prompt_eval_report_*.md    # Rapport d'évaluation des system prompts
├── report/
│   └── rapport_comparatif_*.md    # Rapports comparatifs LLM vs ML vs BERT
├── .env.example               # Variables d'environnement (template)
└── .gitignore
```

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)
- GPU optionnel pour ModernBERT et/ou vLLM local

## Installation

```bash
git clone https://github.com/WillIsback/p12-phase1-zenassist.git
cd p12-phase1-zenassist
uv sync
```

## Configuration

Créez un fichier `.env` à la racine :

```env
# Endpoint LLM (OpenAI-compatible)
# Option 1 — vLLM local :
VLLM_BASE_URL=http://localhost:8000
# Option 2 — Mistral AI :
# VLLM_BASE_URL=https://api.mistral.ai
# MISTRAL_API_KEY=votre_clé

# Weave / Weights & Biases (optionnel — le notebook fonctionne sans)
# WANDB_API_KEY=votre_clé
```

Le notebook détecte automatiquement le modèle exposé sur l'endpoint.
Sans `WANDB_API_KEY`, le suivi Weave est désactivé (les métriques restent calculées localement).

## Dataset

Le dataset CFPB (Consumer Financial Protection Bureau) n'est pas inclus dans le dépôt.
Placez `dataset.csv` dans le dossier `data/` avant d'exécuter le notebook.

## Livrables

- **Notebook** : exploration des données, implémentation LLM / ML / ModernBERT, rapport comparatif
- **Script d'export ML** : `main.py` — entraîne les modèles scikit-learn, sélectionne le meilleur et exporte les artefacts de release
- **Présentation** : `projet12_phase1_zenassist.pptx` — slides de recommandation client
- **Rapports** : analyse détaillée dans `docs/` et `report/`

## Export du modèle ML

Le dépôt contient un script versionné qui entraîne les classifieurs ML, sélectionne le meilleur modèle et exporte les artefacts de release au format pickle et JSON.

Exécution locale :

```bash
python main.py \
  --dataset data/dataset.csv \
  --output-dir output \
  --version local-test
```

Artefacts générés :

- `output/best_ml_classifier.pkl` : classifieur sélectionné + TF-IDF vectorizer + LabelEncoder
- `output/best_ml_metrics.json` : métriques, ranking des modèles et métadonnées du dataset

## Release GitHub Actions

Le workflow `.github/workflows/release-model.yml` permet de versionner les artefacts de modèle avec le code source.

Fonctionnement :

- déclenchement manuel via `workflow_dispatch` pour le debug
- déclenchement automatique lors de la publication d'une release GitHub
- exécution du script d'export
- ajout du pickle et du JSON comme assets de release

Pré-requis CI :

- le workflow télécharge automatiquement le dataset public CFPB depuis OpenClassrooms
- si le dataset ne peut pas être téléchargé, remplacer `ubuntu-latest` par un runner `self-hosted` ayant accès au CSV

## Auteur

William Derue — [OpenClassrooms](https://openclassrooms.com/) parcours IA, projet 12
