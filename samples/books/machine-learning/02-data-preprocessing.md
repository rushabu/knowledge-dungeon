# Working with Data

Data scientists often joke that they spend 80 percent of their time cleaning data and 20 percent complaining about it. The joke is close to the truth. Models learn only what the data shows them, so messy, biased or badly prepared data produces bad models no matter how clever the algorithm. This chapter covers the essential steps between raw data and a dataset ready for training.

## Kinds of Data

Features come in a few basic types, and each needs different handling.

- **Numerical (quantitative):** numbers that can be measured.
  - *Continuous:* any value in a range, such as height or temperature.
  - *Discrete:* countable values, such as number of rooms.
- **Categorical (qualitative):** labels or groups.
  - *Nominal:* no natural order, such as city or colour.
  - *Ordinal:* a meaningful order, such as small / medium / large, or grade A / B / C.
- **Text, images, audio and time series:** unstructured data that must be converted into numbers before most models can use it.

## Exploring the Data

Before changing anything, look at the data. **Exploratory data analysis (EDA)** means summarising and plotting data to understand it.

```python
import pandas as pd

df = pd.read_csv("houses.csv")
print(df.shape)          # rows and columns
print(df.head())         # first five rows
print(df.info())         # column types and missing counts
print(df.describe())     # mean, std, min, max, quartiles
```

Useful questions to ask:

- How many rows and columns are there?
- Which columns have missing values, and how many?
- What are the ranges of numerical features? Are there impossible values, such as a house with -3 bedrooms?
- How are the labels distributed? If 99 percent of transactions are genuine, a model that always says "genuine" is 99 percent accurate but useless.
- Which features seem related to the target?

Plots help enormously: **histograms** show distributions, **box plots** reveal outliers, **scatter plots** show relationships between two variables, and a **correlation heatmap** summarises how numerical features move together.

## Handling Missing Values

Real data has gaps: a customer skipped a survey question, a sensor went offline, a field was added to a form only last year.

Options:

1. **Remove rows** with missing values. Simple, but wasteful if many rows are affected, and it can bias the data.
2. **Remove columns** that are mostly empty.
3. **Impute** (fill in) values:
   - numerical: the **mean** or, better when there are outliers, the **median**;
   - categorical: the **most frequent** value, or a new category such as "Unknown";
   - model-based: predict the missing value from other features.
4. **Add an indicator** column, such as `income_missing = 1`, because missingness itself can carry information.

```python
df["income"] = df["income"].fillna(df["income"].median())
df["city"] = df["city"].fillna("Unknown")
```

> **Key idea:** Compute imputation values (such as the median) from the **training set only**, then apply the same values to the validation and test sets. Otherwise information from the test set leaks into training.

## Outliers

An **outlier** is a value far from the rest. Some are errors, such as a typing mistake that turns age 25 into 250. Others are real but rare, such as a genuine billionaire in an income dataset.

A common rule flags values outside 1.5 times the **interquartile range (IQR)**: below Q1 - 1.5 x IQR or above Q3 + 1.5 x IQR. Depending on the cause, you can correct errors, remove them, cap extreme values (**clipping**), or transform the feature, for example by taking a logarithm to shrink large values.

## Encoding Categorical Features

Most algorithms need numbers, not words.

- **Label (ordinal) encoding:** map categories to integers. Good for ordered categories: small = 0, medium = 1, large = 2.
- **One-hot encoding:** create one binary column per category. City = Pune becomes `city_Pune = 1, city_Mumbai = 0, city_Delhi = 0`. Use it for nominal categories, because integer codes would suggest a false order (Delhi > Mumbai?).

```python
df = pd.get_dummies(df, columns=["city"])
```

With hundreds of categories, one-hot encoding creates too many columns. Alternatives include grouping rare categories into "Other", or **target encoding**, which replaces each category with the average target value for that category (computed carefully to avoid leakage).

## Feature Scaling

Features often have very different ranges: area might be 500 to 5,000 square feet, while bedrooms range from 1 to 5. Algorithms that use distances (k-nearest neighbours, k-means, SVMs) or gradient descent (linear models, neural networks) work much better when features are on similar scales.

- **Min-max normalisation** rescales to the range 0 to 1: x' = (x - min) / (max - min).
- **Standardisation** (z-score) gives mean 0 and standard deviation 1: x' = (x - mean) / std.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # learn mean and std from training data
X_test_scaled = scaler.transform(X_test)         # reuse them on test data
```

Tree-based models such as decision trees and random forests do not need scaling, because they split on one feature at a time.

## Feature Engineering

**Feature engineering** means creating new features that make patterns easier for the model to find. It is where domain knowledge pays off.

- From a date, extract day of week, month, or whether it is a holiday.
- From height and weight, compute BMI.
- From a transaction history, compute "number of purchases in the last 30 days".
- From text, count words or detect keywords.
- Combine features: price per square foot = price / area.

> **Key idea:** A good feature can improve a model more than switching to a more advanced algorithm.

### Feature Selection

More features are not always better. Irrelevant features add noise and increase the risk of overfitting. Feature selection methods include removing features with almost no variation, removing one of two highly correlated features, and keeping the features a model ranks as most important.

## Splitting the Data

We divide the dataset into separate parts:

- **Training set** (often 60 to 80 percent): used to fit the model.
- **Validation set** (10 to 20 percent): used to compare models and tune hyperparameters.
- **Test set** (10 to 20 percent): used **once**, at the very end, to estimate real-world performance.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
```

`stratify=y` keeps the proportion of each class the same in every split, which matters for imbalanced data. For **time series**, never shuffle: train on the past and test on the future, or the model will "see" the future.

## Data Leakage

**Data leakage** happens when information that would not be available at prediction time sneaks into training. The model then looks brilliant in testing and fails in real use.

Examples:

- Scaling or imputing using statistics from the whole dataset, including test rows.
- Including a feature that is recorded *after* the outcome, such as "refund issued" when predicting whether an order will be returned.
- Having the same customer's records in both training and test sets.

The cure is to split first, then fit every preprocessing step on the training data only. scikit-learn **pipelines** make this automatic.

```python
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression())
model.fit(X_train, y_train)
```

## Imbalanced Data

When one class is rare, as with fraud or disease, models tend to ignore it. Remedies include:

- **Oversampling** the minority class, for example with SMOTE, which creates synthetic examples;
- **Undersampling** the majority class;
- using **class weights** so mistakes on the rare class cost more;
- evaluating with precision, recall and F1 instead of accuracy (Chapter 5).

## Summary

- Know your feature types: numerical (continuous or discrete) and categorical (nominal or ordinal).
- Explore data before modelling: shapes, types, missing values, ranges and label balance.
- Handle missing values by removing, imputing or flagging them; deal with outliers deliberately.
- One-hot encode nominal categories; scale features for distance- and gradient-based models.
- Engineer informative features and remove useless ones.
- Split into training, validation and test sets, and prevent leakage by fitting preprocessing on training data only.

## Practice Questions

1. Classify these features: pin code, temperature, T-shirt size, number of siblings.
2. Why is the median often better than the mean for imputing income?
3. Why is label encoding a bad idea for the feature "city"?
4. Give two examples of data leakage and explain how to prevent each.
5. Which of these models need feature scaling: k-nearest neighbours, decision tree, logistic regression?
