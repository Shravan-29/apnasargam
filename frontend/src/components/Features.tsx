const features = [
  {
    label: 'Melody',
    title: 'Constraint-aware generation',
    description:
      "Every generated phrase is checked against key, scale and chord function before it ever reaches you.",
  },
  {
    label: 'Editor',
    title: 'A real editor, not a black box',
    description:
      "Cut, trim and rearrange any track the AI gives you, and save your edits back to the project.",
  },
  {
    label: 'Styles',
    title: 'Genres and Indian ragas',
    description:
      "Eight genres with their own instruments and drum patterns, plus an Indian folk mode using Bhupali, Yaman and Bhairav scales.",
  },
]

export default function Features() {
  return (
    <section id="learn" className="max-w-6xl mx-auto px-6 md:px-12 py-20 md:py-36">
      <div className="text-indigo text-sm uppercase tracking-widest font-semibold mb-4">
        What Makes It Different
      </div>
      <h2 className="font-display text-3xl md:text-4xl font-semibold max-w-xl leading-snug">
        Built like an instrument, not a slot machine.
      </h2>

      <div className="mt-12 md:mt-16 grid grid-cols-1 md:grid-cols-3 gap-px rounded-3xl overflow-hidden border border-white/10 bg-white/10">
        {features.map((feature) => (
          <div
            key={feature.label}
            className="bg-bg-soft p-7 md:p-10 hover:bg-[#14141d] transition-colors"
          >
            <div className="text-gold text-xs font-semibold mb-6">
              {feature.label}
            </div>
            <h3 className="text-lg font-semibold mb-2.5">{feature.title}</h3>
            <p className="text-muted text-sm leading-relaxed">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
