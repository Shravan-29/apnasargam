# ApnaSargam

An AI music generation platform I'm building — you describe a mood, genre or tempo (or just type a sentence like "dark cyberpunk melody at 110 BPM") and it composes an actual MIDI track that you can then edit note by note.

This started from my research paper, "AI-Driven Music Generation: A Creative Tool for Modern Music Composition." The old college version doesn't exist anymore (lost the code), so this is a full rebuild — same research foundation, real production architecture this time.

## Status

Work in progress. Full design notes are in [docs/architecture.md](docs/architecture.md).

## Stack

Frontend is React + TypeScript + Vite + Tailwind. Backend is Python/FastAPI. AI side uses PyTorch with music21 and pretty_midi for handling the MIDI/music-theory layer. PostgreSQL for the database, Redis for the job queue. Planning to wrap it with Capacitor for an Android build later.

## A few things I care about getting right here

- Generated music actually needs to stay in key and follow sane chord progressions — a model spitting out technically-valid-but-random notes isn't good enough
- The piano roll has to stay smooth even with a few thousand notes on screen, so it's canvas-based instead of rendering a DOM element per note
- Generation happens as a background job instead of blocking the request, since it can take a while and I don't want the UI to just hang

## Setup

Not ready yet, will add once the local dev environment is working end to end.

## License

MIT