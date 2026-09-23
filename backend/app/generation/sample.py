import torch

from app.generation.tcn_model import MelodyTCN

MODEL_PATH = "app/generation/trained_model.pt"
VOCAB_PATH = "app/generation/vocabulary.pt"

# Loaded once when the worker process starts, not on every generation
# request, since deserializing model weights repeatedly would add
# unnecessary latency to each job.
_vocab_data = torch.load(VOCAB_PATH, weights_only=False)
_token_to_id = _vocab_data["token_to_id"]
_id_to_token = _vocab_data["id_to_token"]

_model = MelodyTCN(vocab_size=len(_token_to_id))
_model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
_model.eval()


def generate_raw_sequence(num_events: int, temperature: float = 1.0) -> list[tuple[int, float]]:
    """
    Autoregressively samples a sequence of (pitch, duration) tokens from
    the trained TCN. Temperature controls randomness: lower = more
    conservative/repetitive, higher = more chaotic/creative.
    """
    import random
    seed_id = random.choice(list(_id_to_token.keys()))
    context = [seed_id]
    generated = []

    with torch.no_grad():
        for _ in range(num_events):
            input_tensor = torch.tensor([context[-64:]])  # cap context for efficiency
            logits, _ = _model(input_tensor)
            last_logits = logits[0, -1] / temperature
            probs = torch.softmax(last_logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1).item()

            context.append(next_id)
            generated.append(_id_to_token[next_id])

    return generated