# Evaluating Models

How do you know if a model is any good? "It got 95 percent right" sounds impressive, until you learn that 95 percent of the examples belonged to one class. Choosing the right evaluation method is as important as choosing the right algorithm. This chapter covers validation strategies, the metrics used for classification and regression, and the bias-variance trade-off.

## Why Training Accuracy Lies

A model evaluated on the same data it was trained on can simply memorise the answers. A decision tree grown without limits often reaches 100 percent training accuracy and then does poorly on new data. **Always evaluate on data the model did not see during training.**

## Validation Strategies

### Hold-Out Validation

Split the data once into training, validation and test sets (Chapter 2). It is simple and fast, but with small datasets the score depends heavily on which examples happen to land in which split.

### K-Fold Cross-Validation

In **k-fold cross-validation**, the training data is split into k equal parts (folds), commonly 5 or 10.

1. Train on k - 1 folds and validate on the remaining fold.
2. Repeat k times, so each fold is the validation fold once.
3. Average the k scores.

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")
print(scores.mean(), scores.std())
```

Cross-validation uses data efficiently and shows how stable the score is. Its cost is training the model k times.

Variants:

- **Stratified k-fold** keeps class proportions equal in every fold. It is the default for classification.
- **Leave-one-out** uses k = number of examples. Thorough but very slow.
- **Time-series split** always trains on earlier data and validates on later data.

> **Key idea:** Use cross-validation to choose models and hyperparameters. Use the test set exactly once, at the end, to report final performance.

## The Confusion Matrix

For a binary classifier, every prediction falls into one of four boxes.

| | Predicted positive | Predicted negative |
|---|---|---|
| **Actually positive** | True positive (TP) | False negative (FN) |
| **Actually negative** | False positive (FP) | True negative (TN) |

Consider a disease test on 1,000 people, 50 of whom are sick. The model flags 60 people; 40 of them are truly sick.

- TP = 40 (sick and flagged)
- FN = 10 (sick but missed)
- FP = 20 (healthy but flagged)
- TN = 930 (healthy and not flagged)

A **false positive** is a false alarm (Type I error). A **false negative** is a miss (Type II error). Which is worse depends on the problem.

## Classification Metrics

### Accuracy

```
accuracy = (TP + TN) / total = (40 + 930) / 1000 = 97%
```

Accuracy is misleading for imbalanced data. A model that says "healthy" for everyone scores 95 percent here while finding no sick patients at all.

### Precision

Of everything the model flagged as positive, how much was really positive?

```
precision = TP / (TP + FP) = 40 / 60 = 0.67
```

High precision means few false alarms. It matters when false positives are costly, such as marking genuine emails as spam.

### Recall (Sensitivity)

Of all the real positives, how many did the model find?

```
recall = TP / (TP + FN) = 40 / 50 = 0.80
```

High recall means few misses. It matters when false negatives are costly, such as missing a disease or a fraudulent transaction.

### The Precision-Recall Trade-off

Lowering the classification threshold flags more examples: recall rises but precision usually falls. Raising the threshold does the opposite. You cannot usually maximise both, so decide which mistake is more expensive.

### F1 Score

The **F1 score** is the harmonic mean of precision and recall:

```
F1 = 2 * precision * recall / (precision + recall) = 2 * 0.67 * 0.80 / 1.47 = 0.73
```

The harmonic mean is low if *either* value is low, so F1 rewards balanced models. It is a good single number for imbalanced problems.

### Specificity

```
specificity = TN / (TN + FP) = 930 / 950 = 0.98
```

Specificity is the recall of the negative class: how many healthy people were correctly cleared.

## ROC Curves and AUC

A **ROC curve** plots the **true positive rate** (recall) against the **false positive rate** (FP / (FP + TN)) for every possible threshold.

- A perfect model reaches the top-left corner: 100 percent recall with no false positives.
- A random guesser follows the diagonal line.

The **area under the curve (AUC)** summarises the whole curve in one number between 0.5 (random) and 1.0 (perfect). AUC has a neat interpretation: it is the probability that the model gives a randomly chosen positive a higher score than a randomly chosen negative.

For heavily imbalanced data, the **precision-recall curve** and its area are often more informative than ROC, because ROC can look good even when precision is poor.

## Metrics for Multi-Class Problems

Precision, recall and F1 are computed per class and then averaged.

- **Macro average:** the plain average across classes. Every class counts equally, so rare classes matter.
- **Weighted average:** weights each class by how many examples it has.
- **Micro average:** pools all TP, FP and FN counts first.

A multi-class confusion matrix shows which classes are confused with which, such as a digit model mixing up 4 and 9.

## Regression Metrics Revisited

| Metric | Good for |
|---|---|
| MAE | Easy explanation; robust to outliers |
| RMSE | Penalising large errors |
| R^{2} | Comparing against the "predict the mean" baseline |
| MAPE | Errors as percentages, when the target is never near zero |

## The Bias-Variance Trade-off

A model's error on new data comes from three sources.

- **Bias:** error from wrong assumptions. A straight line fitted to a curve has high bias. High bias causes **underfitting**.
- **Variance:** error from being too sensitive to the particular training set. A very deep tree changes wildly if a few examples change. High variance causes **overfitting**.
- **Irreducible noise:** randomness in the data that no model can remove.

Simple models tend to have high bias and low variance; complex models have low bias and high variance. The best model balances the two.

> **Key idea:** Diagnose with training and validation scores. Both low: high bias, so use a more powerful model or better features. Training high but validation low: high variance, so get more data, simplify or regularize.

### Learning Curves

A **learning curve** plots training and validation scores against training-set size.

- If both curves are low and close together, more data will not help much; the model is too simple.
- If there is a big gap between them that narrows as data grows, more data will help.

## Hyperparameter Tuning

Hyperparameters, such as tree depth or regularization strength, are chosen using validation scores.

- **Grid search** tries every combination from a list of values.
- **Random search** tries random combinations. It is often more efficient when only a few hyperparameters really matter.
- **Bayesian optimisation** uses past results to pick promising values next.

```python
from sklearn.model_selection import GridSearchCV

grid = GridSearchCV(model, {"logisticregression__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="f1")
grid.fit(X_train, y_train)
print(grid.best_params_, grid.best_score_)
```

## Summary

- Never judge a model on its training data; use hold-out sets or k-fold cross-validation.
- The confusion matrix counts TP, FP, FN and TN.
- Accuracy misleads on imbalanced data; use precision, recall, F1 and specificity.
- ROC-AUC measures ranking quality across thresholds; precision-recall curves suit rare positives.
- Bias causes underfitting and variance causes overfitting; learning curves help diagnose which.
- Tune hyperparameters on validation data with grid, random or Bayesian search.

## Practice Questions

1. A fraud model has 99.5 percent accuracy on data where 0.5 percent of transactions are fraud. Why might it still be useless?
2. From TP = 30, FP = 10, FN = 20, TN = 940, compute precision, recall and F1.
3. For a cancer screening test, would you prioritise precision or recall? Why?
4. Explain 5-fold cross-validation step by step.
5. Training accuracy is 99 percent and validation accuracy is 70 percent. Name three things you could try.
