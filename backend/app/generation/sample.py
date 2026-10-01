import torch
import random

from app.generation.tcn_model import MelodyTCN

MODEL_PATH = "app/generation/trained_model.pt"
VOCAB_PATH = "app/generation/vocabulary.pt"

# Model and vocabulary are loaded lazily, on first use, rather than at
# import time. Importing this module (which happens whenever the app
# starts, including in CI or any environment without the trained model
# files) used to fail immediately because torch.load ran at import time.
# Lazy loading means the app and its tests can start without the model
# files present; only code paths that actually generate music need them.
_model = None
_token_to_id = None
_id_to_token = None


def _ensure_loaded():
    global _model, _token_to_id, _id_to_token
    if _model is not None:
        return

    vocab_data = torch.load(VOCAB_PATH, weights_only=False)
    _token_to_id = vocab_data["token_to_id"]
    _id_to_token = vocab_data["id_to_token"]

    model = MelodyTCN(vocab_size=len(_token_to_id))
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()
    _model = model


def generate_raw_sequence(min_duration_beats: float, temperature: float = 1.0, max_events: int = 500) -> list[tuple[int, float]]:
    """
    Autoregressively samples tokens until the cumulative duration reaches
    at least `min_duration_beats`, rather than a fixed token count, so
    every requested song length is actually covered regardless of the
    duration distribution the model happens to sample.
    """
    _ensure_loaded()

    seed_id = random.choice(list(_id_to_token.keys()))
    context = [seed_id]
    generated = []
    total_duration = 0.0

    with torch.no_grad():
        while total_duration < min_duration_beats and len(generated) < max_events:
            input_tensor = torch.tensor([context[-64:]])
            logits, _ = _model(input_tensor)
            last_logits = logits[0, -1] / temperature
            probs = torch.softmax(last_logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1).item()

            context.append(next_id)
            token = _id_to_token[next_id]
            generated.append(token)
            total_duration += token[1]

    return generated