# Bibliographic Study

*Section 4.1 of the internship subject: feed-ration prediction in intelligent
aquaculture, supervised regression, federated learning (FedAvg), and SMPC /
secret sharing applied to secure aggregation.*

## 1. Feed-ration prediction in intelligent aquaculture

Modern aquaculture increasingly relies on IoT sensor networks to monitor
water quality continuously instead of manual sampling. Field studies on
biofloc, recirculating-aquaculture and aquaponics systems consistently list
temperature, dissolved oxygen (DO), pH and turbidity as the most commonly
deployed sensor parameters, and report that continuous monitoring
measurably improves fish growth outcomes and reduces mortality [5].

Several projects go a step further and couple the sensor stream to a
machine-learning model that predicts a growth or water-quality outcome
directly from those readings. An ESP32-based edge system deployed on Thai
tilapia farms compared Multiple Linear Regression, Decision Tree Regression
and Random Forest Regression for real-time water-quality prediction, and
found Random Forest most accurate (R² > 0.80) while linear regression
remained the most practical choice for low-power, offline on-device
deployment [6]. A separate study on Nigerian catfish ponds trained Decision
Tree and XGBoost regressors directly on IoT pond sensor logs to predict fish
length and weight, and reported large accuracy gains once sensor data
quality was improved — the fish-length RMSE dropped from 1.01 to 0.61 and
the weight-prediction RMSE from 7.02 to 0.78 after upgrading the sensing
pipeline [5]. Automated-feeder studies separately confirm a strong,
near-linear relationship between a feeder's actuation and the resulting feed
mass delivered, with reported coefficients of determination above 90% [7],
supporting the general premise used in this project that feed quantity can
be modelled as a regression problem from a handful of measurable covariates.

**Gap this project addresses.** None of the datasets surveyed above publish
an actual "grams fed per fish" ground-truth label alongside raw sensor
readings — feed amount is normally metered separately (e.g. feeder actuation
time) or not published at all. The IoT-pond dataset used in this project
(11 real ponds, `dataset/*.csv`) is the same family of sensor-only data:
temperature, dissolved oxygen, pH, turbidity, ammonia, nitrate, fish length
and weight, with no feed column. Section 4.2 below, and `fl_smpc/data.py`,
detail how a feed-ration label was derived from these sensor readings via a
domain-expert feeding rule — consistent with how the literature above
treats feed/growth prediction as a downstream regression task on
water-quality and morphometric covariates.

## 2. Supervised Machine Learning for regression

Supervised regression learns a function `f(x) -> y` from labelled examples
by minimizing a loss between predicted and true values. This project
compares four regressor families spanning the standard bias/variance and
interpretability trade-offs used across the aquaculture-IoT literature
surveyed above:

- **Linear / Ridge Regression** — a linear model `y = w.x + b`; Ridge adds an
  L2 penalty (`+ alpha * ||w||^2`) to control overfitting and keep
  coefficients well-conditioned when input features are correlated (several
  engineered features in this project, e.g. `temp_x_do`, `turb_x_temp`, are
  deliberately correlated with their source features). Both are fully
  interpretable (one coefficient per feature) and are the model family used
  later for FedAvg, since federated averaging combines raw model
  *parameters* across clients — a comparison that is only meaningful for a
  parametric model with a fixed, shared parameter vector.
- **Random Forest** — an ensemble of decorrelated decision trees trained on
  bootstrap samples and random feature subsets, averaging their predictions.
  Captures non-linear, threshold-style relationships (e.g. "growth collapses
  below pH 6.5") that a linear model cannot, at the cost of a much larger,
  less directly interpretable parameter set.
- **Gradient Boosting / XGBoost** — an additive ensemble that fits each new
  tree to the residual error of the current ensemble, typically reaching the
  best raw accuracy of the four on tabular, structured data such as sensor
  logs, again at the cost of interpretability and of not being naturally
  compatible with parameter-averaging aggregation.

Evaluation follows the three metrics the subject requires: **MAE** (mean
absolute error, in the target's own unit — grams of feed here, robust to
outliers), **RMSE** (root mean squared error, penalizes large errors more
heavily), and **R²** (fraction of target variance explained, unit-free,
comparable across experiments). `fl_smpc/experiments/ml_models.py`
implements this comparison on the real dataset; results are summarized in
`fl_smpc/results/ml_comparison.json` and visualized on the dashboard's "ML
model leaderboard" page.

## 3. Federated Learning and FedAvg

Federated Learning (FL) trains a shared global model across many clients
that each hold their own private data, without those clients ever
transmitting their raw data to a central server. The foundational algorithm,
**Federated Averaging (FedAvg)**, was introduced by McMahan, Moore, Ramage,
Hampson and Agüera y Arcas in *"Communication-Efficient Learning of Deep
Networks from Decentralized Data"* (AISTATS 2017) [1]. Each communication
round proceeds in three steps: the server broadcasts the current global
model to a set of clients; each client runs several local gradient-descent
steps on its own data; the server aggregates the resulting client models by
a sample-size-weighted average, minimizing the weighted empirical risk
across clients, where each client's loss is weighted by the fraction of the
total data it holds. Concretely, this is the update rule implemented in
`fl_smpc/experiments/federated.py` and in
`aqua_smart/app/services/federated.py`:
`w_global = sum_k (n_k / N) * w_k`, where `w_k` is client `k`'s locally
trained parameters and `n_k` its number of samples. The method's main
practical appeal is communication efficiency: the original paper and
follow-up analyses report FedAvg reducing the number of communication rounds
needed by one to two orders of magnitude compared to synchronized stochastic
gradient descent [1] — exactly the trade-off measured in this project's
comparison table (communication cost in KB/messages vs. accuracy).
FedAvg's known limitation, also visible in this project's results, is
sensitivity to **non-IID data**: convergence guarantees weaken and empirical
accuracy can degrade when client data distributions differ substantially
from one client to another [4] — precisely the setting used here, 11 real
ponds with very different sizes (590 to 8,000+ rows) and sensor-value
distributions, rather than synthetic, near-identical clients.

## 4. SMPC and secret sharing applied to secure aggregation

Federated Learning alone still exposes each client's raw model update to
the aggregating server, which can leak information about a client's local
data distribution. **Secure Multi-Party Computation (SMPC)** is a family of
cryptographic protocols that let several parties jointly compute a function
over their private inputs (here: a sum of model updates) while revealing
only the output of that computation, never the individual inputs. The
classical theoretical basis is Shamir's **secret sharing** scheme [3]
(1979), which splits a secret into `n` shares such that any `k` of them
reconstruct it, but any fewer reveal nothing about it. Applied specifically
to federated learning, Bonawitz, Ivanov, Kreuter, Marcedone, McMahan, Patel,
Ramage, Segal and Seth's *"Practical Secure Aggregation for
Privacy-Preserving Machine Learning"* (ACM CCS 2017) [2] designs a protocol
in which a server computes the sum of many users' private data vectors
without learning any individual user's contribution, remaining secure even
if some users drop out mid-protocol — the same "secure aggregation" goal
this project's SMPC layer targets, using a simplified mechanism.

This project implements the subject's second suggested option — **additive
masking** rather than full Shamir secret sharing — because it achieves the
same core guarantee (the server only ever sees masked, individually
meaningless updates) with far less protocol complexity, at the cost of not
tolerating client dropout mid-round (a limitation Bonawitz et al.'s full
protocol solves, and one this project documents as future work in
`fl_smpc/README.md`). Concretely, `fl_smpc/experiments/smpc.py` has every
pair of clients `(i, j)` share a random mask vector `m_ij`; client `i` adds
`+m_ij` (scaled by its aggregation weight) to its update, client `j`
subtracts the same mask (scaled by its own weight). Individually, each
masked update is statistically indistinguishable from noise; summed across
all clients in the weighted FedAvg average, every pairwise mask cancels
exactly, so the server recovers the correct global model without ever
seeing a real individual update — verified empirically in this project's
results (FL and FL+SMPC converge to the same model to floating-point
precision, see `fl_smpc/results/comparison_results.json`).

## References

1. McMahan, H. B., Moore, E., Ramage, D., Hampson, S., & Agüera y Arcas, B.
   (2017). *Communication-Efficient Learning of Deep Networks from
   Decentralized Data.* AISTATS 2017. https://arxiv.org/abs/1602.05629
2. Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H. B.,
   Patel, S., Ramage, D., Segal, A., & Seth, K. (2017). *Practical Secure
   Aggregation for Privacy-Preserving Machine Learning.* ACM CCS 2017.
   https://eprint.iacr.org/2017/281
3. Shamir, A. (1979). *How to Share a Secret.* Communications of the ACM,
   22(11), 612-613.
4. Li, X., Huang, K., Yang, W., Wang, S., & Zhang, Z. (2019). *On the
   Convergence of FedAvg on Non-IID Data.* arXiv:1907.02189.
5. Improved IoT sensor system for aquaponics/catfish yield prediction.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10585617
6. *Machine Learning on Low-Cost Edge Devices for Real-Time Water Quality
   Prediction in Tilapia Aquaculture.*
   https://pmc.ncbi.nlm.nih.gov/articles/PMC12526668
7. Automatic fish feeder / water-quality monitoring regression study.
   https://sipora.polije.ac.id/57259/
