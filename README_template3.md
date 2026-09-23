# Network Biology Assignment 

**Course**: KEN3170 — Multi-scale modeling of biological systems
**Group number**: [4]

---

## 1. Repository overview
- `analysis.ipynb` — main notebook containing all required sections (Setup, Part 1–3, Conclusions)
- `requirements.txt` — Python dependencies (numpy, matplotlib, pandas, scipy, seaborn)
- `README.md` — this file

**How to run**: [e.g. `pip install -r requirements.txt` then open and run `analysis.ipynb` top to bottom]

---

## 2. The setup

In this lab we model a simplified cell regulatory network using a Boolean network. Each biological component is represented as either 0 = OFF / inactive or 1 = ON / active. The basic structure of the model and helper class to create networks have been taken over from the practival. The model contains eight nodes: DNA_damage – presence or absence of DNA damage, p53 – tumor suppressor involved in the DNA-damage response, p21 – cell-cycle inhibitor activated by p53, MYC – oncogene that promotes cell growth, CDK2 – promotes cell-cycle progression, MDM2 – inhibits p53, Growth – continued cell proliferation, Death – activation of cell death.

### 2.1 Normal Boolean Rules

DNA_damage = INPUT (constant)
p21 = p53
MYC = (NOT p53) AND (NOT p21)
CDK2 = MYC AND (NOT p21) AND (NOT p53)
MDM2 = MYC
p53 = DNA_damage AND (NOT MDM2)
Growth = CDK2 AND MYC AND (NOT p53)
Death = p53 AND DNA_damage AND (NOT Growth)

These rules are simplified representations of biological regulation and are intended for educational modeling rather than detailed biological prediction.

### 2.2 Mutations Tested

**Mutation A** – p53 Knockout. The p53 tumor suppressor is permanently disabled.

network.add_rule( 'p53',lambda s: False,"p53 = BROKEN (always OFF)")

**Mutation B** – MYC Amplification. MYC is permanently active.

network.add_rule('MYC',lambda s: True,"MYC = AMPLIFIED (always ON)")

**Mutation C** – MDM2 Overexpression. MDM2 is permanently active.

network.add_rule('MDM2',lambda s: True,"MDM2 = OVEREXPRESSED (always ON)")

**Mutation D** – p21 Knockout. p21 is permanently disabled.

network.add_rule('p21', lambda s: False,"p21 = KNOCKOUT (always OFF)")

### 2.3. Scenarios

Each network is tested under three starting conditions.

1. Healthy Cell: DNA_damage = 0

2. Stressed Cell: DNA_damage = 1

This scenario tests whether the protective p53 pathway can stop growth or activate death.

3. Oncogene Hijacked Cell: MYC = 1, DNA_damage = 0



### 2.4. Simulation Method

We have taken over the simulation mechanics from the practical. The only significant change is that for mutated networks, the mutated node is set to its mutation-consistent value from time step 0. This means we modify accordingly scenario conditions at step 0. For example, in the MYC-amplified network, in a Healthy Cell scenario, the MYC at step 0 will be set to 1.


A steady state is detected when two consecutive states are identical:

if len(self.history) >= 2 and self.history[-1] == self.history[-2]:

### 2.5. Attractor Analysis

Like in practical, for each network version, all possible initial states are tested (8 Boolean nodes →2^8 = 256 states tested).
Each of the 256 states is simulated using the provided simulate() method. As mentioned, a state is counted as a steady-state attractor when: np.array_equal(trajectory[-1], trajectory[-2]).

Duplicate attractors are removed so that only unique steady states are reported.

### 2.6. Basin of Attraction

The basin size of an attractor is the number of starting states that eventually reach that attractor.

For example:

Basin Size = 128 states
Basin % = 50.0%

means that 128 out of the 256 possible initial states reach that attractor.

### 2.7. Visualizations

Following the practical, the code produces:

- Scenario heatmaps for all five networks and all three scenarios

- Attractor heatmaps

- Basin-size pie charts and bar charts

- A final attractor summary table


## 3. Main Results

### 3.1. Scenario Comparison

The three starting scenarios show how the network behaves under different biological conditions.

**Healthy Cell**

In the healthy-cell scenario, DNA_damage = 0. The normal network and all mutated networks eventually reach a proliferating state with 
Growth ON, Death OFF, p53 OFF. This means that, without DNA damage, the cell is allowed to continue growing. The mutations have relatively little visible effect in this scenario because the protective DNA-damage response is not needed.

**Stressed Cell*

In the stressed-cell scenario, DNA_damage = 1. This scenario shows the clearest differences between the normal and mutated networks. In  the normal network, DNA damage activates p53 and p21. Growth is stopped and Death becomes active, showing a protective response to damage. With p53 knockout, p53 stays OFF at every time step. The cell is therefore not able to activate the normal protective response and eventually reaches Growth ON and Death OFF despite DNA damage.

MYC amplification and MDM2 overexpression also lead to continued growth under DNA-damage conditions. They both affect the p53 pathway indirectly and therefore produce a similar final outcome.

The p21 knockout behaves differently. p53 can still respond to DNA damage, but the network shows repeated changes in several nodes rather than a simple stable response in all cases.

**Oncogene Hijacked Cell**

In the oncogene-hijacked scenario, MYC starts active while DNA_damage = 0. In all network versions, MYC activity promotes MDM2 and CDK2, leading to Growth ON while Death stays OFF. This shows that the oncogenic starting condition strongly favors proliferation when no DNA-damage signal is present.

Overall, the stressed-cell scenario is the most informative because it reveals whether each network can still use the p53 pathway to respond to DNA damage.

### 3.2. Attractor analysis

**Normal network**

The normal network produces three steady-state attractors: Proliferation without DNA damage, Cell death following DNA damage and Damaged proliferation. The protective cell-death attractor has a basin of: 120 / 256 states = 46.9%. The cancer-like damaged-proliferation attractor has a basin of 8 / 256 states = 3.1%.

**p53 Knockout network**

The p53 knockout removes the protective death attractor. The damaged-proliferation basin increases to 128 / 256 states = 50.0%. It is a huge increase in comparison to the normal network (from 3.1% to 50%). This is a 16-fold increase in the number of states leading to growth despite DNA damage.

**3.3. MYC Amplification network**

MYC amplification produces the same final steady-state attractor distribution as p53 knockout.The damaged-proliferation attractor reaches 128 / 256 states = 50.0%. 

**3.4. MDM2 Overexpression**

MDM2 overexpression also removes the stable protective death attractor and produces 128 / 256 states = 50.0% for damaged proliferation.

**p21 Knockout network- important limitaion**

The detected steady-state basins are:

Proliferating state:               128 states
Cell death state:                   24 states
Cancer-like damaged proliferation:   8 states

Note, that 96 / 256 states = 37.5% are not classified as steady-state attractors by the provided method. We adopted the attractor method from practical, whoch means that we can only recognize stable attractors when the last two states are identical. As a result, cycles are not detected. It has little consequences for the three given mutations, but p21 knockout seems to display cycling behavior (see heatmaps for stressed cell). This is an important limitation in our analysis.

## 4. Questions

### 4.1. (Q1) Which mutation is most dangerous and why? Give quantitative evidence.

Based on our results, p53 knockout, MYC amplification and MDM2 overexpression  produce the same final attractor percentages: 50% of states lead to damaged proliferation . More specifficaly, in the normal network, only 8 out of 256 states (3.1%) end in the cancer-like state where the cell grows despite DNA damage. With the three beforementioned mutations, this increases to 128 out of 256 states (50%), while the protective 46.9% cell-death attractor disappears. This is a 16-fold increase. In that sense, those three mutations seem to be equally dangereous.

However, we have to mention that p53 knockout provides the most direct loss of protection because p53 is never active at all. To compare, in the MYC and MDM2 mutations, the p53 pathway is disrupted indirectly. From this point of view,  p53 knockout stands out, causing the cell to completely lose its p53 response from the very beginning of the simulation. In the stressed-cell simulation, DNA damage stays ON, but p53 stays OFF at every time step. Because p53 cannot respond, the cell does not activate the normal protective pathway properly. Growth eventually becomes ON while Death stays OFF, meaning the damaged cell continues to grow.

---

### 4.2. (Q2) What is the role of feedback loops such as MYC → MDM2 → p53?

Feedback loops help control whether a cell keeps growing or stops when DNA damage is present. One important pathway in this network is:
MYC → MDM2 → blocks p53. When MYC is active, MDM2 is activated. MDM2 then blocks p53. The blockade of p53 reduces p21,which allows CDK2 and MYC to stay active. This promotes cell growth.

In the normal stressed cell we see the opposite protective response. DNA damage activates p53, which activates p21. p21 helps stop MYC and CDK2, so Growth remains OFF. In this model, p53 also helps turn Death ON.

Our results show how the this system is broken by the mutations in different ways. The p53 knockout removes p53 completely. MYC amplification keeps MYC permanently ON, which supports MDM2 activity and suppresses p53. MDM2 overexpression keeps MDM2 permanently ON, again preventing a strong p53 response. This explains why three different mutations can lead to a very similar final result: the damaged cell keeps growing instead of being stopped or removed.

---

## 4.3. (Q3) What are three limitations of this Boolean network model?
1. A Boolean model only uses ON and OFF states

Each gene or protein can only be 0 or 1. In case of simulating overexpression or amplification, this becomes problematic. For instance, 
MYC could be slightly increased or extremely overexpressed, but this model treats both cases simply as MYC = 1. Therefore, the model cannot represent different strengths of gene activity/mutations.

2. The changes at certain time t happen simultaneously

At every time step, all nodes are updated at the same time. In real cells, different processes happen at different speeds. Some proteins respond quickly, while others take longer to be produced or broken down.


3. The network and attractor detection are simplified

The model contains only eight nodes- incomparable to the multitude of genes, proteins and important pathways in a real cell. Moreover, real cells also include randomness, in the sense that two cells with the same mutation may not behave in exactly the same way. Our model does not include such random effects.



---

## 5. Conclusions 

In this lab we showed how mutations in the p53–MYC–MDM2–p21 system can affect the cell. While the normal network can respond to DNA damage by activating p53, stopping growth, and activating cell death, p53 knockout, MYC amplification, and MDM2 overexpression strongly lead to continued growth under DNA-damage conditions. It has been also shown that some mutations can affect important pathways indirectly, leading in the long term to the same steady states as a direct mutation.
.