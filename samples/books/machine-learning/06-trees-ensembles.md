# Decision Trees and Ensembles

Decision trees make predictions the way people often make decisions: by asking a sequence of simple questions. They are easy to understand and work with messy, mixed data. On their own they tend to overfit, but combined into **ensembles** such as random forests and gradient boosting, they become some of the most accurate models for tabular data.

## How a Decision Tree Works

Imagine deciding whether a bank should approve a loan.

```
Is income > 50,000?
 |-- No  -> Is there a guarantor?
 |           |-- No  -> Reject
 |           |-- Yes -> Approve
 |-- Yes -> Credit score > 700?
             |-- No  -> Reject
             |-- Yes -> Approve
```

A decision tree has:

- a **root node**: the first question,
- **internal nodes**: further questions, each testing one feature,
- **branches**: the answers,
- **leaf nodes**: the final predictions.

To classify a new applicant, start at the root and follow the answers down to a leaf. For regression trees, a leaf predicts a number, usually the average target value of the training examples that reached it.

## Learning a Tree

The algorithm builds the tree greedily from the top down:

1. Consider every feature and every possible split point.
2. Choose the split that best separates the classes, making the child nodes as **pure** as possible.
3. Repeat recursively for each child.
4. Stop when a node is pure, too small, or a depth limit is reached.

"Pure" means a node contains examples of only one class. We need a way to measure impurity.

### Gini Impurity

```
Gini = 1 - sum over classes of (p_k)^2
```

where p_k is the fraction of examples in the node belonging to class k.

- A pure node (all one class) has Gini = 0.
- A 50/50 node in a binary problem has Gini = 1 - (0.25 + 0.25) = 0.5, the worst case.

### Entropy and Information Gain

```
Entropy = - sum over classes of p_k * log2(p_k)
```

Entropy is 0 for a pure node and 1 for a 50/50 binary node. **Information gain** is the drop in entropy achieved by a split: the entropy of the parent minus the weighted average entropy of the children. The algorithm picks the split with the highest gain.

In practice Gini and entropy give very similar trees. Gini is slightly faster to compute and is the default in scikit-learn.

### A Tiny Worked Example

A node contains 10 loan applications: 6 approved and 4 rejected. Its Gini is 1 - (0.6^{2} + 0.4^{2}) = 1 - 0.52 = 0.48. Splitting on "income > 50,000" gives a left child with 4 rejected and 1 approved and a right child with 5 approved. The right child is pure (Gini 0). The left child has Gini 1 - (0.8^{2} + 0.2^{2}) = 0.32. The weighted impurity is 0.5 x 0.32 + 0.5 x 0 = 0.16, down from 0.48, which makes this a good split.

### Splitting Regression Trees

For regression, the tree chooses splits that minimise the **variance** (or MSE) of the target inside each child.

## Overfitting and Pruning

A tree allowed to grow without limits keeps splitting until every leaf is pure. It will often end up with one leaf per training example, perfectly memorising the data, noise included.

Ways to control this:

- **Pre-pruning** (early stopping): limit `max_depth`, require `min_samples_split` or `min_samples_leaf`, or cap the number of leaves.
- **Post-pruning:** grow a full tree, then remove branches that do not improve validation performance. **Cost-complexity pruning** (`ccp_alpha` in scikit-learn) does this systematically.

```python
from sklearn.tree import DecisionTreeClassifier, export_text

tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=0)
tree.fit(X_train, y_train)
print(export_text(tree, feature_names=list(X_train.columns)))
```

## Strengths and Weaknesses of Trees

Strengths:

- Easy to visualise and explain.
- Handle numerical and categorical features, and need no feature scaling.
- Capture non-linear relationships and feature interactions automatically.

Weaknesses:

- Overfit easily.
- **Unstable:** a small change in the data can produce a completely different tree.
- Make boxy, step-shaped predictions.

## Ensemble Learning

An **ensemble** combines many models to get a better one. The idea is the "wisdom of crowds": if many reasonably good models make *different* mistakes, their combined vote is more accurate than any one of them.

> **Key idea:** Ensembles work best when the individual models are diverse. Averaging many copies of the same model achieves nothing.

### Bagging

**Bagging** (bootstrap aggregating) trains many models on different **bootstrap samples** of the training data: random samples of the same size drawn *with replacement*, so some examples appear twice and others not at all. Predictions are combined by majority vote (classification) or averaging (regression).

Bagging mainly **reduces variance**, which makes it ideal for unstable, high-variance models like deep trees.

### Random Forests

A **random forest** is bagging with decision trees plus one extra twist: at each split, a tree may only consider a **random subset of the features**. This stops every tree from splitting on the same strong feature at the top, making the trees more diverse.

```python
from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(n_estimators=300, max_features="sqrt", n_jobs=-1, random_state=0)
forest.fit(X_train, y_train)
print(forest.score(X_test, y_test))
```

Useful facts:

- More trees rarely hurt; they just cost time.
- **Out-of-bag (OOB) evaluation:** each tree never saw roughly a third of the data, so those examples provide a free validation score.
- **Feature importance:** forests report how much each feature reduced impurity across all trees. It is a helpful, though imperfect, guide to what the model relies on.

Random forests are an excellent default: accurate, robust and hard to break.

### Boosting

**Boosting** builds models **sequentially**, with each new model focusing on the mistakes of the ones before it. It mainly **reduces bias**, turning many weak learners (often shallow trees) into a strong one.

- **AdaBoost** increases the weight of misclassified examples so the next model pays more attention to them. The final prediction is a weighted vote.
- **Gradient boosting** fits each new tree to the **residual errors** (more precisely, the gradient of the loss) of the current ensemble, and adds it with a small **learning rate**.

```
prediction = tree1 + lr * tree2 + lr * tree3 + ...
```

Popular, highly optimised implementations include **XGBoost**, **LightGBM** and **CatBoost**. They dominate machine learning competitions on tabular data.

Key hyperparameters for gradient boosting:

- `n_estimators`: number of trees.
- `learning_rate`: how much each tree contributes. Smaller values need more trees but generalise better.
- `max_depth`: depth of each tree, usually small (3 to 8).
- `subsample`: fraction of rows used per tree, which adds randomness and reduces overfitting.

Boosting can overfit if it runs too long, so use **early stopping** on a validation set.

### Stacking

**Stacking** trains several different models (say a random forest, logistic regression and gradient boosting), then trains a final **meta-model** on their predictions to learn how best to combine them.

## Comparing the Approaches

| Method | Trains models | Mainly reduces | Typical base model |
|---|---|---|---|
| Bagging / random forest | In parallel, independently | Variance | Deep trees |
| Boosting | Sequentially, fixing errors | Bias | Shallow trees |
| Stacking | Different model types | Both | Anything |

## Summary

- Decision trees split data with simple feature tests, choosing splits that reduce Gini impurity or entropy.
- Unrestricted trees overfit; control depth and leaf size or prune them.
- Ensembles combine diverse models to beat any single one.
- Bagging and random forests average many trees trained on bootstrap samples, reducing variance.
- Boosting adds trees one at a time to fix earlier errors, reducing bias; tune the learning rate and use early stopping.
- For tabular data, random forests and gradient boosting are strong first choices.

## Practice Questions

1. Compute the Gini impurity of a node containing 8 examples of class A and 2 of class B.
2. Why does an unpruned decision tree overfit?
3. What extra randomness does a random forest add compared with plain bagging, and why does it help?
4. Explain the difference between bagging and boosting in terms of bias and variance.
5. What does a small learning rate do in gradient boosting?
