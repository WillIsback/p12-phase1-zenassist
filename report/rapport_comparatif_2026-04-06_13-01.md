# Rapport comparatif — LLM vs Machine Learning

> Généré automatiquement le 2026-04-06 13:01

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
| Modèle | `Intel/Qwen3.5-122B-A10B-int4-AutoRound` |
| Infrastructure | NVIDIA DGX Spark (vLLM) |
| Endpoint | `<ENDPOINT_LLM>/v1` |
| Temperature | 0 |
| Max tokens | 24 |
| Workers parallèles | 2 (benchmark:pp2048_optimal_c2) |
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
| **Accuracy** | 0.8200 | 0.8281 |
| **F1 macro** | 0.6617 | 0.6854 |
| **F1 weighted** | 0.8224 | — |
| **Couverture** | 100.0 % | 100 % |
| **Gap train/test (F1)** | N/A (zero-shot) | 0.0342 |

### Latence et débit

| Métrique | LLM | ML |
|---|---|---|
| **Latence moyenne** | 2114 ms | 0.2235 ms |
| **Latence P95** | 2638 ms | 0.2448 ms |
| **Temps total inférence** | 1057.6 s (1000 tickets) | 18.42 s (entraînement) |
| **Débit** | 0.9 tickets/s | ~4475 tickets/s |

### Coût et scalabilité

| Critère | LLM | ML |
|---|---|---|
| **Entraînement requis** | Non (zero-shot) | Oui (18.42 s) |
| **Projection dataset complet** | ~112:40:49 | < 1 s |
| **Matériel requis** | GPU (DGX Spark) | CPU seul |
| **Ajout de classes** | Modifier le prompt | Ré-entraîner le modèle |

---

## 4. Tableau comparatif ML (tous les modèles)

| model                          |   accuracy_train |   accuracy_test |   f1_macro_train |   f1_macro_test |   f1_macro_gap |   train_time_s |   batch_pred_time_s |   latency_mean_ms |   latency_p95_ms |   selection_score |
|:-------------------------------|-----------------:|----------------:|-----------------:|----------------:|---------------:|---------------:|--------------------:|------------------:|-----------------:|------------------:|
| SGDClassifier(early_stopping)  |           0.8315 |          0.8281 |           0.7197 |          0.6854 |         0.0342 |        18.4171 |              0.0737 |            0.2235 |           0.2448 |            0.6683 |
| LinearSVC(C=0.01,cw=balanced)  |           0.8299 |          0.8238 |           0.7214 |          0.6743 |         0.0470 |        73.4050 |              0.0745 |            0.0556 |           0.0642 |            0.6508 |
| ComplementNB                   |           0.7946 |          0.7949 |           0.5424 |          0.5404 |         0.0021 |         0.3208 |              0.0723 |            0.2188 |           0.2316 |            0.5393 |
| DummyClassifier(most_frequent) |           0.3232 |          0.3232 |           0.0444 |          0.0444 |         0.0000 |         0.0076 |              0.0001 |            0.0171 |           0.0248 |            0.0444 |

---

## 5. Synthèse

| Critère | Avantage |
|---|---|
| Précision (F1 macro) | ML ✓ |
| Latence | ML ✓ (×9462 plus rapide) |
| Coût infra | ML ✓ (CPU vs GPU) |
| Flexibilité (nouvelles classes) | LLM ✓ (zero-shot) |
| Données labellisées requises | LLM ✓ (aucune) |
