import os
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import os
torch.set_num_threads(os.cpu_count())
print(f"Using {os.cpu_count()} CPU threads")

from app.generation.tokenizer import build_vocabulary
from app.generation.training_data import MelodyDataset
from app.generation.lstm_model import MelodyLSTM

DATASET_DIR = "dataset/MIDI/melody"
MODEL_SAVE_PATH = "app/generation/trained_model.pt"
VOCAB_SAVE_PATH = "app/generation/vocabulary.pt"

MAX_FILES = 100
SEQ_LENGTH = 32
BATCH_SIZE = 128
EPOCHS = 20
LEARNING_RATE = 0.003

# Early stopping configuration: if loss improvement drops below
# MIN_IMPROVEMENT for PATIENCE consecutive epochs, training stops.
# This avoids wasting compute on epochs that aren't meaningfully
# improving the model, without reducing model size or context length.
PATIENCE = 3
MIN_IMPROVEMENT = 0.005


def train():
    print("Building vocabulary...")
    token_to_id, id_to_token = build_vocabulary(DATASET_DIR, max_files=MAX_FILES)
    vocab_size = len(token_to_id)
    print(f"Vocabulary size: {vocab_size}")

    all_files = [
        os.path.join(DATASET_DIR, f)
        for f in os.listdir(DATASET_DIR) if f.endswith(".mid")
    ][:MAX_FILES]

    print("Building training dataset...")
    STRIDE = 1
    dataset = MelodyDataset(all_files, token_to_id, seq_length=SEQ_LENGTH, stride=STRIDE)
    print(f"Total training examples: {len(dataset)}")

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,
        persistent_workers=True,
    )

    model = MelodyLSTM(vocab_size=vocab_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=1)

    print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")
    print("Starting training...\n")

    start_time = time.time()
    best_loss = float("inf")
    patience_counter = 0
    epochs_run = 0

    for epoch in range(EPOCHS):
        total_loss = 0.0
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            logits, _ = model(inputs)

            loss = criterion(logits.view(-1, vocab_size), targets.view(-1))
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        scheduler.step(avg_loss)
        epochs_run = epoch + 1
        print(f"Epoch {epochs_run}/{EPOCHS} - Loss: {avg_loss:.4f}")

        if best_loss - avg_loss > MIN_IMPROVEMENT:
            best_loss = avg_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"\nEarly stopping triggered at epoch {epochs_run} (loss plateaued)")
                break

    elapsed = time.time() - start_time
    print(f"\nTraining completed in {elapsed:.1f} seconds ({elapsed/60:.2f} minutes)")
    print(f"Ran {epochs_run}/{EPOCHS} epochs, final loss: {best_loss:.4f}")

    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    torch.save({"token_to_id": token_to_id, "id_to_token": id_to_token}, VOCAB_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()