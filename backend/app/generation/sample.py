import torch
import random

from app.generation.tcn_model import MelodyTCN

MODEL_PATH = "app/generation/trained_model.pt"
VOCAB_PATH = "app/generation/vocabulary.pt"

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


def get_vocabulary():
    _ensure_loaded()
    return _token_to_id, _id_to_token


def generate_raw_sequence(
    min_duration_beats: float,
    temperature: float = 1.0,
    max_events: int = 500,
    seed_tokens: list[int] | None = None,
) -> list[tuple[int, float]]:
    """
    Autoregressively samples tokens until the cumulative duration of the
    NEWLY generated tokens reaches at least `min_duration_beats`.

    If `seed_tokens` is given, generation is conditioned on that context
    (e.g. a melody detected from a user's humming) instead of a random
    single seed - this is what lets the model continue a user's own
    musical idea rather than starting from scratch. The seed itself is
    not included in the returned list; only the new continuation is.
    """
    _ensure_loaded()

    if seed_tokens:
        context = list(seed_tokens)
    else:
        context = [random.choice(list(_id_to_token.keys()))]

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