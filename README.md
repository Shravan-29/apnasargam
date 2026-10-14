# ApnaSargam
![Backend Tests](https://github.com/Shravan-29/apnasargam/actions/workflows/backend-tests.yml/badge.svg)

A music generation platform I built end to end. You either describe a track in plain text ("sweet romantic love song") or pick the mood, key, BPM and genre yourself, and it composes a 1-2 minute instrumental as a MIDI file. You can play it in the browser, cut and trim it in a small timeline editor, and it gets saved to your projects.

It started as my research paper, "AI-Driven Music Generation: A Creative Tool for Modern Music Composition". I lost the original college code, so this is a full rebuild with the same idea behind it.

## How it works

```
text prompt -> intent classifier -> mood
                                      |
mood + key + genre -> song assembler -> TCN melody model -> scale/key constraints
                                      |
                      instrumentation + drum pattern -> MIDI -> browser playback
```

- **Intent classifier**: TF-IDF (unigrams + bigrams) with logistic regression, turns a free-text prompt into a mood.
- **Melody model**: a small Temporal Convolutional Network (dilated causal convolutions) trained on melodies from the Nottingham folk dataset. It predicts the next (pitch, duration) token.
- **Constraint layer**: the raw model output is snapped to the requested scale (Western keys, or Indian ragas like Bhupali, Yaman and Bhairav), so the result stays in key even if the model wanders.
- **Song assembler**: generates each unique section once (intro, verse, chorus, outro) and arranges them as intro-verse-chorus-verse-chorus-outro. Repeated sections are reused, like a real chorus.
- **Instrumentation and drums**: 7 moods and 8 genres (Rock, Jazz, Hip-hop, Electronic, Classical, Cinematic, Lo-fi, Ambient) each pick instruments and a rule-based drum pattern.
- **Job queue**: generation runs as a background job (Redis + RQ worker), so the API never blocks while a song is composed.
- **Hum to melody**: you hum into the mic, the browser encodes the recording as a WAV file (so the backend needs no ffmpeg), and a pitch detector I wrote from scratch (autocorrelation on numpy) turns it into notes. Those notes are snapped to the tokens the TCN was trained on and used as the seed, so the model continues your melody instead of starting from nothing.
- **Similar tracks**: each track is reduced to four numbers (average pitch, pitch range, note density, tempo) and compared with a Gaussian similarity score to list tracks like the one you are viewing.

## Measured results

| What | Result |
|---|---|
| Intent classifier | 87.1% accuracy, 0.873 precision, 0.871 recall, 0.866 F1 |
| Classifier data | dair-ai/emotion, 16,000 train and 2,000 validation examples |
| Melody model training data | 100 files from the Nottingham dataset, 13,003 training windows, vocabulary of 165 tokens |
| LSTM baseline | 241,605 parameters, about 4 min training on CPU, final loss about 0.20 |
| TCN (used) | 120,101 parameters, 3.2 min training on CPU, final loss about 0.23 |
| One full song generation | about 0.4 s in the worker in one measured run, output around 1:40 long |
| Pitch detector (synthetic audio) | Correct MIDI note in all 15 tone cases (5 notes x 3 sample rates); a 5-note melody with harmonics and gaps recovered note by note, also with background noise |
| Similarity score fix | My first version (cosine on raw features) scored all 15 pairs of 6 synthetic tracks between 98.5% and 99.97%, so it could not tell calm from energetic. Replaced with a Gaussian similarity: a close calm pair scores 88%, calm vs energetic about 0% |

The TCN has half the parameters of the LSTM and trained about 19% faster in my runs, with a slightly higher loss. Loss numbers are from my own runs on a 4 thread CPU and I did not average many seeds, so treat them as indicative.

Things I tried that did not help (kept in the commit history): more CPU threads made no difference, batch size 512 got worse loss for the same time, and a larger stride made training fast but left the model undertrained. An LSTM is sequential by nature, which is why switching architecture helped and tuning did not.

## Known limitations

- Genre is rule-based orchestration and drum patterns on top of the same melody model. I did not train a separate model per genre.
- The intent classifier only covers 5 of the 7 moods (Calm and Energetic have no equivalent label in the public dataset). Those two are still available through the manual mood picker.
- Playback uses a general MIDI soundfont in the browser, so instruments like flute or sitar sound synthetic.
- The in-browser player pulls in an old dependency chain that `npm audit` flags. It is client side only and there is no upstream fix, so I documented it instead of hiding it.
- Humming: the pitch detector was tested on synthetic tones and melodies, not on a range of real voices, so accuracy on real recordings is unmeasured. Repeating the same note with no pause between is detected as one long note. Output is melody only (no chords), fixed at 16 bars, and the continuation is inspired by the hum rather than an exact copy, because notes are snapped to the model's vocabulary. Hum timing is read using the BPM slider, so hum near that tempo.
- The similarity feature uses four hand-picked features, so it captures register and tempo but not melody shape or harmony.
- The backend has 76 pytest tests (auth, ownership, MIDI export, music config, pitch detection, similarity) and CI runs them on every push. The job queue endpoints, the hum endpoint and the frontend are not covered by tests. Not deployed anywhere yet.

## Stack

React, TypeScript, Vite, Tailwind on the frontend. FastAPI, SQLAlchemy, Alembic and PostgreSQL on the backend. Redis and RQ for jobs. PyTorch for the melody model, scikit-learn for the classifier, pretty_midi for MIDI output. Docker Compose for Postgres and Redis.

## Running it locally

You need Docker, Python 3.12 and Node.

```
# 1. database and redis
cd infrastructure
docker-compose up -d

# 2. backend
cd ../backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# create backend/.env with DATABASE_URL, REDIS_URL, SECRET_KEY, ENVIRONMENT
alembic upgrade head

# 3. data and models (dataset is not committed)
# download https://github.com/jukedeck/nottingham-dataset and put the MIDI folder in backend/dataset/
python -m app.generation.train_tcn
python -m app.generation.intent_classifier

# 4. run the api and the worker (two terminals)
uvicorn app.main:app --reload
rq worker generation --url redis://localhost:6379/0 --worker-class rq.worker.SimpleWorker

# 5. frontend
cd ../frontend
npm install
npm run dev
```

The `SimpleWorker` flag is only needed on Windows because the default RQ worker uses `fork`.

## Tests

cd backend
pip install pytest httpx
python -m pytest -v

API tests run against a temporary in-memory SQLite database, so no Postgres or Redis is needed. The trained model files must exist because the app loads the model on import.

## License

MIT