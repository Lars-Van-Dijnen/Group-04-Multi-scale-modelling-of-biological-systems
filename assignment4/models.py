"""Pre-implemented models of sound event recognition."""

import torch

from config import SAMPLE_RATE, SNIPPET_DURATION


class WaveformModel(torch.nn.Module):
    """ Super simple model that operates directly on raw waveforms: 5 fully connected layers with tanh activations,
    followed by a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        input_length = int(SAMPLE_RATE * SNIPPET_DURATION)
        hidden_sizes = (1024, 512, 256, 128, 64)

        self.flatten = torch.nn.Flatten()

        sizes = [input_length, *hidden_sizes]
        self.hidden_layers = torch.nn.ModuleList([
            torch.nn.Linear(sizes[i], sizes[i + 1]) for i in range(len(hidden_sizes))
        ])
        self.activation = torch.nn.Tanh()

        self.classifier = torch.nn.Linear(hidden_sizes[-1], num_classes)

    def forward(
            self,
            waveform: torch.Tensor
    ) -> torch.Tensor:
        x = self.flatten(waveform)
        for layer in self.hidden_layers:
            x = self.activation(layer(x))
        return self.classifier(x)


class UninspiredModel(torch.nn.Module):
    """ More complex but still uninspired model that now operates on spectrograms: 3 convolutional layers with
    tanh activations, followed by 2 fully connected layers and a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        fc_sizes = (64, 128, 64)

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.Tanh()

        self.fc_layers = torch.nn.ModuleList([
            torch.nn.Linear(fc_sizes[i], fc_sizes[i + 1]) for i in range(len(fc_sizes) - 1)
        ])

        self.classifier = torch.nn.Linear(fc_sizes[-1], num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))
        x = x.mean(dim=(-2, -1))
        for fc in self.fc_layers:
            x = self.activation(fc(x))
        return self.classifier(x)


class InspiredModel(torch.nn.Module):
    """ The most complex model, operating on spectrograms: 3 convolutional layers with ReLU6 activations extract local
    time-frequency features, 2 stacked recurrent (GRU) layers integrate information over time, and a linear classifier
    returns logits. Its conv -> recurrent structure loosely mirrors the auditory system's hierarchy of local
    spectrotemporal filtering followed by temporal integration.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        rnn_hidden_size = 128

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.ReLU6()

        self.rnn = torch.nn.GRU(
            input_size=conv_channels[-1], hidden_size=rnn_hidden_size, num_layers=2, batch_first=True,
        )

        self.classifier = torch.nn.Linear(rnn_hidden_size, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))

        x = x.mean(dim=2).transpose(1, 2)

        _, hidden = self.rnn(x)
        last_hidden = hidden[-1]

        return self.classifier(last_hidden)

import torch


class CorticalCRNN(torch.nn.Module):
    """Biologically inspired auditory CRNN (convolutional + recurrent network) 
    that operates on mel spectrograms. Approximate mapping: core_conv -> 
    primary/core auditory cortex; belt_conv -> auditory belt; parabelt_conv -> 
    parabelt / higher auditory cortex; stg_rnn -> recurrent temporal integration 
    in STG; classifier -> task-specific readout."""

    # The sound is first turned into a spectrogram, which then passes through a chain of 
    # stages that mimic the stages of the human auditory system in the brain:
    #   1. Core- picks up simple, small-scale patterns
    #   2. Belt- combines those into slightly bigger patterns 
    #   3. Parabelt- combines them again into complex, longer patterns
    #   4. STG (memory)- follows the sound over time, like a listener keeping track of what was just heard
    #   5. Classifier- makes the final decision: which category does this sound belong to?
    # -----------------------------------------------------------------
    def __init__(self, num_classes: int):
        super().__init__()

        # set audicotry core layer
        self.core_conv = torch.nn.Conv2d(in_channels=1, out_channels=16, kernel_size=(5, 3), padding=(2, 1))

        # set belt layer
        self.belt_conv = torch.nn.Conv2d(in_channels=16, out_channels=32, kernel_size=(5, 5), padding=(2, 2))

        #parabelt
        self.parabelt_conv = torch.nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(3, 7), padding=(1, 3))

        #ReLU6 gives no negative activity and caps the strength at 6, 
        # unlike ordinary ReLU, which has no upper cap. 
        # This keeps values in a sensible range, as neurons cannot fire infinitely strongly.
        
        self.activation = torch.nn.ReLU6()

        
        # POOLING: keep only the strongest signal in each small neighbourhood, 
        # so the model focuses on what matters and becomes less sensitive to tiny shifts.
        # The pooling windows are (frequency, time): the core and parabelt pools shrink only 
        # the pitch axis, while the belt pool shrinks both. 
        # Overall, time is preserved more strongly than pitch, because timing matters a lot in 
        # sound.
        
        self.core_pool = torch.nn.MaxPool2d(kernel_size=(2, 1))
        self.belt_pool = torch.nn.MaxPool2d(kernel_size=(2, 2))
        self.parabelt_pool = torch.nn.MaxPool2d(kernel_size=(2, 1))

        
        # DROPOUT: during training, randomly switch off 20% of the signals. ---
        self.dropout = torch.nn.Dropout(0.2)

        
        # STG: deliberately one-directional (forward in time only): like real listening, 
        # it never uses future sounds to interpret earlier ones.
       
        self.stg_rnn = torch.nn.GRU(input_size=64, hidden_size=128, num_layers=1, batch_first=True)

        # Classifuer
        self.classifier = torch.nn.Linear(128, num_classes)

    # Forward pass
    def forward(self, spectrogram: torch.Tensor) -> torch.Tensor:
        # Input shape: (batch, 1, mel_frequency, time) 

        # auditory core: detect simple features -> keep the strongest responses -> randomly drop some signals (training only)
        x = self.activation(self.core_conv(spectrogram))
        x = self.core_pool(x)
        x = self.dropout(x)

        # auditory belt: combine simple features into richer patterns, then summarise and apply dropout
        x = self.activation(self.belt_conv(x))
        x = self.belt_pool(x)
        x = self.dropout(x)

        # parabelt: detect complex, long-lasting patterns, then summarise and apply dropout
        x = self.activation(self.parabelt_conv(x))
        x = self.parabelt_pool(x)
        x = self.dropout(x)

        # bridge between "seeing patterns" and "following them over time": average across the remaining pitch bands so each moment in time is described by one list of 64 numbers, keeping the time order intact
        x = x.mean(dim=2).transpose(1, 2)

        # Stage 4 (STG-like memory): read the sequence moment by moment; `hidden` holds the memory state after the whole sound has been heard
        _, hidden = self.stg_rnn(x)

        # We treat the final memory state as  a compact summary of the entire sound
        stg_representation = hidden[-1]

        # Classifier converts stg representation into a score for each sound category
        return self.classifier(stg_representation)