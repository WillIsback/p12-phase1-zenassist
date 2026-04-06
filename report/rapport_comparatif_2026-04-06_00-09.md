# Rapport comparatif — LLM vs Machine Learning

> Généré automatiquement le 2026-04-06 00:09

---

## 1. Données d'entraînement / évaluation

| | LLM (zero-shot) | ML (supervisé) |
|---|---|---|
| **Source** | `dataset.csv` | `dataset.csv` |
| **Lignes exploitables** | 383,564 | 383,564 |
| **Nombre de classes** | 11 | 11 |
| **Échantillon évalué** | 1,000 (stratifié) | 76,713 (test 20 %) |
| **Split** | Aucun (zero-shot) | 80 / 20 stratifié |
| **Pré-traitement texte** | Prompt + troncature 3 000 car. | TF-IDF (max_features=30,000, ngram 1-2) |

---

## 2. Configuration des modèles

### LLM
| Paramètre | Valeur |
|---|---|
| Modèle | `cyankiwi/gemma-4-31B-it-AWQ-4bit` |
| Infrastructure | NVIDIA DGX Spark (vLLM) |
| Endpoint | `<ENDPOINT_LLM>/v1` |
| Temperature | 0 |
| Max tokens | 24 |
| Workers parallèles | 32 (endpoint:max_num_seqs) |
| Retries | 2 (guided_choice → free-form) |

### ML — Meilleur modèle : `SGDClassifier(early_stopping)`
| Paramètre | Valeur |
|---|---|
| Vectorisation | TF-IDF (vocab 30,000, densité 0.6357%) |
| Tuning LinearSVC | CV interne 3 folds, grille 8 configs |
| Meilleur C | 0.01 |
| class_weight | balanced |
| Modèles comparés | DummyClassifier(most_frequent), ComplementNB, SGDClassifier(early_stopping), LinearSVC(C=0.01,cw=balanced) |

---

## 3. Résultats et performance

### Métriques de classification

| Métrique | LLM | ML (`SGDClassifier(early_stopping)`) |
|---|---|---|
| **Accuracy** | 0.7730 | 0.8281 |
| **F1 macro** | 0.6278 | 0.6854 |
| **F1 weighted** | 0.7769 | — |
| **Couverture** | 100.0 % | 100 % |
| **Gap train/test (F1)** | N/A (zero-shot) | 0.0342 |

### Latence et débit

| Métrique | LLM | ML |
|---|---|---|
| **Latence moyenne** | 11073 ms | 0.2235 ms |
| **Latence P95** | 13047 ms | 0.2392 ms |
| **Temps total inférence** | 352.9 s (1000 tickets) | 17.59 s (entraînement) |
| **Débit** | 2.8 tickets/s | ~4474 tickets/s |

### Coût et scalabilité

| Critère | LLM | ML |
|---|---|---|
| **Entraînement requis** | Non (zero-shot) | Oui (17.59 s) |
| **Projection dataset complet** | ~125:41:34 | < 1 s |
| **Matériel requis** | GPU (DGX Spark) | CPU seul |
| **Ajout de classes** | Modifier le prompt | Ré-entraîner le modèle |

---

## 4. Tableau comparatif ML (tous les modèles)

| model                          |   accuracy_train |   accuracy_test |   f1_macro_train |   f1_macro_test |   f1_macro_gap |   train_time_s |   batch_pred_time_s |   latency_mean_ms |   latency_p95_ms |   selection_score |
|:-------------------------------|-----------------:|----------------:|-----------------:|----------------:|---------------:|---------------:|--------------------:|------------------:|-----------------:|------------------:|
| SGDClassifier(early_stopping)  |           0.8315 |          0.8281 |           0.7197 |          0.6854 |         0.0342 |        17.5853 |              0.0757 |            0.2235 |           0.2392 |            0.6683 |
| LinearSVC(C=0.01,cw=balanced)  |           0.8299 |          0.8238 |           0.7214 |          0.6743 |         0.0470 |        74.3662 |              0.0723 |            0.0541 |           0.0622 |            0.6508 |
| ComplementNB                   |           0.7946 |          0.7949 |           0.5424 |          0.5404 |         0.0021 |         0.3055 |              0.0736 |            0.2194 |           0.2414 |            0.5393 |
| DummyClassifier(most_frequent) |           0.3232 |          0.3232 |           0.0444 |          0.0444 |         0.0000 |         0.0083 |              0.0001 |            0.0163 |           0.0229 |            0.0444 |

---

## 5. Synthèse

| Critère | Avantage |
|---|---|
| Précision (F1 macro) | ML ✓ |
| Latence | ML ✓ (×49537 plus rapide) |
| Coût infra | ML ✓ (CPU vs GPU) |
| Flexibilité (nouvelles classes) | LLM ✓ (zero-shot) |
| Données labellisées requises | LLM ✓ (aucune) |
