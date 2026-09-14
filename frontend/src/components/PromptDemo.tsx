export default function PromptDemo() {
  const tags = [
    { label: 'Key: A Minor' },
    { label: 'Tempo: 110 BPM' },
    { label: 'Mood: Tense' },
    { label: 'Instruments: Synth, Strings' },
    { label: 'Structure: A–B–A' },
  ]

  return (
    <section id="generate" className="max-w-6xl mx-auto px-12 py-36">
      <div className="text-indigo text-sm uppercase tracking-widest font-semibold mb-4">
        The Generator
      </div>
      <h2 className="font-display text-4xl font-semibold max-w-xl leading-snug">
        Describe it in your own words. It composes in music theory.
      </h2>
      <p className="mt-4 text-muted max-w-lg">
        Every prompt is parsed into real musical parameters — key, tempo,
        chord function — not guesswork.
      </p>

      <div className="mt-16 rounded-3xl border border-white/10 bg-bg-soft p-10 flex flex-col gap-6">
        <div className="flex items-center gap-3 rounded-full border border-white/10 px-6 py-4 text-base">
          Dark cinematic cyberpunk melody at 110 BPM
          <span className="w-0.5 h-4 bg-gold animate-pulse" />
        </div>

        <div className="flex flex-wrap gap-2.5">
          {tags.map((tag) => (
            <span
              key={tag.label}
              className="px-4 py-2 rounded-full bg-indigo/10 border border-indigo/25 text-indigo-200 text-xs font-medium"
            >
              {tag.label}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}