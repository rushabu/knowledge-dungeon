# Unsupervised Learning: Clustering and Dimensionality Reduction

So far every dataset has come with answers. Often, though, we have plenty of data and no labels at all: millions of customers, thousands of documents, endless sensor readings. **Unsupervised learning** finds structure in such data. This chapter covers the two biggest families: **clustering**, which groups similar examples, and **dimensionality reduction**, which compresses many features into a few.

## Clustering

**Clustering** divides data into groups (clusters) such that examples in the same cluster are similar and examples in different clusters are dissimilar.

Common uses:

- **Customer segmentation:** find groups such as bargain hunters, loyal regulars and occasional big spenders, and market to each differently.
- **Document grouping:** organise news articles by topic.
- **Image compression:** replace thousands of colours with the few cluster centres.
- **Anomaly detection:** points far from every cluster may be suspicious.

## k-Means Clustering

k-means is the most popular clustering algorithm.

### The Algorithm

1. Choose the number of clusters, **k**.
2. Place k **centroids** at random (often at k random data points).
3. **Assign** each point to its nearest centroid.
4. **Update** each centroid to be the mean of the points assigned to it.
5. Repeat steps 3 and 4 until assignments stop changing.

The algorithm minimises the **within-cluster sum of squares** (also called **inertia**): the total squared distance from each point to its centroid.

```python
from sklearn.cluster import KMeans

km = KMeans(n_clusters=4, n_init=10, random_state=0)
labels = km.fit_predict(X_scaled)
print(km.cluster_centers_)
```

> **Key idea:** k-means always converges, but possibly to a poor solution that depends on where the centroids started. Running it several times with different starts (`n_init`) and using the smarter **k-means++** initialisation largely solves this.

### Choosing k

- **Elbow method:** run k-means for k = 1, 2, 3, ... and plot inertia. Inertia always falls as k grows, but the curve usually bends at some point. That "elbow" is a reasonable choice.
- **Silhouette score:** for each point, compare its average distance to its own cluster (a) with its average distance to the nearest other cluster (b). The silhouette is (b - a) / max(a, b), ranging from -1 to 1. Higher is better. Choose the k with the highest average silhouette.
- **Domain knowledge:** sometimes the business needs a specific number of segments.

### Limitations of k-Means

- You must choose k in advance.
- It assumes clusters are roughly round and of similar size. It fails on long, curved or nested shapes.
- It is sensitive to outliers, which drag centroids towards them.
- Features must be scaled, because it relies on distances.

## Hierarchical Clustering

**Agglomerative hierarchical clustering** builds a tree of clusters from the bottom up:

1. Start with every point as its own cluster.
2. Repeatedly merge the two closest clusters.
3. Continue until only one cluster remains.

The result is drawn as a **dendrogram**, a tree diagram showing the order and distance of merges. Cutting the dendrogram at a chosen height gives any number of clusters, so you do not need to fix k beforehand.

How is the distance between two *clusters* measured? This is the **linkage**:

- **Single linkage:** distance between the closest pair of points. It can create long, chained clusters.
- **Complete linkage:** distance between the farthest pair. It produces compact clusters.
- **Average linkage:** average distance over all pairs.
- **Ward's method:** merge the pair that increases total within-cluster variance the least. It is often the best default.

Hierarchical clustering is intuitive, but it is slow for large datasets, because it compares all pairs of points.

## DBSCAN: Density-Based Clustering

**DBSCAN** defines clusters as dense regions separated by sparse regions. It has two parameters:

- **eps:** the radius of a neighbourhood;
- **min_samples:** how many points must lie within eps for a point to be a **core point**.

Core points that are close together form a cluster; points near a cluster but not dense themselves are **border points**; points in no dense region are labelled **noise**.

Advantages: it finds clusters of **any shape**, it does not need k, and it identifies outliers automatically. Disadvantages: choosing eps can be tricky, and it struggles when clusters have very different densities.

| Algorithm | Need k? | Cluster shapes | Handles outliers |
|---|---|---|---|
| k-means | Yes | Round, similar size | Poorly |
| Hierarchical | No (cut later) | Depends on linkage | Moderately |
| DBSCAN | No | Any shape | Yes, labels them as noise |

## Dimensionality Reduction

Datasets can have hundreds or thousands of features. **Dimensionality reduction** represents the data with fewer features while keeping as much useful information as possible.

Why bother?

- **Visualisation:** we can only plot 2 or 3 dimensions.
- **Speed:** fewer features mean faster training.
- **Noise reduction:** discarding minor directions can remove noise.
- **Avoiding the curse of dimensionality** for distance-based methods.

## Principal Component Analysis (PCA)

**PCA** finds new axes, called **principal components**, that capture the most variation in the data.

- The **first principal component** is the direction along which the data varies the most.
- The **second** is the direction of greatest remaining variation that is **perpendicular** (uncorrelated) to the first.
- And so on.

We then keep only the first few components. Imagine photographing a 3-D object: a good camera angle keeps most of its shape in a 2-D picture. PCA finds the best angle mathematically.

### Steps

1. Standardise the features (mean 0, standard deviation 1).
2. Compute the covariance matrix of the features.
3. Find its **eigenvectors** (the directions of the components) and **eigenvalues** (how much variance each direction captures).
4. Sort components by eigenvalue and keep the top ones.
5. Project the data onto them.

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=0.95)            # keep enough components for 95% of the variance
X_reduced = pca.fit_transform(X_scaled)
print(pca.n_components_, pca.explained_variance_ratio_)
```

The **explained variance ratio** tells you what fraction of the total variance each component captures. A **scree plot** of these values helps decide how many components to keep.

> **Key idea:** Principal components are combinations of the original features, so they are harder to interpret. PCA also only captures *linear* structure.

### Feature Selection vs Feature Extraction

- **Feature selection** keeps a subset of the original features. They stay interpretable.
- **Feature extraction** (like PCA) creates new features from combinations of the old ones.

## Non-Linear Methods for Visualisation

**t-SNE** and **UMAP** are non-linear techniques designed mainly for visualising high-dimensional data in 2-D. They place similar points close together, often revealing clusters beautifully, for example digits of the same kind forming islands. They are great for exploration, but distances between far-apart clusters in the plot are not meaningful, and they are rarely used as input features for other models.

## Evaluating Unsupervised Models

Without labels, evaluation is harder.

- **Internal metrics** such as silhouette score and inertia measure cluster quality from the data alone.
- **External metrics** such as the adjusted Rand index compare clusters with known labels, when some exist.
- **Usefulness** is often the real test: do the customer segments lead to better marketing results?

## Summary

- Unsupervised learning finds structure without labels.
- k-means assigns points to the nearest centroid and updates centroids until stable; choose k with the elbow method or silhouette score.
- Hierarchical clustering builds a dendrogram using a linkage rule; DBSCAN finds dense regions of any shape and labels noise.
- Dimensionality reduction helps visualisation, speed and noise reduction.
- PCA finds uncorrelated directions of maximum variance; keep enough components to explain most of the variance.
- t-SNE and UMAP are for visualisation, not general feature engineering.

## Practice Questions

1. Walk through two iterations of k-means on a small example of your own.
2. What does the elbow in an elbow plot represent?
3. When would DBSCAN be a better choice than k-means?
4. Why must features be standardised before applying PCA?
5. A PCA shows the first two components explain 92 percent of the variance. What does that mean in plain words?
