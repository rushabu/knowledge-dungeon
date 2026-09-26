# Neural Networks and Deep Learning

Neural networks power the most visible achievements of modern AI: recognising faces, translating languages, generating images and holding conversations. The core ideas, however, are surprisingly approachable. A neural network is a stack of simple units, each doing a weighted sum followed by a small non-linear function, trained with the same gradient descent you met in Chapter 3.

## From Neurons to Perceptrons

Biological neurons receive signals through dendrites, combine them, and fire an output signal if the combined input is strong enough. The artificial **neuron** (or **perceptron**) is a loose mathematical imitation:

```
z = w1*x1 + w2*x2 + ... + wn*xn + b
output = activation(z)
```

Each input has a **weight**, there is a **bias**, and an **activation function** decides the output. A single perceptron with a step activation can learn to separate two classes with a straight line, just like logistic regression. It famously cannot learn the XOR function, which needs a curved boundary. The solution is to stack neurons into layers.

## Multi-Layer Networks

A **feed-forward neural network**, also called a **multi-layer perceptron (MLP)**, has:

- an **input layer**, with one value per feature;
- one or more **hidden layers** of neurons, each connected to every neuron in the previous layer;
- an **output layer**, which produces the prediction.

Data flows forward from inputs to outputs. Each hidden layer builds new features out of the previous layer's outputs. In an image model, early layers might detect edges, middle layers shapes, and later layers whole objects. "Deep" learning simply means networks with many hidden layers.

> **Key idea:** The power of neural networks comes from learning features automatically, layer by layer, instead of relying on hand-engineered features.

## Activation Functions

Without non-linear activations, a stack of layers would collapse into one big linear function, no more powerful than linear regression. Activations add the non-linearity.

| Activation | Formula (idea) | Typical use |
|---|---|---|
| Sigmoid | Squashes to 0 to 1 | Binary output layer |
| Tanh | Squashes to -1 to 1 | Older hidden layers, some recurrent nets |
| ReLU | max(0, z) | Default for hidden layers |
| Leaky ReLU | Small slope for negative z | Avoids "dead" ReLU units |
| Softmax | Probabilities summing to 1 | Multi-class output layer |

**ReLU** (rectified linear unit) is the default in hidden layers because it is cheap to compute and helps gradients flow in deep networks. Sigmoid and tanh flatten out for large inputs, which slows learning.

## Training: Forward Pass, Loss and Backpropagation

Training repeats four steps for each mini-batch of data.

1. **Forward pass:** feed inputs through the network to get predictions.
2. **Compute the loss:** compare predictions with true labels, using MSE for regression and cross-entropy for classification.
3. **Backward pass (backpropagation):** compute the gradient of the loss with respect to every weight, working backwards from the output layer. It uses the **chain rule** from calculus to reuse intermediate results efficiently.
4. **Update weights:** move each weight a small step against its gradient.

One full pass through the training data is an **epoch**. Networks typically train for many epochs.

### Optimizers

Plain gradient descent can be slow or erratic. Improved **optimizers** adjust the steps intelligently:

- **SGD with momentum** keeps a running average of past gradients, like a ball rolling downhill that builds up speed and rolls through small bumps.
- **RMSProp** adapts the step size of each weight based on the size of its recent gradients.
- **Adam** combines momentum and adaptive step sizes. It is the usual default.

## A Neural Network in Code

Using the Keras API:

```python
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Input(shape=(20,)),
    keras.layers.Dense(64, activation="relu"),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X_train, y_train, epochs=30, batch_size=32, validation_split=0.2)
```

PyTorch is the other major framework, popular in research. The ideas are identical; only the style differs.

## Fighting Overfitting

Neural networks have many parameters, often millions, so they overfit easily.

- **More data** is the most reliable cure. **Data augmentation** creates extra training examples by, for instance, flipping, rotating or cropping images.
- **Dropout** randomly switches off a fraction of neurons during each training step, so the network cannot rely on any single neuron.
- **Weight decay (L2 regularization)** penalises large weights.
- **Early stopping** halts training when validation loss stops improving.
- **Batch normalization** standardises the inputs to each layer, which speeds up and stabilises training and adds a mild regularizing effect.

### Vanishing and Exploding Gradients

In very deep networks, gradients can shrink towards zero as they travel backwards through many layers, so early layers barely learn (**vanishing gradients**), or they can grow uncontrollably (**exploding gradients**). ReLU activations, careful weight initialisation, batch normalization, **residual (skip) connections** and gradient clipping all help.

## Specialised Architectures

### Convolutional Neural Networks (CNNs)

Images have spatial structure: nearby pixels are related. A **CNN** uses **convolutional layers**, in which small filters (such as 3 x 3 grids of weights) slide across the image, detecting local patterns like edges and textures. The same filter is reused everywhere, which massively reduces the number of parameters. **Pooling layers** shrink the image while keeping the strongest signals. CNNs dominate image classification, object detection and medical imaging.

### Recurrent Neural Networks (RNNs)

Text, speech and time series are **sequences**. An **RNN** processes one element at a time while carrying a hidden state, a kind of memory, from step to step. Plain RNNs forget long-range information, so improved versions called **LSTM** and **GRU** add gates that control what to remember and what to forget.

### Transformers

**Transformers** replaced RNNs for most language tasks. Their key mechanism, **self-attention**, lets every word in a sentence look directly at every other word and decide which ones matter for its meaning. Transformers process sequences in parallel, which makes them fast to train on huge datasets. Large language models, modern translation systems and many image models are transformers.

## Transfer Learning

Training a large network from scratch needs enormous data and computing power. **Transfer learning** starts from a model already trained on a big dataset, such as an image model trained on millions of photos, and **fine-tunes** it on your smaller dataset. The early layers already know general features like edges and shapes; only the later layers need adapting. This lets small teams build strong models with a few thousand examples.

## When to Use Deep Learning

Deep learning shines with **unstructured data** (images, audio, text) and large datasets. For small or medium **tabular** datasets, gradient-boosted trees (Chapter 6) are usually as accurate or better, and faster and easier to tune. Pick the tool that fits the data.

## Summary

- A neuron computes a weighted sum plus bias and applies an activation function.
- Stacking layers with non-linear activations lets networks learn complex functions and their own features.
- Training uses forward passes, a loss, backpropagation and an optimizer such as Adam.
- Dropout, weight decay, early stopping, data augmentation and batch normalization fight overfitting.
- CNNs suit images, RNNs and LSTMs suit sequences, and transformers use attention and power modern language models.
- Transfer learning reuses pre-trained networks; for tabular data, tree ensembles often win.

## Practice Questions

1. Why does a network need non-linear activation functions?
2. Describe the four steps of one training iteration.
3. What does dropout do, and why does it reduce overfitting?
4. Why are CNNs better suited to images than fully connected networks?
5. Explain transfer learning with an example relevant to your college.
