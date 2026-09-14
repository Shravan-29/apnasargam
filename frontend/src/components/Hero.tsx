import { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function Hero() {
  const canvasWrapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const wrap = canvasWrapRef.current
    if (!wrap) return

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(
      55,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    )
    camera.position.set(0, 0, 9)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    wrap.appendChild(renderer.domElement)

    const COUNT = 2600
    const geometry = new THREE.BufferGeometry()
    const positions = new Float32Array(COUNT * 3)
    const chaosPos: number[] = []
    const orderPos: number[] = []
    const colors = new Float32Array(COUNT * 3)

    const gold = new THREE.Color(0xe8a33d)
    const indigo = new THREE.Color(0x6c5ce7)

    for (let i = 0; i < COUNT; i++) {
      const r = 4.5 + Math.random() * 2.5
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(Math.random() * 2 - 1)
      const cx = r * Math.sin(phi) * Math.cos(theta)
      const cy = r * Math.sin(phi) * Math.sin(theta)
      const cz = r * Math.cos(phi)
      chaosPos.push(cx, cy, cz)

      const t = (i / COUNT) * Math.PI * 10
      const strand = i % 2
      const radius = 2.6 + Math.sin(t * 0.5) * 0.5
      const ox = Math.cos(t + strand * Math.PI) * radius
      const oy = (i / COUNT) * 8 - 4
      const oz = Math.sin(t + strand * Math.PI) * radius
      orderPos.push(ox, oy, oz)

      positions[i * 3] = cx
      positions[i * 3 + 1] = cy
      positions[i * 3 + 2] = cz

      const c = gold.clone().lerp(indigo, Math.random())
      colors[i * 3] = c.r
      colors[i * 3 + 1] = c.g
      colors[i * 3 + 2] = c.b
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

    const material = new THREE.PointsMaterial({
      size: 0.055,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })

    const points = new THREE.Points(geometry, material)
    scene.add(points)

    let morph = 0
    let targetMorph = 0
    let mouseX = 0
    let mouseY = 0
    let autoT = 0

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2
      targetMorph = Math.min(1, Math.abs(mouseX) * 0.6 + 0.35)
    }
    window.addEventListener('mousemove', handleMouseMove)

    let animationId: number
    const animate = () => {
      animationId = requestAnimationFrame(animate)
      autoT += 0.004
      const autoMorph = (Math.sin(autoT) + 1) / 2
      morph += (targetMorph * 0.6 + autoMorph * 0.4 - morph) * 0.03

      const posAttr = geometry.attributes.position as THREE.BufferAttribute
      for (let i = 0; i < COUNT; i++) {
        const cx = chaosPos[i * 3]
        const cy = chaosPos[i * 3 + 1]
        const cz = chaosPos[i * 3 + 2]
        const ox = orderPos[i * 3]
        const oy = orderPos[i * 3 + 1]
        const oz = orderPos[i * 3 + 2]
        posAttr.array[i * 3] = cx + (ox - cx) * morph
        posAttr.array[i * 3 + 1] = cy + (oy - cy) * morph
        posAttr.array[i * 3 + 2] = cz + (oz - cz) * morph
      }
      posAttr.needsUpdate = true

      points.rotation.y += 0.0018
      points.rotation.x = mouseY * 0.15

      camera.position.x += (mouseX * 1.2 - camera.position.x) * 0.03
      camera.lookAt(0, 0, 0)

      renderer.render(scene, camera)
    }
    animate()

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', handleResize)
      wrap.removeChild(renderer.domElement)
      geometry.dispose()
      material.dispose()
      renderer.dispose()
    }
  }, [])

  return (
    <section className="relative h-screen flex items-center px-12 overflow-hidden bg-bg">
      <div ref={canvasWrapRef} className="absolute inset-0 z-0" />

      <div className="relative z-10 max-w-xl pointer-events-none">
        <div className="text-gold text-sm uppercase tracking-widest font-semibold mb-5">
          AI Music Composition
        </div>
        <h1 className="font-display text-6xl font-bold leading-tight">
          Turn intent into{' '}
          <span className="bg-gradient-to-r from-gold to-yellow-200 bg-clip-text text-transparent">
            music
          </span>
          , note by note.
        </h1>
        <p className="mt-6 text-muted text-lg max-w-md">
          ApnaSargam listens to a mood, a tempo, a feeling — and composes
          original melodies, harmonies and rhythm with you, not for you.
        </p>
        <div className="mt-9 flex gap-4 pointer-events-auto">
          <button className="px-7 py-4 rounded-full bg-gold text-black font-semibold hover:-translate-y-0.5 transition-transform">
            Start Composing
          </button>
          <button className="px-7 py-4 rounded-full border border-white/10 hover:border-white/25 transition-colors">
            See it think
          </button>
        </div>
      </div>
    </section>
  )
}