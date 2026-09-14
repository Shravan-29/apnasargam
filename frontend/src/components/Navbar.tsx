import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-12 py-5 bg-gradient-to-b from-bg/90 to-transparent backdrop-blur-sm">
      <div className="font-display font-bold text-xl flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-gold shadow-[0_0_12px_theme(colors.gold)]" />
        ApnaSargam
      </div>

      <div className="hidden md:flex gap-9 text-sm text-muted">
        <a href="#generate" className="hover:text-text transition-colors">
          Generate
        </a>
        <a href="#learn" className="hover:text-text transition-colors">
          Learn
        </a>
        <a href="#lab" className="hover:text-text transition-colors">
          Research Lab
        </a>
      </div>

      <Link
  to="/login"
  className="px-5 py-2.5 rounded-full bg-text text-bg text-sm font-semibold hover:-translate-y-0.5 transition-transform"
>
  Start Creating
</Link>
    </nav>
  )
}