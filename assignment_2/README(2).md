# E. coli Core Model Assignment — Enzyme Activity-Constrained FBA

**Course**: KEN3170 — Multi-scale modeling of biological systems
**Group number**: [2]

---

## 1. Repository overview
- `assignment_2.ipynb` — main analysis notebook
- `e_coli_core-1.json` — *E. coli* core COBRA model
- `KEN3170_Assignment_2026_e_coli_core_expression.csv` — maximal reaction activity data
- `requirements.txt` — Python dependencies (numpy, matplotlib, pandas, scipy, seaborn)
- `README.md` — this file

**How to run**: 
place the notebook, model JSON file and reaction activity CSV file in the same directory.
Then `pip install -r requirements.txt` then open and run `assignment_2.ipynb` top to bottom.

---

## 2. Objective
- This assignment uses the *E. coli* core metabolic model in COBRApy to study how maximal reaction activities constrain metabolic fluxes and biomass production.

In the notebook we perform the following tasks:

- Load the *E. coli* core metabolic model.
- Import maximal reaction activity data from a CSV file.
- Apply these activities as reaction-specific flux bounds:
  - reversible reactions receive bounds of `-Vmax` to `+Vmax`;
  - irreversible reactions receive bounds of `0` to `+Vmax`;
  - reactions without activity data retain their original bounds;
  - the ATP maintenance reaction (`ATPM`) keeps its original lower bound;
  - the glucose exchange reaction (`EX_glc__D_e`) is initially restored to the large default exchange bounds.
- Run Flux Balance Analysis (FBA) with biomass production as the objective.
- Study how limiting glucose uptake affects the maximal biomass production rate.
- Modify the glucose uptake bound from 1 to 15 mmol/gDW/h in increments of 0.1 and plot the resulting biomass production rate.
- Inspect exchange fluxes to identify the metabolic process associated with the second segment of the biomass-vs-glucose curve.
- Visualize acetate secretion (`EX_ac_e`) together with biomass production.

---

## 3. Results

## Part 1: Loading and interpretation of maximal reaction activity data

- We load maximal reaction activities into the Escher map.

- We distinguish maximal reaction activities from actual steady-state fluxes. **Maximal reaction activities** inform about independently measured or estimated capacities of reactions. They do not have to be equal along a linear pathway. In contrast, actual **steady-state fluxes** are constrained by mass balance.

- Some reactions in the Escher map are gray and have two possible labels: **0.00** means that a maximal activity value is present in the dataset and is zero, or is displayed as zero at the shown precision. **nd** means that no maximal activity value is available for that reaction. This does not imply that its true maximal activity is zero.

## Part 2: Setting the activity values in the activity-constrained model

- The activity values are implemented as flux bounds in the E. coli core model: reversible reactions receive bounds from *-Vmax* to *+Vmax*; irreversible reactions receive bounds from *0* to *+Vmax*. Reactions without activity data keep their original model constraints.
The lower bound of ATPM is preserved because it represents the cellular ATP maintenance requirement.

- The glucose exchange reaction EX_glc__D_e is initially reset to the high default exchange bounds of -1000 and 1000 mmol/gDW/h.

- The resulting lower and upper bounds for all reactions are printed in the notebook for inspection.

## Part 3: FBA and glucose uptake limitation

- We perform FBA with biomass production as the model objective.

- With the maximal reaction activity constraints implemented, we obtained the maximal biomass production rate of 0.8732862458582367 h^-1

- The glucose exchange reaction is then constrained to a maximum uptake rate of 5 mmol/gDW/h by setting: gluc_ex.lower_bound = -5.  In COBRApy, uptake through an exchange reaction is represented by negative flux. Therefore, a lower bound of -5 means that the cell can take up at most 5 mmol/gDW/h of glucose. The upper bound remains large, so glucose secretion is effectively unrestricted by this bound.

- This glucose constraint differs from the expression-based constraints applied to intracellular reactions. The intracellular constraints represent limits due to maximal enzyme/reaction activity, whereas the glucose exchange constraint represents a limit on substrate uptake from the environment.

- With the glucose uptake limit imposed, the maximal biomass production rate becomes 0.41559777509290663 h^-1, which is a decrease of approximately 52.4%. The result indicates that glucose availability becomes limiting under this condition.

## Part 4: Biomass production as a function of glucose uptake

- The glucose uptake bound is varied from 1 to 15 mmol/gDW/h in increments of 0.1 mmol/gDW/h. For each uptake limit, FBA is performed and the maximal biomass production rate is recorded.

- The resulting curve contains three distinct regions. At lower glucose uptake limits, biomass production increases approximately linearly because glucose is limiting. Around 9.3–9.4 mmol/gDW/h, the slope changes and a second segment appears. At higher uptake limits, the biomass production rate approaches a plateau of approximately: 0.8732862458582383 h^-1. Beyond roughly 11 mmol/gDW/h, increasing the allowed glucose uptake no longer increases biomass production. At that point, glucose is no longer the limiting factor and other model constraints, including the imposed maximal reaction activity constraints, determine the maximal growth rate.

- Inspection of the exchange reaction fluxes shows that acetate secretion becomes active in the second segment. The relevant reaction is:
EX_ac_e. In the notebook, EX_ac_e becomes positive at approximately 9.4 mmol/gDW/h glucose uptake, increases through the second segment, and then stabilizes at about 2.5 mmol/gDW/h. Biomass production and acetate secretion are plotted together to visualize this transition.

## 4. Conclusions

The assignment shows how experimentally derived maximal reaction activities can be incorporated into a constraint-based metabolic model. These activity values restrict the feasible flux space without directly specifying the actual metabolic fluxes.

FBA shows that predicted growth depends on both intracellular reaction capacity and nutrient availability represented by exchange reactions. At low glucose uptake, growth is glucose-limited. As more glucose becomes available, biomass production increases until other metabolic constraints become limiting. The activation of acetate secretion in the intermediate region illustrates how the optimal metabolic strategy changes as glucose availability increases.

