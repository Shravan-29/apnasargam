import torch
import random

from app.generation.tcn_model import MelodyTCN

MODEL_PATH = "app/generation/trained_model.pt"
VOCAB_PATH = "app/generation/vocabulary.pt"

_vocab_data = torch.load(VOCAB_PATH, weights_only=False)
_token_to_id = _vocab_data["token_to_id"]
_id_to_token = _vocab_data["id_to_token"]

_model = MelodyTCN(vocab_size=len(_token_to_id))
_model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
_model.eval()


def generate_raw_sequence(min_duration_beats: float, temperature: float = 1.0, max_events: int = 500) -> list[tuple[int, float]]:
    """
    Autoregressively samples tokens until the cumulative duration reaches
    at least `min_duration_beats`, rather than a fixed token count.
    A fixed-count approach under-filled sections when the model sampled
    many short-duration tokens (discovered via measured song-length
    being far shorter than requested). Generating by cumulative duration
    guarantees every section reaches its intended length regardless of
    the duration distribution the model happens to sample.
    `max_events` is a safety cap against a pathological infinite loop.
    """
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