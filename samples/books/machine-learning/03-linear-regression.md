# Linear Regression

Linear regression is the "hello world" of machine learning. It predicts a number by drawing the best straight line (or flat surface) through the data. It is simple, fast and easy to interpret, and it introduces three ideas that power almost every other model: a **hypothesis**, a **cost function** and **gradient descent**.

## The Problem

Suppose we want to predict the price of a flat from its area. We have data on past sales:

| Area (sq ft) | Price (lakh) |
|---|---|
| 600 | 45 |
| 850 | 62 |
| 1,000 | 70 |
| 1,200 | 86 |
| 1,500 | 104 |

Plotting these points shows a clear upward trend. Linear regression finds the line that fits them best, so we can predict the price of a 1,100 sq ft flat.

## The Hypothesis

With one feature, the model is the equation of a line:

```
y_hat = w * x + b
```

- x is the input feature (area),
- y_hat (read "y hat") is the predicted price,
- w is the **weight** or slope: how much the price rises for each extra square foot,
- b is the **bias** or intercept: the predicted price when x is 0.

With many features (area, bedrooms, age of building, distance to station), the model becomes

```
y_hat = w1*x1 + w2*x2 + ... + wn*xn + b
```

This is **multiple linear regression**. Each weight tells us how much the prediction changes when that feature increases by one unit, keeping the others fixed.

## Measuring Error: The Cost Function

For each example, the **residual** (error) is the difference between the actual value and the prediction: y - y_hat. We need a single number that summarises how bad the line is overall.

The standard choice is the **mean squared error (MSE)**:

```
MSE = (1/n) * sum over all examples of (y - y_hat)^2
```

Squaring does two useful things: it makes every error positive, and it punishes large errors much more than small ones. Training means finding the values of w and b that make the MSE as small as possible.

> **Key idea:** A model is only as good as the thing it is trained to minimise. The cost function defines what "good" means for the learning algorithm.

## Finding the Best Line

### The Normal Equation

For linear regression there is an exact formula, called the **normal equation**, which gives the best weights in one step using matrix algebra. It works well for small and medium problems but becomes slow when there are very many features, because it requires inverting a large matrix.

### Gradient Descent

**Gradient descent** is a general method used by almost every modern ML model, including huge neural networks.

Imagine standing on a foggy hillside and wanting to reach the valley. You cannot see the bottom, but you can feel the slope under your feet. So you take a step downhill, feel the slope again, and repeat.

1. Start with some values of w and b (often zeros or small random numbers).
2. Compute the **gradient**: the direction in which the cost increases fastest.
3. Take a small step in the **opposite** direction.
4. Repeat until the cost stops decreasing.

```
w = w - learning_rate * (d cost / d w)
b = b - learning_rate * (d cost / d b)
```

For MSE, the gradients are simple averages over the data:

```
d cost / d w = (2/n) * sum( (y_hat - y) * x )
d cost / d b = (2/n) * sum( (y_hat - y) )
```

### The Learning Rate

The **learning rate** controls the step size.

- **Too small:** training is painfully slow.
- **Too large:** steps overshoot the valley, and the cost may bounce around or even grow.
- **Just right:** the cost falls steadily and levels off.

Plotting cost against the number of iterations (a **learning curve**) is the easiest way to spot a bad learning rate.

### Variants

- **Batch gradient descent** uses all examples for every step. Stable but slow for big data.
- **Stochastic gradient descent (SGD)** uses one random example per step. Fast and noisy.
- **Mini-batch gradient descent** uses small batches, such as 32 or 64 examples. It is the usual compromise and the standard in deep learning.

## Linear Regression in Code

```python
import numpy as np

x = np.array([600, 850, 1000, 1200, 1500], dtype=float)
y = np.array([45, 62, 70, 86, 104], dtype=float)
x = (x - x.mean()) / x.std()          # scale for stable gradient descent

w, b, lr = 0.0, 0.0, 0.1
for step in range(500):
    y_hat = w * x + b
    dw = 2 * np.mean((y_hat - y) * x)
    db = 2 * np.mean(y_hat - y)
    w, b = w - lr * dw, b - lr * db

print(w, b)
```

In practice you would simply use scikit-learn:

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression().fit(X_train, y_train)
print(model.coef_, model.intercept_)
print(model.predict([[1100]]))
```

## Evaluating Regression Models

| Metric | Meaning | Notes |
|---|---|---|
| MAE | Mean absolute error | Average size of errors, in the target's units |
| MSE | Mean squared error | Punishes large errors heavily |
| RMSE | Square root of MSE | Back in the target's units |
| R^{2} | Fraction of variance explained | 1 is perfect; 0 is no better than predicting the mean |

An R^{2} of 0.85 means the model explains 85 percent of the variation in prices. RMSE of 5 means predictions are typically off by around 5 lakh.

## Assumptions of Linear Regression

Linear regression works best when:

1. **Linearity:** the relationship between features and target is roughly linear.
2. **Independence:** errors for different examples are independent.
3. **Constant variance:** errors are about equally spread for small and large predictions.
4. **Normal errors:** residuals are roughly bell-shaped (important for confidence intervals).
5. **Little multicollinearity:** features are not strongly correlated with each other. If area and number of rooms move together, their individual weights become unreliable.

Plotting residuals against predictions is a quick way to check these assumptions. A random cloud is good; a curve or a funnel shape signals trouble.

## Polynomial Regression

What if the relationship is curved? We can still use linear regression by adding **polynomial features** such as x^{2} and x^{3}. The model is still "linear" in its weights, but it can fit curves.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
```

Beware: a very high degree fits every wiggle in the training data, which is overfitting.

## Regularization

**Regularization** fights overfitting by adding a penalty for large weights to the cost function.

- **Ridge regression (L2):** adds lambda times the sum of squared weights. It shrinks all weights towards zero but rarely makes them exactly zero.
- **Lasso regression (L1):** adds lambda times the sum of absolute weights. It can shrink some weights to exactly zero, which performs **feature selection**.
- **Elastic Net:** a mix of both.

The hyperparameter lambda (called `alpha` in scikit-learn) controls the strength. Larger values give simpler models. Features must be scaled before regularization, or the penalty treats them unfairly.

> **Key idea:** Regularization trades a little accuracy on the training data for better generalization to new data.

## Summary

- Linear regression predicts a number with a weighted sum of features plus a bias.
- Training minimises a cost function, usually mean squared error.
- Gradient descent repeatedly steps opposite the gradient; the learning rate sets the step size.
- Evaluate with MAE, RMSE and R^{2}; check residual plots for broken assumptions.
- Polynomial features let a linear model fit curves.
- Ridge and Lasso add penalties that reduce overfitting; Lasso can also select features.

## Practice Questions

1. What do the weight and bias mean in the model price = w * area + b?
2. Why do we square errors in MSE instead of just adding them?
3. Describe what happens when the learning rate is too large.
4. What is the difference between Ridge and Lasso regression?
5. A model has R^{2} = 0.98 on training data and 0.60 on test data. What is going on, and what would you try?
