# Performance Experiment - Pyomo vs JuMP

This repository tries to make a fair comparison between the performance of Pyomo and JuMP. Performance is measured in model generation time and model generation plus solve time.

- Python 3.11.3
- Pyomo 6.6.0
- Julia 1.9.0
- JuMP 1.11.1

## Example IJKLM

### Model

$$\text{min} \ z = 1$$

$$\sum_{(j,k):(i,j,k) \in \mathcal{IJK}} \ \sum_{l:(j,k,l) \in \mathcal{JKL}} \ \sum_{m:(k,l,m) \in \mathcal{KLM}} x_{i,j,k,l,m} \ge 0 \hspace{1cm} \forall \ i \in \mathcal{I}$$

$$x_{i,j,k,l,m} \ge 0 \hspace{1cm} \forall \ (i,j,k) \in \mathcal{IJK}, l:(j,k,l) \in \mathcal{JKL}, m:(k,l,m) \in \mathcal{KLM} $$

### Model Generation Performance

![Alt text](plots/IJKLM/model_performance.png)

### Model Generation + Solve Performance

![Alt text](plots/IJKLM/solve_performance.png)

## Example Supply Chain

### Model

$$\min F = 1$$

$$\sum_{j:(i,j) \in \mathcal{IJ} \ \land \ (j,k) \in \mathcal{JK}} x_{ijk} \ge \sum_{l:(k,l) \in \mathcal{KL}} y_{ikl} \hspace{1cm} \forall \ (i,k) \in \mathcal{IK} $$

$$\sum_{k:(k,l) \in \mathcal{KL}} y_{ikl} \ge \sum_{m:(l,m) \in \mathcal{LM}} z_{ilm} \hspace{1cm} \forall \ i \in \mathcal{I}, l \in \mathcal{L} $$

$$\sum_{l:(l,m) \in \mathcal{LM}} z_{ilm} \ge d_{im} \hspace{1cm} \forall \ i \in \mathcal{I}, m \in \mathcal{M} $$

| Sets                |             |
| ------------------- | --------    |
| $i \in \mathcal{I}$ | products    |
| $j \in \mathcal{J}$ | machines    |
| $k \in \mathcal{K}$ | production plants   |
| $l \in \mathcal{L}$ | distribution centers |
| $m \in \mathcal{M}$ | customers |
| $\mathcal{IJ}$ | set of products $i$ that can be processed by machine $j$ |
| $\mathcal{JK}$ | set of machines $j$ that are available at plant $k$ |
| $\mathcal{IK}$ | set of plants $k$ able to produce product $i$ |
| $\mathcal{KL}$ | set of plant $k$ that can ship products to distribution center $l$ |
| $\mathcal{LM}$ | set of distribution centers $l$ able to supply customer $m$ |


| Parameters | |
| ------------------- | --------    |
| $d_{im}$ | demand for product $i$ related to customer $m$ |

| Variables | |
| ------------------- | --------    |
| $x_{ijk}$ | production quantity of product $i$ on machine $j$ and plant $k$ |
| $y_{ikl}$ | shipping quantity of product $i$ from plant $k$ to distribution center $l$ |
| $z_{ilm}$ | delivery quantity of product $i$ from distribution center $l$ to customer $m$ |

### Model Generation Performance

![Alt text](plots/supply_chain/model_performance.png)

### Model Generation + Solve Performance

![Alt text](plots/supply_chain/solve_performance.png)
