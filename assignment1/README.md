# Epidemiological Model Assignment — Parameter Exploration

**Course**: KEN3170 — Multi-scale modeling of biological systems  
**Group number**: 4

---

## 1. Repository overview

- `analysis.ipynb` — main notebook containing all required sections (Setup, Part 1–3, Conclusions)
- `requirements.txt` — Python dependencies (`numpy`, `matplotlib`, `pandas`, `scipy`, `seaborn`)
- `README.md` — this file

### How to run

```bash
pip install -r requirements.txt
```

Then open `analysis.ipynb` and run all cells from top to bottom.

---

## 2. Part 1 — Parameter analysis function

**Function**: `analyze_recovery_rates(beta, mu, N, I0, simulation_days)`

The function analyzes how different recovery rates (`gamma`) affect the spread and outcome of an epidemic using the SIRD model. Five recovery rates are tested:

```python
gamma_values = [0.05, 0.10, 0.15, 0.20, 0.25]
```

For each recovery rate, the SIRD differential equations are solved over the specified simulation period using `odeint()`.

The function records:

- the basic reproduction number `R0 = beta / gamma`, as specified in the assignment
- the maximum number of infected individuals
- the day on which infections reach their peak
- the epidemic duration
- the total number of deaths at the end of the simulation

Epidemic duration is defined as the first day after the epidemic peak at which fewer than one infected individual remains in the deterministic model.

Infection curves are stored during the simulations and can be visualized using the returned `plot_curves()` function.

The output DataFrame contains the following columns:

```text
gamma, R0, peak_infected, peak_day, epidemic_duration, total_deaths
```

Peak infections and total deaths are rounded to integer values.

The function returns:

```python
results_df, plot_curves
```

where `results_df` contains the parameter-analysis results and `plot_curves()` plots the number of infected individuals over time for each recovery rate.

---

## 3. Part 2 — Scenario comparison

Two scenarios are compared using the same population size (`N = 1000`), initial number of infected individuals (`I0 = 5`), and simulation period of 200 days.

### Scenario A — High Transmission

Parameters:

```text
beta = 0.4
mu = 0.02
```

| gamma | R0 | peak_infected | peak_day | epidemic_duration | total_deaths |
|------:|---:|--------------:|---------:|------------------:|-------------:|
| 0.05 | 8.000000 | 521 | 21 | 118 | 285 |
| 0.10 | 4.000000 | 340 | 22 | 86 | 160 |
| 0.15 | 2.666667 | 213 | 24 | 77 | 103 |
| 0.20 | 2.000000 | 124 | 27 | 78 | 67 |
| 0.25 | 1.600000 | 63 | 30 | 84 | 43 |

### Scenario B — Low Transmission

Parameters:

```text
beta = 0.2
mu = 0.005
```

| gamma | R0 | peak_infected | peak_day | epidemic_duration | total_deaths |
|------:|---:|--------------:|---------:|------------------:|-------------:|
| 0.05 | 4.000000 | 371 | 44 | 178 | 88 |
| 0.10 | 2.000000 | 139 | 52 | 154 | 37 |
| 0.15 | 1.333333 | 31 | 67 | 185 | 14 |
| 0.20 | 1.000000 | 5 | 0 | 116 | 2 |
| 0.25 | 0.800000 | 5 | 0 | 28 | 0 |

### Public-health comparison

Scenario A poses the greater overall threat to public health. It combines a higher transmission rate with a higher mortality rate, which leads to larger and earlier epidemic peaks and substantially more deaths across all tested recovery rates.

For example, at `gamma = 0.05`, Scenario A reaches a peak of 521 infected individuals on day 21 and produces 285 deaths. Under the same recovery rate, Scenario B peaks at 371 infected individuals on day 44 and produces 88 deaths.

The assignment-defined basic reproduction number remains higher in Scenario A for every tested recovery rate because its transmission rate is twice as high. At sufficiently high recovery rates in Scenario B (`gamma = 0.20` and `0.25`), the initial five infected individuals are already the maximum number of infected individuals, indicating that the infected population begins to decline immediately rather than developing into a growing epidemic.

---

## 4. Part 3 — Policy recommendations

### 4.1 Parameter impact analysis

Increasing the recovery rate has a strong beneficial effect on epidemic severity in both scenarios. A higher recovery rate means that infected individuals leave the infected compartment more quickly, reducing both the time available to transmit the disease and the time during which they remain at risk of death.

In Scenario A, increasing `gamma` from 0.05 to 0.25 reduces the peak number of infected individuals from 521 to 63, a reduction of approximately 87.9%. Over the same range, total deaths decrease from 285 to 43, corresponding to a reduction of approximately 84.9%.

Scenario B shows the same overall pattern. At `gamma = 0.05`, the epidemic reaches a peak of 371 infected individuals and produces 88 deaths. At `gamma = 0.10`, the peak falls to 139 infected individuals and deaths fall to 37. At `gamma = 0.15`, only 31 individuals are infected at the peak and 14 deaths occur. At `gamma = 0.20` and `0.25`, the maximum number of infected individuals remains equal to the initial five infected individuals.

The effect on epidemic duration is more complex. In Scenario A, epidemic duration decreases from 118 days at `gamma = 0.05` to 77 days at `gamma = 0.15`, but then rises slightly to 78 and 84 days at `gamma = 0.20` and `0.25`. In Scenario B, the duration is also non-monotonic: 178, 154, 185, 116, and 28 days across the five recovery rates.

Therefore, increasing the recovery rate consistently reduces peak infections and total deaths, but it does not necessarily reduce epidemic duration in a strictly linear or monotonic way.

### 4.2 Intervention analysis

To estimate the effect of an intervention that increases the recovery rate by 50%, Scenario A with `gamma = 0.10` is used as the baseline.

A 50% increase gives:

```text
gamma_intervention = 0.10 × 1.50 = 0.15
```

At `gamma = 0.10`, Scenario A produces 160 total deaths. At `gamma = 0.15`, total deaths decrease to 103.

The absolute reduction is:

```text
160 - 103 = 57 fewer deaths
```

The relative reduction is:

```text
(57 / 160) × 100 ≈ 35.6%
```

According to the model, a 50% increase in recovery rate therefore reduces total deaths by approximately 35.6% under these Scenario A conditions.

### 4.3 Real-world application

One real medical intervention that can be related to an increased recovery rate is Paxlovid, an antiviral treatment used for COVID-19.

Paxlovid inhibits a SARS-CoV-2 protease that is required for viral replication. By reducing viral replication, it can help the body control the infection and reduce disease severity.

In a simplified SIRD model, its effect could be represented by a modest increase in the recovery rate (`gamma`). Its strongest demonstrated clinical effect is the reduction of severe disease, hospitalization, and death, so a more realistic SIRD representation would also include a reduction in the mortality rate (`mu`).

A small-to-moderate increase in `gamma`, for example around 5–10%, can be used as an illustrative modeling assumption rather than as a directly measured clinical effect. Early clinical trials in high-risk unvaccinated patients showed a much stronger reduction in hospitalization or death, of approximately 85–90%, which should not be interpreted as an 85–90% increase in the recovery-rate parameter.

---

## 5. Conclusions

Increasing the recovery rate substantially reduces peak infections and total deaths in both SIRD scenarios. Scenario A consistently produces worse public-health outcomes because of its higher transmission and mortality rates.

A 50% increase in the recovery rate from 0.10 to 0.15 reduces total deaths in Scenario A from 160 to 103, corresponding to a reduction of approximately 35.6%.

Epidemic duration shows a more complex, non-linear relationship with recovery rate, demonstrating that reductions in epidemic severity do not necessarily correspond to proportional reductions in epidemic duration.
