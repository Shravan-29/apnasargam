import { Link } from 'react-router-dom'

export default function PromptDemo() {
  const isLoggedIn = !!localStorage.getItem('apnasargam_token')

  const steps = [
    { label: 'You type', value: 'Dark cinematic melody, slow and tense' },
    { label: 'Classifier reads the mood', value: 'Dark' },
    { label: 'Model writes the melody', value: 'Temporal convolutional network' },
    { label: 'Theory layer keeps it in key', value: 'Scale and chord constraints' },
    { label: 'You get', value: '1-2 minute MIDI track you can edit' },
  ]

  return (
    <section id="generate" className="max-w-6xl mx-auto px-12 py-36">
      <div className="text-indigo text-sm uppercase tracking-widest font-semibold mb-4">
        How it works
      </div>
      <h2 className="font-display text-4xl font-semibold max-w-xl leading-snug">
        Describe it in your own words. It composes in music theory.
      </h2>
      <p className="mt-4 text-muted max-w-lg">
        A text classifier picks the mood from your sentence, a small neural
        network writes the melody, and a theory layer keeps every note in key.
      </p>

      <div className="mt-16 rounded-3xl border border-white/10 bg-bg-soft p-10 flex flex-col gap-4">
        {steps.map((step, index) => (
          <div
            key={step.label}
            className="flex items-center gap-4 rounded-2xl border border-white/10 px-6 py-4"
          >
            <div className="w-7 h-7 rounded-full bg-gold text-black text-xs font-bold flex items-center justify-center shrink-0">
              {index + 1}
            </div>
            <div className="text-sm text-muted w-64 shrink-0">{step.label}</div>
            <div className="text-sm">{step.value}</div>
          </div>
        ))}

        <Link
          to={isLoggedIn ? '/generate' : '/register'}
          className="mt-4 self-start px-6 py-3 rounded-full bg-gold text-black text-sm font-semibold hover:-translate-y-0.5 transition-transform"
        >
          Try it yourself
        </Link>
      </div>
    </section>
  )
}
