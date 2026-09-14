const features = [
  {
    label: 'Melody',
    title: 'Constraint-aware generation',
    description:
      'Every generated phrase is checked against key, scale and chord function before it ever reaches you.',
  },
  {
    label: 'Editor',
    title: 'A real piano roll',
    description:
      'Drag, resize, and rewrite any note the AI gives you. It\'s a co-writer, not a black box.',
  },
  {
    label: 'Learn',
    title: 'Understand the "why"',
    description:
      'See the chord progression, the scale, the theory behind every composition — built to teach as you create.',
  },
]

export default function Features() {
  return (
    <section id="learn" className="max-w-6xl mx-auto px-12 py-36">
      <div className="text-indigo text-sm uppercase tracking-widest font-semibold mb-4">
        What Makes It Different
      </div>
      <h2 className="font-display text-4xl font-semibold max-w-xl leading-snug">
        Built like an instrument, not a slot machine.
      </h2>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-px rounded-3xl overflow-hidden border border-white/10 bg-white/10">
        {features.map((feature) => (
          <div
            key={feature.label}
            className="bg-bg-soft p-10 hover:bg-[#14141d] transition-colors"
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