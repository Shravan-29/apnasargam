from app.generation.tokenizer import build_vocabulary

DATASET_DIR = "dataset/MIDI/melody"

token_to_id, id_to_token = build_vocabulary(DATASET_DIR, max_files=100)

print(f"Vocabulary size: {len(token_to_id)}")
print(f"Sample tokens: {list(token_to_id.items())[:10]}")