# Rapport comparatif : LLM vs ML vs ModernBERT

## 1. Contexte & objectifs

Ce rapport compare trois approches de classification automatique
de tickets consommateurs (Consumer Financial Protection Bureau) :

1. **LLM zero-shot** (Qwen3.5-122B via vLLM)
2. **ML classique** (TF-IDF + classifieurs scikit-learn)
3. **ModernBERT fine-tuné** (WillisBack/modernbert-large-consumer-finance-11cls)

- **Nombre de classes** : 10
- **Jeu d'évaluation commun** : 100 tickets (LLM & BERT sur même split)
- **Date** : 20260408_005322

## 2. Configuration des approches

| Critère | LLM (Qwen3.5-122B) | ML (TF-IDF + SGDClassifier(early_stopping)) | ModernBERT fine-tuné |
|---|---|---|---|
| Type | Zero-shot (pas d'entraînement) | Supervisé classique | Encoder fine-tuné |
| Paramètres | ~122B (quantisé int4) | TF-IDF 30000 features | 395M (full fine-tuning) |
| Infrastructure | NVIDIA DGX Spark (vLLM) | CPU standard | GPU (RTX 5080, 6.3h train) |
| Données d'entraînement | Aucune (zero-shot) | Train split du dataset | 293k tickets (HF dataset) |
| Max tokens / longueur | context window LLM | N/A (TF-IDF) | 1024 tokens |

## 3. Métriques de performance

| Métrique | LLM | ML (SGDClassifier(early_stopping)) | ModernBERT |
|---|---|---|---|
| **Accuracy** | 0.8000 | 0.8281 | 0.7200 |
| **F1 macro** | 0.6718 | 0.6854 | 0.5815 |
| **F1 weighted** | 0.7988 | 0.6854 | 0.7349 |
| **Coverage** | 1.0000 | 1.0000 | 1.0000 |

## 4. Latence & débit

| Métrique | LLM | ML | ModernBERT |
|---|---|---|---|
| Latence moyenne | 2039.9 ms | < 1 ms | 1519.6 ms |
| Latence P95 | 2538.2 ms | < 1 ms | 4329.4 ms |
| Débit | ~0.5 t/s | > 10 000 t/s | 0.7 t/s |

## 5. Coût & scalabilité

| Critère | LLM | ML | ModernBERT |
|---|---|---|---|
| Coût d'entraînement | Aucun | Faible (CPU, minutes) | Modéré (GPU, ~6h) |
| Coût d'inférence | Élevé (GPU serveur vLLM) | Très faible (CPU) | Modéré (GPU) |
| Scalabilité | Limitée (throughput) | Excellente | Bonne (batch GPU) |
| Maintenance | Faible (prompt eng.) | Moyenne (re-train) | Moyenne (re-train) |
| Mise en production | API simple | Léger (pickle + API) | Modéré (GPU requis) |

## 6. Synthèse comparative

| Critère | Gagnant |
|---|---|
| Meilleure accuracy | ML (SGDClassifier(early_stopping)) |
| Meilleur F1 macro | ML (SGDClassifier(early_stopping)) |
| Latence la plus basse | ML |
| Coût le plus faible | ML |
| Pas d'entraînement requis | LLM |
| Meilleur compromis qualité/coût | À discuter selon le contexte |

## 7. Recommandation

### Scénario 1 : Prototype rapide / exploration
**LLM zero-shot** — Pas d'entraînement, résultats utilisables immédiatement.
Idéal pour valider la faisabilité avant d'investir dans un modèle supervisé.

### Scénario 2 : Production à haut volume, budget limité
**ML classique (TF-IDF + SGDClassifier(early_stopping))** — Inférence quasi-instantanée,
déploiement léger, coût minimal. Performant si les données sont représentatives.

### Scénario 3 : Production avec exigence de qualité maximale
**ModernBERT fine-tuné** — Meilleur compromis entre qualité et coût d'inférence.
Nécessite un GPU mais offre un excellent F1 après fine-tuning sur le domaine.
Le coût d'entraînement initial (~6h sur GPU) est amorti sur le long terme.

### Stratégie hybride recommandée
1. **Phase pilote** : LLM zero-shot pour valider le besoin et collecter des labels
2. **Phase production** : ModernBERT fine-tuné comme modèle principal
3. **Fallback** : ML classique en secours si le GPU est indisponible

## 8. Traçabilité

| Élément | Valeur |
|---|---|
| Jeu d'évaluation | 100 tickets, 10 classes |
| LLM | Qwen3.5-122B-A10B-int4-AutoRound (vLLM) |
| ML | SGDClassifier(early_stopping) + TF-IDF (30000 features) |
| ModernBERT | WillisBack/modernbert-large-consumer-finance-11cls (395M params) |
| Rapport généré | report/rapport_comparatif_20260408_005322.md |
| Weave project | p12-ticket-classification |
