# Performance Experiment - Pyomo vs JuMP
This repository tries to make a fair comparision between the performance of Pyomo and JuMP. Performance is measures in model generation time and model generation plus solve time. 

## Example IJKLM
### Model
$$min \ z$$

$$\sum_{(j,k):(i,j,k) \in \mathcal{IJK}} \ \sum_{l:(j,k,l) \in \mathcal{JKL}} \ \sum_{m:(k,l,m) \in \mathcal{KLM}} x_{i,j,k,l,m} \ge 0 \hspace{1cm} \forall \ i \in \mathcal{I}$$

$$x_{i,j,k,l,m} \ge 0 \hspace{1cm} \forall \ (i,j,k) \in \mathcal{IJK}, l:(j,k,l) \in \mathcal{JKL}, m:(k,l,m) \in \mathcal{KLM} $$

### Model Generation Performance
![Alt text](plots/IJKLM/model_performance.png)

### Model Generation + Solve Performance
![Alt text](plots/IJKLM/solve_performance.png)