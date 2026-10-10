import { useRef, useState } from 'react'
import { Mic, Square } from 'lucide-react'

// Records raw PCM from the mic via the Web Audio API and encodes it as
// a 16-bit WAV file directly in the browser. This deliberately avoids
// MediaRecorder's default WebM/Opus output, which the backend would
// need ffmpeg to decode - encoding WAV client-side keeps the backend
// dependency-free (Python's built-in `wave` module can read it).
function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)

  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
  }

  writeString(0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, samples.length * 2, true)

  let offset = 44
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }

  return new Blob([view], { type: 'audio/wav' })
}

export default function HumRecorder({ onRecorded }: { onRecorded: (blob: Blob, url: string) => void }) {
  const [recording, setRecording] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const audioCtxRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const samplesRef = useRef<Float32Array[]>([])
  const timerRef = useRef<number | null>(null)

  const start = async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const audioCtx = new AudioContext()
      audioCtxRef.current = audioCtx
      const source = audioCtx.createMediaStreamSource(stream)
      sourceRef.current = source

      const processor = audioCtx.createScriptProcessor(4096, 1, 1)
      processorRef.current = processor
      samplesRef.current = []

      processor.onaudioprocess = (e) => {
        samplesRef.current.push(new Float32Array(e.inputBuffer.getChannelData(0)))
      }

      source.connect(processor)
      processor.connect(audioCtx.destination)

      setRecording(true)
      setSeconds(0)
      timerRef.current = window.setInterval(() => setSeconds((s) => s + 1), 1000)
    } catch {
      setError('Could not access the microphone. Check browser permissions.')
    }
  }

  const stop = () => {
    processorRef.current?.disconnect()
    sourceRef.current?.disconnect()
    streamRef.current?.getTracks().forEach((t) => t.stop())
    if (timerRef.current) window.clearInterval(timerRef.current)

    const sampleRate = audioCtxRef.current?.sampleRate || 44100
    const total = samplesRef.current.reduce((sum, arr) => sum + arr.length, 0)
    const merged = new Float32Array(total)
    let offset = 0
    for (const arr of samplesRef.current) {
      merged.set(arr, offset)
      offset += arr.length
    }

    const blob = encodeWav(merged, sampleRate)
    const url = URL.createObjectURL(blob)
    onRecorded(blob, url)

    audioCtxRef.current?.close()
    setRecording(false)
  }

  return (
    <div>
      <div className="flex items-center gap-3">
        {!recording ? (
          <button
            type="button"
            onClick={start}
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-gold text-black text-sm font-semibold"
          >
            <Mic size={16} />
            Start Humming
          </button>
        ) : (
          <button
            type="button"
            onClick={stop}
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-red-400 text-black text-sm font-semibold"
          >
            <Square size={14} />
            Stop ({seconds}s)
          </button>
        )}
      </div>
      {error && <p className="text-xs text-red-400 mt-2">{error}</p>}
    </div>
  )
}
