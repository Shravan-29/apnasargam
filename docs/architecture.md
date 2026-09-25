# ApnaSargam — Architecture Design Document (Phase 0)

**Status:** Approved for implementation
**Last updated:** 2026-08-16

---

## 1. Problem Statement

ApnaSargam is an AI-assisted music composition platform that turns natural-language
or structured musical intent (mood, genre, tempo, key) into original, editable
MIDI compositions. It evolves a college research prototype
("AI-Driven Music Generation: A Creative Tool for Modern Music Composition")
into a production-grade product, usable by both casual creators and musicians
who want to edit AI output at the note level.

## 2. Goals

- Users can generate music from natural-language or structured prompts
- Users can edit generated output in a real piano-roll editor
- Users can save, organize, and revisit projects
- System runs entirely on free-tier infrastructure at MVP scale
- Architecture scales to paid infrastructure later without a rewrite
- Codebase and process are resume-defensible for placement-level engineering roles

## 3. Non-Goals (explicitly out of scope for v1)

- Raw audio (waveform) generation — v1 is symbolic (MIDI) generation only,
  rendered to audio via soundfont synthesis, not neural audio synthesis
- Real-time multi-user collaborative editing (single-user projects only, v1)
- iOS app (Android via Capacitor first; iOS is a later milestone, same codebase)
- Training a music-generation model fully from scratch — v1 fine-tunes an
  existing open symbolic-music model

## 4. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | User can generate music via structured params (mood, genre, tempo, key, instruments, duration) |
| FR2 | User can generate music via natural-language prompt, parsed into structured params |
| FR3 | User can play back generated compositions |
| FR4 | User can edit notes (pitch, duration, velocity, position) in a piano-roll editor |
| FR5 | User can save/rename/delete/duplicate projects |
| FR6 | User can upload a MIDI file for analysis or editing |
| FR7 | User can view AI-assisted analysis of a composition (melody/harmony/rhythm heuristics, clearly labeled as heuristic) |
| FR8 | User can register, log in, and manage their account |
| FR9 | System processes generation as an async job with visible status (queued/generating/ready) |

## 5. Non-Functional Requirements

| ID | Requirement | Target (MVP, free-tier) |
|----|-------------|--------------------------|
| NFR1 | API responsiveness | Non-generation endpoints respond < 300ms p95 |
| NFR2 | Generation UX | Job status visible within 200ms of submission; no blocked/frozen UI |
| NFR3 | Piano-roll performance | 5,000+ notes render at 60fps |
| NFR4 | Security | Passwords hashed (bcrypt/argon2), JWT auth, rate-limited generation endpoint |
| NFR5 | Cost | $0 infrastructure cost at MVP scale (excluding one-time $25 Play Store fee) |
| NFR6 | Portability | Same React codebase serves Web + Android (Capacitor) |
| NFR7 | Observability | `/health` endpoint + structured logs from Phase 1 onward |

## 6. High-Level Architecture

### 6.1 Local development

React (Vite, TS) ──REST/JSON──> FastAPI
│
┌────────────┼────────────┐
▼ ▼ ▼
PostgreSQL Redis Local filesystem
(Docker) (Docker) (MIDI + audio)
│
▼
Celery/RQ worker
│
▼
AI Engine (PyTorch)


### 6.2 Production, free-tier

Users → CDN (static) → Backend API (single free-tier instance,
stateless, cold-start tolerant)
│
┌─────────┼─────────┐
▼ ▼ ▼
Postgres Redis Object storage
(free tier) (free tier) (R2/Supabase, free tier)
│
▼
Worker (same free-tier
compute, queue-driven)


Upgrade path (documented, not built until justified by real usage):
add more API replicas behind a load balancer, move worker pool to paid
GPU compute, upgrade DB/Redis tiers. Architecture is stateless by design
specifically so this upgrade is a config/infra change, not a rewrite.

## 7. API Contract (v1 sketch)

POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/projects
POST /api/v1/projects
GET /api/v1/projects/{id}
PATCH /api/v1/projects/{id}
DELETE /api/v1/projects/{id}

POST /api/v1/generate → creates async job, returns job_id
GET /api/v1/generate/{job_id} → job status: queued|generating|ready|failed

POST /api/v1/midi/upload
GET /api/v1/midi/{id}/analysis

GET /health


## 8. Core Data Model (v1)

users (id, email, password_hash, created_at)
projects (id, user_id, name, genre, mood, bpm, key, created_at, updated_at)
tracks (id, project_id, instrument, order)
generation_jobs (id, user_id, project_id, prompt, params_json, status, created_at, completed_at)
midi_files (id, project_id, storage_path, uploaded_at)
analysis_results(id, midi_file_id, melody_score, harmony_score, rhythm_score, method, created_at)


Indexes: `projects.user_id`, `generation_jobs.status`, `generation_jobs.user_id`.
`analysis_results.method` records how a score was computed (heuristic name),
so scores are never presented without provenance.

## 9. Architecture Decision Records (ADRs)

**ADR-001: FastAPI over Django**
Async-native, matches I/O-heavy workload (AI calls, file I/O), auto-generated
OpenAPI docs reduce frontend/backend contract drift. Trade-off: smaller
batteries-included ecosystem than Django; acceptable since we don't need
Django's admin/ORM conventions.

**ADR-002: PostgreSQL over MongoDB**
Data is relational (users → projects → tracks → jobs) with real foreign-key
integrity needs. JSONB columns cover the flexible bits (generation params)
without giving up relational guarantees elsewhere.

**ADR-003: Symbolic (MIDI) generation over raw audio generation, v1**
Raw audio (waveform) generative models require orders of magnitude more
compute and data than symbolic MIDI generation. Symbolic generation is
achievable on free-tier/CPU compute and is directly editable (a real
requirement — FR4), whereas raw audio output is not editable note-by-note.

**ADR-004: Async job queue for generation, not synchronous request**
Generation latency is unpredictable and can exceed reasonable HTTP timeout
windows. A synchronous endpoint would block API workers and degrade UX for
all users during any single slow generation.

**ADR-005: Free-tier-first infrastructure**
Per product constraint, cost must be $0 until usage justifies otherwise.
This caps realistic concurrent-generation capacity in the near term (see
Section 10), which is an accepted trade-off, not an oversight.

## 10. Known Constraints (stated explicitly, not hidden)

- Free-tier compute realistically supports low tens of concurrent generation
  jobs before queue wait time becomes noticeable — not 100k concurrent.
- Free backend hosting tiers may cold-start after inactivity; UI must
  communicate this state rather than appear frozen.
- Analysis scores (FR7) are heuristic, not scientifically validated —
  always labeled as such in UI and docs.

## 11. Milestone Breakdown

Follows the 27-phase roadmap, grouped:
- **Foundation** (Phases 1–7): local env, design system, shell, backend, DB
- **Core product** (Phases 8–14): MIDI engine, AI generation, player, piano roll, analysis, learning mode, research lab
- **Platform** (Phases 15–20): auth, jobs, testing, security, performance, Docker
- **Launch** (Phases 21–27): production architecture, deployment, domain, mobile, Play Store

## 12. Risks

| Risk | Mitigation |
|---|---|
| AI generation quality below expectations initially | Fine-tune existing open model rather than train from scratch; set honest expectations |
| Solo-dev scope creep vs 27-phase plan | Treat Phases 1–11 as MVP milestone; re-scope explicitly if behind |
| Free-tier compute ceiling hit by real usage | Architecture is scale-ready by design (ADR-004); upgrade is config-level |

## 13. Known Security Considerations

- `html-midi-player` (used for in-browser MIDI playback) has transitive
  dependencies (`protobufjs`, `ndarray-resample` via `@magenta/music`)
  with known CVEs and no upstream fix currently available. Risk is
  assessed as low for this project: these are client-side-only
  dependencies, and the app never parses untrusted protobuf input.
  Documented here rather than suppressed; a future mitigation would be
  replacing this library with a lighter, actively-maintained MIDI
  player if this becomes a production concern.