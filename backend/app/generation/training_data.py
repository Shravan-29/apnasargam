import torch
from torch.utils.data import Dataset

from app.generation.tokenizer import extract_notes_from_file


class MelodyDataset(Dataset):
    def __init__(self, file_paths: list[str], token_to_id: dict, seq_length: int = 32, stride: int = 8):
        self.seq_length = seq_length
        self.examples = []

        for file_path in file_paths:
            try:
                sequence = extract_notes_from_file(file_path)
                token_ids = [token_to_id[t] for t in sequence if t in token_to_id]

                for i in range(0, len(token_ids) - seq_length, stride):
                    input_seq = token_ids[i:i + seq_length]
                    target_seq = token_ids[i + 1:i + seq_length + 1]
                    self.examples.append((input_seq, target_seq))
            except Exception:
                continue

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        input_seq, target_seq = self.examples[idx]
        return torch.tensor(input_seq), torch.tensor(target_seq)