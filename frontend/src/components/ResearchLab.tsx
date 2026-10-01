import { Link } from 'react-router-dom'

function Section({ eyebrow, title, children }: { eyebrow: string; title: string; children: React.ReactNode }) {
  return (
    <section className="max-w-4xl mx-auto px-6 md:px-12 py-16 border-b border-white/10">
      <div className="text-indigo text-xs uppercase tracking-widest font-semibold mb-3">{eyebrow}</div>
      <h2 className="font-display text-2xl font-semibold mb-6">{title}</h2>
      {children}
    </section>
  )
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0">
      <span className="text-sm text-muted">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  )
}

function Bar({ label, value, max, suffix }: { label: string; value: number; max: number; suffix: string }) {
  const pct = (value / max) * 100
  return (
    <div className="mb-4">
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-muted">{label}</span>
        <span className="font-medium">{value}{suffix}</span>
      </div>
      <div className="h-2.5 rounded-full bg-white/5 overflow-hidden">
        <div className="h-full rounded-full bg-gradient-to-r from-gold to-indigo" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function ResearchLab() {
  return (
    <div className="bg-bg text-text min-h-screen">
      <nav className="flex items-center justify-between px-6 md:px-12 py-5 border-b border-white/10">
        <Link to="/" className="font-display font-bold text-lg flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-gold" />
          ApnaSargam
        </Link>
        <Link to="/" className="text-sm text-muted hover:text-text transition-colors">
          Back to home
        </Link>
      </nav>

      <div className="px-6 md:px-12 pt-16 pb-8 max-w-4xl mx-auto">
        <div className="text-gold text-xs uppercase tracking-widest font-semibold mb-4">Research Lab</div>
        <h1 className="font-display text-4xl font-bold mb-5">From a research paper to a working system</h1>
        <p className="text-muted max-w-2xl leading-relaxed">
          This started as my research paper, "AI-Driven Music Generation: A
          Creative Tool for Modern Music Composition". This page documents
          the actual training runs and numbers behind the system, not a
          polished summary. Where a number is approximate or a method has a
          known limitation, it's noted as such below.
        </p>
      </div>

      <Section eyebrow="Pipeline" title="How a prompt becomes a song">
        <div className="rounded-2xl border border-white/10 bg-bg-soft p-6 font-mono text-xs text-muted leading-7 overflow-x-auto whitespace-pre">
{`text prompt
  -> intent classifier (TF-IDF + logistic regression) -> mood
mood + key + genre
  -> song assembler (intro/verse/chorus/verse/chorus/outro)
  -> TCN melody model (dilated causal convolutions) -> raw (pitch, duration) tokens
  -> scale/raga constraint layer -> notes snapped to key
  -> instrumentation + rule-based drum pattern
  -> MIDI file -> browser playback`}
        </div>
      </Section>

      <Section eyebrow="Dataset" title="What the melody model learned from">
        <div className="rounded-2xl border border-white/10 bg-bg-soft p-6">
          <MetricRow label="Source" value="Nottingham folk dataset" />
          <MetricRow label="Files used" value="100 of 1,034 available" />
          <MetricRow label="Vocabulary size" value="165 unique (pitch, duration) tokens" />
          <MetricRow label="Training windows" value="13,003 (stride 1, sequence length 32)" />
        </div>
        <p className="text-xs text-muted mt-4 leading-relaxed">
          Only 100 files were used to keep training time short on a CPU. A
          larger subset would likely improve melodic variety but was not
          tested due to time constraints.
        </p>
      </Section>

      <Section eyebrow="Architecture experiment" title="Why a TCN instead of an LSTM">
        <p className="text-sm text-muted mb-6 leading-relaxed">
          The first version used an LSTM. After testing whether hyperparameters
          (batch size, thread count, learning rate schedule) could reduce
          training time, none of them helped, because an LSTM's recurrence is
          inherently sequential. Switching the architecture to a Temporal
          Convolutional Network, which is parallelizable, did help.
        </p>

        <div className="rounded-2xl border border-white/10 bg-bg-soft p-6">
          <Bar label="LSTM parameters" value={241605} max={250000} suffix="" />
          <Bar label="TCN parameters" value={120101} max={250000} suffix="" />
          <Bar label="LSTM training time" value={4.0} max={5} suffix=" min" />
          <Bar label="TCN training time" value={3.2} max={5} suffix=" min" />
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4 text-xs text-muted">
          <p>LSTM final loss: about 0.20</p>
          <p>TCN final loss: about 0.23</p>
        </div>

        <p className="text-xs text-muted mt-4 leading-relaxed">
          The TCN has about half the parameters and trained roughly 19% faster,
          at a slightly higher loss. These are single runs on a 4-thread CPU,
          not averaged over multiple seeds, so treat them as indicative rather
          than statistically rigorous.
        </p>

        <div className="mt-4 rounded-xl border border-white/10 p-4 text-xs text-muted leading-relaxed">
          <span className="text-text font-medium">Tried and rejected:</span> more
          CPU threads made no measurable difference; batch size 512 trained in
          the same time but with worse loss; a larger stride cut training time
          but left the model undertrained. Kept in the commit history rather
          than removed.
        </div>
      </Section>

      <Section eyebrow="NLP intent classifier" title="Turning a sentence into a mood">
        <p className="text-sm text-muted mb-6 leading-relaxed">
          TF-IDF (unigrams and bigrams) with logistic regression, trained on
          the public dair-ai/emotion dataset. Its six emotion labels were
          mapped onto five of this project's seven moods (Calm and Energetic
          have no equivalent label, so those are only reachable through the
          manual mood picker, not free text).
        </p>

        <div className="rounded-2xl border border-white/10 bg-bg-soft p-6">
          <MetricRow label="Training examples" value="16,000" />
          <MetricRow label="Validation examples" value="2,000 (held out, not seen in training)" />
          <MetricRow label="Accuracy" value="87.1%" />
          <MetricRow label="Precision (weighted)" value="0.873" />
          <MetricRow label="Recall (weighted)" value="0.871" />
          <MetricRow label="F1 score (weighted)" value="0.866" />
        </div>
      </Section>

      <Section eyebrow="Known limitations" title="What this system does not do well yet">
        <ul className="text-sm text-muted flex flex-col gap-3 leading-relaxed list-disc pl-5">
          <li>Genre (Rock, Jazz, Hip-hop, etc.) changes instrumentation and the drum pattern, not the melody model itself. No genre-specific training data was used.</li>
          <li>Playback uses a general MIDI soundfont in the browser, so instruments like flute or sitar sound synthetic rather than like a recording.</li>
          <li>The melody model was trained on 100 files for speed; quality is bounded by that dataset size.</li>
          <li>No automated listening evaluation exists; quality was judged by ear, not a metric.</li>
        </ul>
      </Section>

      <div className="px-6 md:px-12 py-16 max-w-4xl mx-auto text-center">
        <Link
          to="/register"
          className="inline-block px-7 py-3.5 rounded-full bg-gold text-black font-semibold text-sm hover:-translate-y-0.5 transition-transform"
        >
          Try generating a track
        </Link>
      </div>
    </div>
  )
}
