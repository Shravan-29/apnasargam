from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import joblib

MODEL_PATH = "app/generation/intent_classifier.joblib"
VECTORIZER_PATH = "app/generation/intent_vectorizer.joblib"

# Maps the dair-ai/emotion dataset's 6 emotion labels onto our music
# mood taxonomy. This is a deliberate, documented simplification: the
# public dataset does not have direct equivalents for "Calm" or
# "Energetic", so this classifier currently supports 5 of our 7 moods.
# Prompts implying Calm/Energetic still work via the existing keyword
# fallback in the generation UI.
EMOTION_ID_TO_LABEL = {0: "sadness", 1: "joy", 2: "love", 3: "anger", 4: "fear", 5: "surprise"}

EMOTION_TO_MOOD = {
    "sadness": "Melancholic",
    "joy": "Uplifting",
    "love": "Romantic",
    "anger": "Dark",
    "fear": "Dark",
    "surprise": "Epic",
}


def train_intent_classifier():
    print("Downloading/loading dair-ai/emotion dataset...")
    dataset = load_dataset("dair-ai/emotion")

    train_texts = dataset["train"]["text"]
    train_labels = [EMOTION_TO_MOOD[EMOTION_ID_TO_LABEL[label]] for label in dataset["train"]["label"]]

    val_texts = dataset["validation"]["text"]
    val_labels = [EMOTION_TO_MOOD[EMOTION_ID_TO_LABEL[label]] for label in dataset["validation"]["label"]]

    print(f"Training examples: {len(train_texts)}")
    print(f"Validation examples: {len(val_texts)}")

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)

    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X_train, train_labels)

    predictions = classifier.predict(X_val)

    accuracy = accuracy_score(val_labels, predictions)
    precision = precision_score(val_labels, predictions, average="weighted", zero_division=0)
    recall = recall_score(val_labels, predictions, average="weighted", zero_division=0)
    f1 = f1_score(val_labels, predictions, average="weighted", zero_division=0)

    print(f"\nAccuracy: {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")

    joblib.dump(classifier, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def predict_mood_from_prompt(prompt: str) -> str:
    classifier = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    vectorized = vectorizer.transform([prompt])
    return classifier.predict(vectorized)[0]


if __name__ == "__main__":
    train_intent_classifier()