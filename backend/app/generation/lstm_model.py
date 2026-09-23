import torch
import torch.nn as nn


class MelodyLSTM(nn.Module):
    """
    A deliberately lightweight LSTM for symbolic melody generation.
    Small hidden size and few layers because music theory constraints
    (handled separately) reduce how much the model needs to learn on its own.
    """

    def __init__(self, vocab_size: int, embedding_dim: int = 32, hidden_dim: int = 128, num_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        output, hidden = self.lstm(embedded, hidden)
        logits = self.fc(output)
        return logits, hidden