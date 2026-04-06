# Rapport d'évaluation des System Prompts

> **Date :** 2026-04-06 12:57:50
> **Modèle :** `Intel/Qwen3.5-122B-A10B-int4-AutoRound`
> **Endpoint :** `<ENDPOINT_LLM>/v1`
> **Échantillon :** 100 tickets (stratifié, 11 classes)
> **guided_choice :** désactivé (évaluation du prompt pur)

---

## 1. Configuration de l'évaluation

| Paramètre | Valeur |
|---|---|
| `PROMPT_EVAL_SAMPLE_SIZE` | 100 |
| Nombre de variantes | 5 |
| Total inférences | 500 |
| `use_guided_choice` | `False` |
| `temperature` | 0.7 |
| `top_p` | 0.8 |
| `max_tokens` | 30 |
| `LLM_MAX_WORKERS` | 2 |
| `LLM_MAX_RETRIES` | 2 |

---

## 2. Détail par variante (classées par F1 macro décroissant)

### v5_expert_persona

**System Prompt :**

```
You are a senior financial compliance analyst at the CFPB (Consumer Financial Protection Bureau) with 15 years of experience categorizing consumer complaints. You are precise, consistent, and always assign complaints to the most specific applicable category. Your task: read the consumer complaint and assign it to exactly ONE category from the provided list. Reply with ONLY the category label — no commentary, no punctuation, no extra text.
```

**User message format :** categories + descriptions + few-shot examples

| Métrique | Valeur |
|---|---|
| Accuracy | 0.8000 |
| F1 macro | 0.5689 |
| F1 weighted | 0.7973 |
| Couverture | 100.0% |
| Prédictions valides | 100 / 100 |
| Temps d'inférence | 107.9s |

---

### v1_baseline

**System Prompt :**

```
You are an expert classifier for consumer financial complaint tickets. Your task is to assign each ticket to exactly ONE category from the provided list. Read the ticket carefully and reply with ONLY the category label — no explanation, no punctuation, no extra text.
```

**User message format :** categories + descriptions + few-shot examples

| Métrique | Valeur |
|---|---|
| Accuracy | 0.7800 |
| F1 macro | 0.5547 |
| F1 weighted | 0.7814 |
| Couverture | 100.0% |
| Prédictions valides | 100 / 100 |
| Temps d'inférence | 105.8s |

---

### v3_structured_json

**System Prompt :**

```
You are a text classifier for consumer financial complaints. Respond with ONLY a valid JSON object containing one key 'label' with the category name as value. No explanation, no extra text.
```

**User message format :** categories + descriptions

| Métrique | Valeur |
|---|---|
| Accuracy | 0.7600 |
| F1 macro | 0.5495 |
| F1 weighted | 0.7585 |
| Couverture | 100.0% |
| Prédictions valides | 100 / 100 |
| Temps d'inférence | 63.4s |

---

### v4_cot_brief

**System Prompt :**

```
You are an expert classifier for consumer financial complaints. First, identify the main financial product or service mentioned in the complaint. Then classify the complaint into exactly one category from the provided list. Reply with ONLY the category label on the last line.
```

**User message format :** categories + descriptions

| Métrique | Valeur |
|---|---|
| Accuracy | 0.7600 |
| F1 macro | 0.5429 |
| F1 weighted | 0.7554 |
| Couverture | 100.0% |
| Prédictions valides | 100 / 100 |
| Temps d'inférence | 45.8s |

---

### v2_minimal

**System Prompt :**

```
Classify the following consumer complaint into one category. Reply with ONLY the category label.
```

**User message format :** categories only (labels list)

| Métrique | Valeur |
|---|---|
| Accuracy | 0.7400 |
| F1 macro | 0.5092 |
| F1 weighted | 0.7375 |
| Couverture | 100.0% |
| Prédictions valides | 100 / 100 |
| Temps d'inférence | 34.3s |

---

## 3. Tableau comparatif

|                    |   accuracy |   f1_macro |   f1_weighted |   coverage |   time_s |   n_valid |
|:-------------------|-----------:|-----------:|--------------:|-----------:|---------:|----------:|
| v5_expert_persona  |       0.8  |     0.5689 |        0.7973 |          1 | 107.913  |       100 |
| v1_baseline        |       0.78 |     0.5547 |        0.7814 |          1 | 105.817  |       100 |
| v3_structured_json |       0.76 |     0.5495 |        0.7585 |          1 |  63.3682 |       100 |
| v4_cot_brief       |       0.76 |     0.5429 |        0.7554 |          1 |  45.8363 |       100 |
| v2_minimal         |       0.74 |     0.5092 |        0.7375 |          1 |  34.3369 |       100 |

---

## 4. Recommandation

**Meilleur prompt : `v5_expert_persona`** avec un F1 macro de **0.5689**

| Stratégie | Description |
|---|---|
| `v1_baseline` | Rôle + tâche directe + few-shot + descriptions |
| `v2_minimal` | Zero-shot minimal, labels uniquement |
| `v3_structured_json` | Sortie JSON structurée + descriptions |
| `v4_cot_brief` | Chain-of-thought court + descriptions |
| `v5_expert_persona` | Persona expert CFPB + few-shot + descriptions |

---

## 5. Traçabilité Weave

Chaque variante est loggée dans Weave avec :

- Un `weave.Dataset` dédié (`prompt-eval-<variant>`)
- Un `EvaluationLogger` par variante avec scores `exact_match` et `valid_prediction`
- Les métriques agrégées (accuracy, f1_macro, f1_weighted, coverage, time_s)

Pour consulter les résultats détaillés -> onglet **Evaluations** du projet Weave.
