# What Is Machine Learning?

Your email app moves spam out of your inbox. Your music app suggests songs you end up loving. Your phone unlocks when it sees your face. None of these programs were given a list of rules by a programmer. Instead, they **learned** from examples. This chapter explains what that means and introduces the main ideas you will use throughout the book.

## Traditional Programming vs Machine Learning

In **traditional programming**, a person writes rules, the computer applies them to data, and out come answers.

```
Rules + Data  ->  Program  ->  Answers
```

To detect spam the traditional way, you might write: "if the email contains 'lottery' and 'winner', mark it as spam". This breaks quickly. Spammers change their words, and you end up with thousands of fragile rules.

In **machine learning**, we give the computer data *and* the correct answers, and it works out the rules itself.

```
Data + Answers  ->  Learning algorithm  ->  Model (the rules)
```

The result is a **model**: a function that takes new inputs and produces predictions. Show it thousands of emails labelled "spam" or "not spam", and it learns which patterns matter.

> **Key idea:** Machine learning is the study of algorithms that improve their performance at a task through experience (data), rather than through explicitly programmed rules.

A classic definition by Tom Mitchell puts it precisely: a program learns from **experience E** with respect to a **task T** and **performance measure P** if its performance at T, measured by P, improves with E. For spam filtering, T is classifying emails, E is a set of labelled emails, and P is the percentage classified correctly.

## When Should You Use Machine Learning?

Machine learning shines when:

- the rules are too complex to write by hand (recognising faces, understanding speech),
- the rules keep changing (spam, fraud, trending products),
- the problem involves huge amounts of data that no person could study, or
- we want to discover patterns we did not know existed (grouping customers).

It is a poor choice when a simple rule works perfectly, when there is little or no data, or when every decision must be fully explainable and a formula already exists. You do not need machine learning to calculate GST.

## Types of Machine Learning

### Supervised Learning

In **supervised learning**, every training example comes with the correct answer, called the **label**. The model learns to map inputs to labels.

- **Classification:** the label is a category. Is this email spam or not? Is this tumour benign or malignant? Which digit is in this image?
- **Regression:** the label is a number. What will this house sell for? How many units will we sell next month?

### Unsupervised Learning

In **unsupervised learning**, there are no labels. The model looks for structure on its own.

- **Clustering:** grouping similar items, such as customers with similar shopping habits.
- **Dimensionality reduction:** compressing many features into a few while keeping most of the information.
- **Anomaly detection:** spotting unusual items, such as a fraudulent transaction.

### Reinforcement Learning

In **reinforcement learning**, an **agent** takes actions in an **environment** and receives **rewards** or penalties. It learns a strategy (a **policy**) that maximises total reward over time. Game-playing programs, robot control and some recommendation systems use reinforcement learning.

### Semi-Supervised and Self-Supervised Learning

Labels are often expensive, because someone must hand-label every example. **Semi-supervised learning** combines a small labelled set with a large unlabelled one. **Self-supervised learning** creates labels from the data itself, for example by hiding a word in a sentence and asking the model to predict it. Large language models are trained this way.

| Type | Has labels? | Example task |
|---|---|---|
| Supervised | Yes | Predict house prices |
| Unsupervised | No | Group customers |
| Reinforcement | Rewards, not labels | Learn to play chess |
| Self-supervised | Created from data | Predict the next word |

## Key Vocabulary

- **Dataset:** the collection of examples used for learning.
- **Example / sample / instance:** one row of the dataset, such as one house.
- **Feature:** an input variable describing an example, such as area, number of bedrooms or location. Features are usually written x.
- **Label / target:** the value we want to predict, such as the price. Usually written y.
- **Model:** the learned function that maps features to predictions.
- **Parameters:** the numbers inside the model that are learned from data, such as weights.
- **Hyperparameters:** settings chosen *before* training, such as how many trees a forest has. They are not learned directly.
- **Training:** the process of adjusting parameters to fit the data.
- **Inference / prediction:** using a trained model on new data.

## The Machine Learning Workflow

Real projects follow a fairly standard sequence of steps.

1. **Define the problem.** What exactly are we predicting, and how will we measure success? "Reduce customer churn" becomes "predict which customers will cancel within 30 days".
2. **Collect data.** Gather examples from databases, logs, surveys or public datasets.
3. **Explore and clean the data.** Look for missing values, errors and odd distributions (Chapter 2).
4. **Engineer features.** Choose and transform inputs that help the model.
5. **Split the data** into training, validation and test sets.
6. **Choose and train models.** Start simple, then try more powerful models.
7. **Evaluate.** Measure performance on data the model has never seen (Chapter 5).
8. **Tune.** Adjust hyperparameters to improve validation performance.
9. **Deploy.** Put the model into a real application.
10. **Monitor.** Watch performance over time, because the world changes and models go stale.

> **Key idea:** In practice, most time goes into steps 2 to 4, the data work. A simple model on clean, relevant data usually beats a fancy model on messy data.

## Generalization: The Real Goal

A model is only useful if it works on **new** data. Memorising the training examples is easy; performing well on unseen examples is the real challenge. This ability is called **generalization**.

- **Underfitting:** the model is too simple to capture the pattern. It performs badly even on the training data. Fitting a straight line to a curved relationship underfits.
- **Overfitting:** the model is so complex that it memorises noise in the training data. It looks excellent in training but fails on new data, like a student who memorises answers without understanding.
- **Good fit:** the model captures the real pattern and ignores the noise.

This is why we always keep a **test set** aside and never train on it. Its score estimates how the model will perform in the real world.

## A Tiny Example in Python

The scikit-learn library makes simple models very short to write.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_iris(return_X_y=True)             # 150 flowers, 4 features each
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

model = DecisionTreeClassifier(max_depth=3)
model.fit(X_train, y_train)                   # training
print(model.score(X_test, y_test))            # accuracy on unseen flowers
```

The whole ML workflow is visible here in miniature: load data, split it, train a model, and evaluate it on data it has not seen.

## A Brief History

- **1950s:** Alan Turing asks whether machines can think; Arthur Samuel's checkers program learns from self-play and coins the term "machine learning".
- **1958:** Frank Rosenblatt builds the perceptron, an early neural network.
- **1980s-1990s:** decision trees, backpropagation for neural networks and support vector machines become popular.
- **2000s:** large datasets and ensemble methods such as random forests spread through industry.
- **2012 onwards:** deep learning, powered by GPUs and big data, transforms image recognition, speech and language.
- **2020s:** large language models and generative AI reach millions of everyday users.

## Summary

- Machine learning learns rules from data and answers instead of having rules written by hand.
- Supervised learning uses labels (classification and regression); unsupervised learning finds structure without labels; reinforcement learning learns from rewards.
- Features are inputs, labels are targets, parameters are learned and hyperparameters are chosen.
- The workflow runs from problem definition through data work, training and evaluation to deployment and monitoring.
- The goal is generalization: avoid both underfitting and overfitting, and judge models on unseen test data.

## Practice Questions

1. Explain the difference between traditional programming and machine learning with an example of your own.
2. Classify each as classification, regression or clustering: predicting tomorrow's temperature, detecting fraudulent payments, grouping news articles by topic.
3. What is the difference between a parameter and a hyperparameter?
4. Describe overfitting using a student-exam analogy.
5. Why must the test set never be used during training?
