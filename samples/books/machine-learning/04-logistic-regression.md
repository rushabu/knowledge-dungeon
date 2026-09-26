# Classification and Logistic Regression

Many real questions have yes-or-no answers. Will this customer cancel? Is this email spam? Does this X-ray show pneumonia? These are **classification** problems. Despite its name, **logistic regression** is one of the most widely used classification algorithms. It is fast, interpretable and a strong baseline for almost any classification task.

## Why Not Use Linear Regression?

Suppose we label "spam" as 1 and "not spam" as 0 and fit a straight line. Two problems appear immediately.

1. The line produces values like -0.4 or 1.7, which make no sense as answers or as probabilities.
2. A few extreme examples can tilt the whole line and move the decision boundary in the wrong place.

We need a model whose output always stays between 0 and 1, so we can read it as a **probability**.

## The Sigmoid Function

The **sigmoid** (or logistic) function squashes any number into the range 0 to 1:

```
sigmoid(z) = 1 / (1 + e^(-z))
```

- When z is large and positive, sigmoid(z) is close to 1.
- When z is large and negative, sigmoid(z) is close to 0.
- When z = 0, sigmoid(z) = 0.5.

It draws a smooth S-shaped curve.

## The Logistic Regression Model

Logistic regression first computes a linear score, exactly like linear regression, and then passes it through the sigmoid:

```
z = w1*x1 + w2*x2 + ... + wn*xn + b
p = sigmoid(z)                        # probability that y = 1
```

To turn the probability into a class, we apply a **threshold**, usually 0.5:

```
predict 1 if p >= 0.5, otherwise predict 0
```

> **Key idea:** Logistic regression outputs a probability, not just a label. That lets you choose the threshold to suit the problem. A cancer screening test might flag patients at p >= 0.2, because missing a case is worse than an extra check-up.

### The Decision Boundary

Because p >= 0.5 exactly when z >= 0, the boundary between the classes is the set of points where w1*x1 + ... + b = 0. With two features that is a straight line; with more features it is a flat surface (a hyperplane). Logistic regression is therefore a **linear classifier**. Adding polynomial features lets it draw curved boundaries.

### Interpreting the Weights

The quantity z is the **log-odds**: log(p / (1 - p)). Each weight says how much the log-odds change when its feature rises by one unit. A positive weight pushes towards class 1 and a negative weight towards class 0. This interpretability makes logistic regression popular in medicine, finance and anywhere decisions must be explained.

## The Cost Function: Log Loss

MSE works poorly with the sigmoid, so logistic regression uses **binary cross-entropy**, also called **log loss**:

```
loss = -[ y * log(p) + (1 - y) * log(1 - p) ]
```

Consider what it does:

- If the true label is 1 and the model says p = 0.99, the loss is tiny.
- If the true label is 1 and the model says p = 0.01, the loss is huge.

Confident wrong answers are punished severely, which pushes the model towards well-calibrated probabilities. The weights are found with gradient descent, just as in Chapter 3, and log loss has a single minimum, so training is reliable.

## Logistic Regression in Code

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0))
model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]    # probability of class 1
preds = (probs >= 0.5).astype(int)
```

In scikit-learn, `C` is the *inverse* of regularization strength: a smaller C means stronger regularization and a simpler model.

## Multi-Class Classification

What if there are more than two classes, such as classifying handwritten digits 0 to 9?

### One-vs-Rest

Train one binary classifier per class: "is it a 3 or not?", "is it a 7 or not?", and so on. For a new example, pick the class whose classifier is most confident.

### Softmax Regression

**Softmax regression** (multinomial logistic regression) handles all classes at once. It computes a score for each class and converts the scores into probabilities that add up to 1:

```
p(class k) = e^(z_k) / sum over all classes j of e^(z_j)
```

The loss is **categorical cross-entropy**. Softmax also appears as the final layer of most neural network classifiers.

| Setting | Output | Loss |
|---|---|---|
| Binary classification | Sigmoid, one probability | Binary cross-entropy |
| Multi-class (one label) | Softmax, probabilities sum to 1 | Categorical cross-entropy |
| Multi-label (several labels) | One sigmoid per label | Binary cross-entropy per label |

Multi-label problems are those where an example can belong to several classes at once, such as a movie that is both "comedy" and "romance".

## Choosing the Threshold

The default threshold of 0.5 is not always right. Raising it makes the model more cautious about predicting class 1: fewer false alarms, but more missed positives. Lowering it catches more positives at the cost of more false alarms. Chapter 5 introduces precision, recall and the ROC curve, which help you pick a threshold on purpose.

## Other Common Classifiers

Logistic regression is a baseline. Other classifiers you will meet in this book include:

- **k-nearest neighbours:** classify by the majority vote of the closest training examples (Chapter 7).
- **Naive Bayes:** use Bayes' theorem with a simplifying independence assumption. It is very fast and works surprisingly well for text such as spam filtering.
- **Decision trees and random forests** (Chapter 6).
- **Support vector machines** (Chapter 7).
- **Neural networks** (Chapter 9).

### A Quick Look at Naive Bayes

Naive Bayes predicts the class with the highest probability given the features, using

```
P(class | features)  is proportional to  P(class) * P(feature1 | class) * P(feature2 | class) * ...
```

It is "naive" because it assumes features are independent given the class, which is rarely exactly true. For spam, it asks: how common is spam overall, and how often do words like "free" and "winner" appear in spam compared with normal mail?

## Strengths and Weaknesses of Logistic Regression

Strengths:

- Fast to train, even on large datasets.
- Produces probabilities.
- Weights are interpretable.
- Less prone to overfitting than complex models, especially with regularization.

Weaknesses:

- Draws only linear boundaries unless you engineer features.
- Struggles with complex interactions between features.
- Sensitive to strongly correlated features and to unscaled data.

## Summary

- Classification predicts categories; logistic regression is a linear classifier that outputs probabilities.
- The sigmoid squashes a linear score into a probability; a threshold turns it into a class.
- Weights change the log-odds and can be interpreted.
- Training minimises log loss (binary cross-entropy) with gradient descent.
- Multi-class problems use one-vs-rest or softmax with categorical cross-entropy.
- The threshold can and should be tuned to the costs of different mistakes.

## Practice Questions

1. Why is linear regression unsuitable for classification?
2. What is sigmoid(0)? What happens to sigmoid(z) as z becomes very large?
3. Explain why log loss punishes confident wrong predictions more than MSE would.
4. When would you choose a threshold lower than 0.5? Give a real example.
5. What is the difference between multi-class and multi-label classification?
