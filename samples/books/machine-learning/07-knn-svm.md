# Nearest Neighbours and Support Vector Machines

This chapter covers two classic algorithms with very different personalities. **k-nearest neighbours** is almost laughably simple: to classify something, look at the most similar examples you have already seen. **Support vector machines** are mathematically elegant: they find the widest possible "street" separating two classes. Both rely on the idea of distance or geometry in feature space, so both care a lot about feature scaling.

## Feature Space

Think of every example as a point in space, with one axis per feature. A student described by hours studied and hours slept is a point in 2-D space; a house with ten features is a point in 10-D space. Similar examples are points that lie close together. Classification then becomes a question of geometry: which region of the space does a new point fall into?

## k-Nearest Neighbours (kNN)

### The Algorithm

To classify a new point:

1. Compute its distance to every training example.
2. Pick the **k** closest examples, its "neighbours".
3. **Classification:** predict the most common class among the neighbours.
4. **Regression:** predict the average of the neighbours' target values.

That is the whole algorithm. There is no real training step; the model simply stores the data. kNN is therefore called a **lazy learner** or an **instance-based** method.

### Measuring Distance

The most common choice is **Euclidean distance**, the straight-line distance:

```
d(a, b) = sqrt( (a1 - b1)^2 + (a2 - b2)^2 + ... + (an - bn)^2 )
```

Other options:

- **Manhattan distance:** the sum of absolute differences, like walking city blocks: |a1 - b1| + |a2 - b2| + ...
- **Cosine similarity:** compares the *direction* of two vectors rather than their size. It is popular for text, where documents of different lengths should still match if they use words in similar proportions.

> **Key idea:** kNN is only as good as its distance measure. If one feature ranges from 0 to 100,000 (income) and another from 0 to 5 (rating), income completely dominates the distance. Always scale features before using kNN.

### Choosing k

- **Small k** (such as 1): the model follows every quirk of the training data. It has low bias and high variance and is sensitive to noise.
- **Large k:** predictions become smoother, but eventually the model ignores local structure. High bias, low variance.

Choose k with cross-validation. For binary classification, an odd k avoids ties. A useful refinement is **distance-weighted voting**, in which nearer neighbours count more than distant ones.

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

knn = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=7, weights="distance"))
knn.fit(X_train, y_train)
```

### Strengths and Weaknesses of kNN

Strengths:

- Very simple to understand and implement.
- Makes no assumptions about the shape of the decision boundary.
- New data can be added instantly without retraining.

Weaknesses:

- **Slow predictions:** every prediction compares against all training points. Data structures such as KD-trees and ball trees, or approximate nearest-neighbour search, help.
- Needs lots of memory to store the dataset.
- Sensitive to irrelevant features and unscaled data.
- Suffers badly from the curse of dimensionality.

### The Curse of Dimensionality

As the number of features grows, space becomes enormous and data becomes sparse. In very high dimensions, almost all points end up roughly the same distance from each other, so "nearest" loses its meaning. Distance-based methods then perform poorly unless you reduce the number of dimensions first (Chapter 8) or select relevant features.

## Support Vector Machines (SVM)

### The Maximum Margin Idea

Suppose two classes can be separated by a straight line. Usually many lines would work. Which is best?

An SVM chooses the line (in higher dimensions, a **hyperplane**) that has the **largest margin**: the greatest distance to the nearest points of either class. Picture the widest possible street between the two classes, with the decision boundary running down the middle.

The training points that lie on the edges of the street are called **support vectors**. They alone determine the boundary; moving other points (without crossing the street) changes nothing. This makes SVMs robust and memory-efficient at prediction time.

> **Key idea:** A wide margin means the classifier is not "cutting it close" to any training example, which tends to generalise better to new data.

### Soft Margins and the C Parameter

Real data is rarely perfectly separable, and outliers can force a very narrow street. A **soft-margin SVM** allows some points to fall inside the street or even on the wrong side, at a cost.

The hyperparameter **C** controls the trade-off:

- **Large C:** mistakes are expensive, so the model tries hard to classify every training point correctly. The margin is narrower and there is more risk of overfitting.
- **Small C:** mistakes are cheap, so the margin is wider and the model is simpler and more tolerant of outliers.

### The Kernel Trick

What if the classes cannot be separated by any straight line, say one class forms a ring around the other? The trick is to map the data into a higher-dimensional space where a flat separator *does* exist. Adding the feature x^{2} + y^{2}, for example, turns the ring problem into a simple threshold.

Computing such mappings explicitly can be very expensive. The **kernel trick** lets the SVM compute similarities *as if* the data had been mapped, without ever building the new features.

Common kernels:

| Kernel | Boundary shape | Notes |
|---|---|---|
| Linear | Straight line / hyperplane | Fast; good for text and many features |
| Polynomial | Curved, of a set degree | Degree is a hyperparameter |
| RBF (Gaussian) | Flexible, smooth regions | The most popular default |
| Sigmoid | Similar to a neural network | Rarely used |

The RBF kernel has a hyperparameter **gamma**. A large gamma makes each training point's influence very local, giving wiggly boundaries that can overfit. A small gamma makes boundaries smoother. Tune C and gamma together with a grid search.

```python
from sklearn.svm import SVC

svm = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale", probability=True))
svm.fit(X_train, y_train)
```

### SVMs for Regression

**Support vector regression (SVR)** flips the idea: it fits a tube of width epsilon around the data and ignores errors that fall inside the tube, penalising only points outside it.

### Strengths and Weaknesses of SVMs

Strengths:

- Effective in high-dimensional spaces, even when features outnumber examples.
- Memory-efficient, because only support vectors matter.
- Flexible through kernels.

Weaknesses:

- Training is slow on very large datasets (hundreds of thousands of rows or more).
- Sensitive to feature scaling and to the choice of C and gamma.
- Do not directly produce probabilities; extra calibration is needed.
- Harder to interpret than trees or linear models.

## kNN vs SVM at a Glance

| | kNN | SVM |
|---|---|---|
| Training cost | None (stores data) | Can be high |
| Prediction cost | High (compares with all data) | Low (support vectors only) |
| Key hyperparameters | k, distance measure | C, kernel, gamma |
| Needs scaling | Yes | Yes |
| Handles high dimensions | Poorly | Well |

## Summary

- Examples are points in feature space; similar examples lie close together.
- kNN predicts from the k closest training points. It is lazy, simple, and very sensitive to scaling and dimensionality.
- Small k overfits; large k underfits. Choose k with cross-validation.
- SVMs find the maximum-margin hyperplane, defined by the support vectors.
- C trades margin width against training errors; kernels such as RBF handle non-linear boundaries.
- Both methods need scaled features and tuned hyperparameters.

## Practice Questions

1. Compute the Euclidean and Manhattan distances between (1, 2) and (4, 6).
2. Why must features be scaled before using kNN? Give an example of what goes wrong otherwise.
3. What happens to a kNN classifier as k grows very large?
4. What are support vectors, and why are they important?
5. Explain the effect of increasing C in a soft-margin SVM.
