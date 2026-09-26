# Machine Learning in Practice and Ethics

A model that scores well in a notebook is only the beginning. It has to be deployed, kept healthy as the world changes, and used fairly and responsibly. This final chapter covers how ML systems work in the real world, and the ethical questions every practitioner should ask.

## From Notebook to Product

A typical production ML system has several parts beyond the model itself.

1. **Data pipeline:** collects, validates and transforms data regularly.
2. **Training pipeline:** retrains the model on fresh data, evaluates it and stores it with a version number.
3. **Model registry:** keeps track of every model version, its metrics and the data it was trained on.
4. **Serving:** makes predictions available to applications.
5. **Monitoring:** watches inputs, predictions and outcomes over time.

The discipline of running these systems reliably is called **MLOps**, bringing ideas from software engineering (version control, automated testing, continuous deployment) to machine learning.

## Ways to Serve Predictions

- **Batch prediction:** compute predictions for everyone at once on a schedule, such as nightly churn scores for all customers. Simple and efficient.
- **Online (real-time) prediction:** a web service returns a prediction on request within milliseconds, such as fraud checks during payment.
- **On-device prediction:** the model runs on the phone or device itself, such as keyboard suggestions. This is fast, works offline and keeps data private, but needs small models.

A minimal online service might look like this:

```python
from fastapi import FastAPI
import joblib

app = FastAPI()
model = joblib.load("churn_model.joblib")

@app.post("/predict")
def predict(customer: dict):
    features = [[customer["tenure"], customer["monthly_bill"], customer["complaints"]]]
    return {"churn_probability": float(model.predict_proba(features)[0, 1])}
```

## Reproducibility

Could you rebuild last month's model exactly? Reproducibility requires:

- versioned **code** (git),
- versioned **data**, or at least a record of exactly which data was used,
- fixed **random seeds**,
- recorded **hyperparameters** and library versions.

Experiment-tracking tools such as MLflow and Weights & Biases record these details automatically.

## Monitoring and Drift

The world changes, and models trained on the past slowly go stale.

- **Data drift:** the distribution of inputs changes. A loan model trained before a recession sees very different incomes afterwards.
- **Concept drift:** the relationship between inputs and outputs changes. Fraudsters invent new tricks, so old fraud patterns stop working.

> **Key idea:** Every deployed model needs monitoring. Track input statistics, prediction distributions and, when labels arrive later, real accuracy. Retrain when performance drops.

## Explainability

Many decisions must be explained: why was this loan rejected, why was this patient flagged? Some models are interpretable by design, such as linear models and small trees. For complex models, **explainability tools** help.

- **Feature importance** shows which features the model relies on overall.
- **Partial dependence plots** show how predictions change as one feature varies.
- **SHAP values** break down an individual prediction into contributions from each feature: "income lowered this applicant's score by 0.12; late payments lowered it by 0.20."
- **LIME** fits a simple local model around one prediction to explain it.

Explanations build trust, help debug models, and are increasingly required by regulations.

## Fairness and Bias

Machine learning models learn patterns from historical data, and history contains human bias. A model can therefore repeat or even amplify unfair treatment.

### Where Bias Comes From

- **Historical bias:** if past hiring favoured one group, a model trained on past hiring decisions learns that preference.
- **Representation bias:** if a face dataset contains mostly light-skinned faces, the model performs worse on darker-skinned faces.
- **Measurement bias:** the data measures the wrong thing. Using "number of arrests" as a stand-in for "crime" reflects where police patrol, not only where crime happens.
- **Proxy variables:** even if you remove sensitive attributes such as gender or caste, other features, such as pin code or first name, can act as proxies for them.

### Measuring Fairness

There are several definitions of fairness, and they cannot all be satisfied at once:

- **Demographic parity:** each group receives positive predictions at the same rate.
- **Equal opportunity:** qualified people in each group are approved at the same rate (equal true positive rates).
- **Equalised odds:** equal true positive *and* false positive rates across groups.
- **Calibration:** a predicted score of 0.8 means the same real-world chance for every group.

Choosing which definition matters is a human and social decision, not just a technical one.

### Reducing Bias

- Collect more representative data.
- Audit model performance separately for different groups.
- Adjust training, for example by reweighting examples, or adjust thresholds per group where appropriate and lawful.
- Keep humans involved in high-stakes decisions.

> **Key idea:** "The algorithm decided" is never an excuse. People choose the data, the objective and how predictions are used, and they are responsible for the outcomes.

## Privacy

Models are often trained on personal data.

- Collect only the data you need (**data minimisation**) and get proper consent.
- **Anonymise** data, remembering that combinations of fields like age, pin code and gender can re-identify people.
- Models can **memorise** training data; large language models have been shown to repeat private text they were trained on.
- **Differential privacy** adds carefully calibrated noise so no individual's data can be inferred from the results.
- **Federated learning** trains models across many devices without collecting the raw data centrally, as with phone keyboards learning from typing.

Laws such as India's Digital Personal Data Protection Act and Europe's GDPR set legal requirements for handling personal data.

## Safety, Security and Misuse

- **Adversarial examples:** tiny, carefully crafted changes to an input, invisible to humans, can fool a model, such as stickers that make a stop sign look like a speed-limit sign to a car's camera.
- **Data poisoning:** attackers insert bad examples into training data to corrupt a model.
- **Misuse:** the same technology can create deepfakes, automate scams or enable mass surveillance.

Responsible teams test models against such attacks, restrict access to powerful capabilities and think ahead about how a system could be misused.

## Environmental Cost

Training very large models consumes a lot of electricity. Choosing efficient models, reusing pre-trained models through transfer learning, and not training bigger than necessary all reduce the environmental footprint.

## A Responsible ML Checklist

Before deploying a model, ask:

1. Is machine learning actually needed, or would a simple rule do?
2. Is the training data representative of the people the model will affect?
3. How does performance differ across groups?
4. Can decisions be explained to the people affected?
5. What happens when the model is wrong, and can people appeal?
6. How will the model be monitored and updated?
7. Is personal data protected and used with consent?

## Where to Go Next

- Practise on real datasets from Kaggle or the UCI repository.
- Learn a deep learning framework (PyTorch or TensorFlow) properly.
- Study the maths more deeply: linear algebra, probability and optimisation.
- Read about specialised fields that interest you: computer vision, natural language processing, recommender systems or reinforcement learning.
- Build and deploy a complete project end to end. It teaches more than any course.

## Summary

- Production ML includes data pipelines, training pipelines, a model registry, serving and monitoring (MLOps).
- Predictions can be served in batch, online or on-device.
- Reproducibility needs versioned code, data, seeds and settings.
- Data drift and concept drift make models go stale; monitor and retrain.
- Explainability tools such as SHAP help justify predictions.
- Bias enters through data, measurement and proxies; fairness has several competing definitions.
- Protect privacy, defend against attacks and misuse, and consider environmental cost.

## Practice Questions

1. What is the difference between data drift and concept drift? Give an example of each.
2. When would you choose batch prediction over online prediction?
3. Explain how a model can be biased even if gender is removed from the features.
4. Why can't all definitions of fairness be satisfied at once? Discuss briefly.
5. Apply the responsible ML checklist to a model that shortlists job applicants.
