# Assignment 4: Auditory Models and Brain Representational Similarity Analysis

## Overview

This project investigates how different neural-network architectures represent natural sounds and how similar those representations are to human auditory-cortex responses.

The workflow has two main parts:

1. **Sound-event recognition**  
   Several neural networks are trained on the ESC-50 environmental sound dataset.

2. **Brain-alignment analysis**  
   The trained models are presented with the 288 natural sounds from the Santoro fMRI dataset. Internal model activations are extracted and compared with superior temporal gyrus (STG) brain responses using Representational Similarity Analysis (RSA).

The project includes four custom model types:

- `WaveformModel`
- `UninspiredModel`
- `InspiredModel`
- `CorticalCRNN`

It also uses pretrained **YAMNet** activations as an external reference model.

---

## Project structure

The main files are:
config.py
core.py
models.py
train.py
util.py
assignment4.ipynb
data/
models/

The findings are extensively discussed in the notebook and in the Report.pdf file

## Models

### WaveformModel

A simple fully connected network operating directly on the raw 1-second waveform.

It contains five hidden linear layers with `tanh` activations followed by a classifier.

This model serves as a basic baseline.

### UninspiredModel

A convolutional model operating on mel spectrograms.

It contains:

- three convolutional layers
- max pooling
- `tanh` activations
- two fully connected layers
- a final classifier

This model is more suitable for sound input than the waveform baseline, but is not designed around a biological interpretation.

### InspiredModel

A convolutional-recurrent neural network.

It contains:

- three convolutional layers
- ReLU6 activations
- pooling
- a two-layer GRU
- a classifier

The convolutional layers extract local time-frequency features, while the recurrent stage combines information across time.

### CorticalCRNN

The custom CorticalCRNN is a biologically inspired convolutional-recurrent model.

Its main stages are:

mel spectrogram
      ↓
core_conv
      ↓
belt_conv
      ↓
parabelt_conv
      ↓
stg_rnn
      ↓
classifier

There are important diferrences between corticanCRNN and inspiried model: In InspiredModel, the  three convolutional layers all use the same 3×3 kernel size, the same max-pooling strategy, and then a two-layer GRU with hidden size 128. It is “inspired” mainly because it follows a sensible auditory-processing hierarchy: local spectrotemporal feature extraction followed by temporal integration. 

The CorticalCRNN is more specialized: 

- CorticalCRNN explicitly maps stages to core, belt, parabelt, and STG, while InspiredModel uses generic convolutional and recurrent layers. 
- CorticalCRNN uses (5,3), (5,5), and (3,7) kernels, so deeper stages look across different frequency/time ranges. InspiredModel uses 3×3 throughout. 
- CorticalCRNN preserves the time dimension more strongly, using (2,1), (2,2), (2,1) pooling. InspiredModel uses ordinary 2×2 pooling after every convolution.
- In CorticalCRNN, we add Dropout(0.2) after each convolutional stage. InspiredModel does not.
- InspiredModel uses a 2-layer GRU, whereas CorticalCRNN uses a single-layer GRU.

---

## Data requirements

### ESC-50

During training, each 5-second ESC-50 recording is resampled to 8 kHz and a random 1-second section is selected.

The random crop acts as simple data augmentation and also makes the training examples the same duration as the Santoro sounds.

### Santoro fMRI dataset

The project expects the Santoro sound files under: data/santoro_sounds/

and the label file: data/santoro_sounds/Labels_288Sounds_ObjectSoundDescription.csv

The dataset contains 288 sounds together with STG fMRI response patterns

### YAMNet activations

Precomputed YAMNet embeddings are expected under: data/yamnet_embeddings/
These activations are used as a pretrained reference in the RSA analysis.

---

## Installation

The project requires Python together with common scientific and deep-learning packages.

Typical dependencies include:

torch
torchaudio
numpy
scipy
pandas
matplotlib
scikit-learn
h5py
soundfile

A simple installation command is: pip install torch torchaudio numpy scipy pandas matplotlib scikit-learn h5py soundfile


---

## Training

Run commands from the project directory containing `train.py`.

### Train one model

For example, to train the CorticalCRNN:


python train.py --models cortical_crnn


This uses the defaults from `config.py`.

### Train several independent copies

The analysis uses multiple runs to estimate variability between independently trained networks.

For five CorticalCRNN runs: python train.py --models cortical_crnn --n-models 5


## Saved checkpoints

In practice, we explicitly train only CorticalCRNN on ESC-50. The other models (waveform, uninspired, and inspired) already have saved checkpoint files for several runs in the models/ directory, and the analysis code loads those weights rather than retraining them. The `*_best.pt` file contains the weights from the epoch with the highest validation accuracy. If checkpoint epochs are requested, the training code also saves the initial untrained weights. Saving the untrained checkpoint is useful when the analysis should compare each trained network with its exact initial state.



## Brain-alignment analysis

After training, the models are not trained further on the Santoro dataset. Instead, the 288 Santoro sounds are passed through each trained model and the internal activation patterns are recorded. This produces representations for each layer. These representations are then compared with the STG brain responses.


## Representational Dissimilarity Matrices

Brain responses and neural-network activations have different numbers of features, so they cannot be compared directly.
Instead, each representation is converted into a **Representational Dissimilarity Matrix (RDM)**.

For each layer:

1. each of the 288 sounds is represented by its activation pattern;
2. correlation distance is calculated between every pair of sounds;
3. the result is a `288 × 288` RDM.

Small RDM values mean two sounds have similar representations. Large values mean their representations are more different.

---

## Representational Similarity Analysis

RSA compares the model RDM with the STG RDM. The analysis uses several comparison measures: **Spearman correlation**, **Pearson correlation** and **Kendall's tau-b**. Using several measures helps check whether the overall conclusions depend strongly on the exact RSA metric. The RSA scores are generally small, so they are mainly interpreted as relative measures of alignment between models, layers, and training conditions rather than as evidence that a model fully reproduces STG processing.

---

## Multiple runs and confidence intervals

Neural-network training contains random elements such as weight initialization and minibatch ordering. A single trained network may not represent the typical behavior of an architecture.The project uses several independent runs. Each run is analyzed separately first. For example, RSA is calculated separately for a given layer in all five runs. The five values are then summarized using mean ± 95% confidence interval.

The independent model runs are treated as the repeated observations, rather than treating different layers of the same network as independent samples.

YAMNet has only one pretrained instance in this project, so no across-run confidence interval is calculated for YAMNet.

---

## Training effect

The analysis also asks whether ESC-50 training changes brain alignment. For each model and layer: training effect = trained RSA - untrained RSA. A positive value means training increased similarity to the STG representation. A negative value means alignment decreased after training. This analysis is performed per run before results are averaged across runs.

---

## Layer depth

The models contain different numbers of layers. To compare changes across depth, layer positions are scaled from: 0 = first analyzed layer to 1 = final analyzed layer. The analysis then examines whether STG alignment tends to increase or decrease as representations move deeper through the model.

---

## Category-separation analysis

The project also examines whether sounds with the same sound-source label are represented close together. Category organization is measured with the **silhouette score** using each layer's RDM. A higher silhouette score indicates clearer grouping of sounds with the same label. Silhouette analysis essentialy asks: Does the model group sounds with the same label together?

A model can therefore have relatively clear category structure without closely matching the brain representation.

---

## t-SNE visualization

t-SNE is used as a qualitative visualization of the representation at different layers. Each point represents a sound and colors represent sound-source labels. The plots help show how the representation changes across the network, but they should not be treated as a quantitative measure of brain similarity. For models with several training runs, one representative run is shown rather than averaging t-SNE coordinates.

---

## Main observations

The analysis suggests several broad patterns.

The waveform model generally shows weak brain alignment and poor category separation after training.

The spectrogram-based models show more structured changes across depth.

The Inspired model and CorticalCRNN show stronger positive STG alignment in some intermediate and later stages.

For the CorticalCRNN in particular, ESC-50 training shifts the strongest STG alignment toward the `parabelt_conv` stage. Alignment then decreases again in the recurrent `stg_rnn` stage.

This suggests that training changes where brain-like representations appear in the network rather than simply improving every layer equally.

Category separation also tends to be strongest in early or intermediate convolutional stages and becomes weaker in later recurrent or fully connected stages.

YAMNet provides a useful pretrained comparison, but because only one pretrained YAMNet instance is available, its results are descriptive and do not have across-run confidence intervals.

Overall, no model closely reproduces the full STG representational geometry. The results are better interpreted as showing relative differences between architectures and processing stages.

---

## Reproducibility notes

A few details are especially important for obtaining valid results:

- Santoro dataset should not be shuffled during activation extraction.
- The same sound order has to be used for every model and for the brain RDM.
- The model runs have to be kept separately until run-level statistics have been calculated.
- The `*_best.pt` files are used for trained-model analysis.
- When confidence intervals are required, several independent runs must be used.
- T-SNE plots cannot be interpreted as direct statistical evidence.

---