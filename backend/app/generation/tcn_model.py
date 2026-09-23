import torch
import torch.nn as nn


class CausalConv1d(nn.Module):
    """
    A 1D convolution that only looks at past and present tokens, never
    future ones (padding is added on the left, then trimmed on the right).
    This preserves the autoregressive property LSTMs give for free.
    """

    def __init__(self, in_channels, out_channels, kernel_size, dilation):
        super().__init__()
        self.padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            in_channels, out_channels, kernel_size,
            padding=self.padding, dilation=dilation
        )

    def forward(self, x):
        out = self.conv(x)
        return out[:, :, :-self.padding] if self.padding != 0 else out


class TCNBlock(nn.Module):
    """
    One residual block: two causal dilated convolutions with a skip
    connection. Dilation grows exponentially across blocks (1, 2, 4, 8...)
    so deeper blocks see exponentially larger context without needing
    more layers or recurrence.
    """

    def __init__(self, channels, kernel_size, dilation):
        super().__init__()
        self.conv1 = CausalConv1d(channels, channels, kernel_size, dilation)
        self.conv2 = CausalConv1d(channels, channels, kernel_size, dilation)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.relu(self.conv1(x))
        out = self.relu(self.conv2(out))
        return self.relu(out + x)  # residual connection


class MelodyTCN(nn.Module):
    """
    TCN-based alternative to MelodyLSTM. Same input/output interface
    (token sequence in, next-token logits out), fully parallelizable
    over the sequence dimension during training.
    """

    def __init__(self, vocab_size: int, channels: int = 64, num_blocks: int = 4, kernel_size: int = 3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, channels)
        self.blocks = nn.Sequential(*[
            TCNBlock(channels, kernel_size, dilation=2 ** i)
            for i in range(num_blocks)
        ])
        self.fc = nn.Linear(channels, vocab_size)

    def forward(self, x, hidden=None):
        # x: (batch, seq_len) -> embed -> (batch, seq_len, channels)
        embedded = self.embedding(x)
        # Conv1d expects (batch, channels, seq_len)
        embedded = embedded.transpose(1, 2)
        out = self.blocks(embedded)
        out = out.transpose(1, 2)  # back to (batch, seq_len, channels)
        logits = self.fc(out)
        return logits, None