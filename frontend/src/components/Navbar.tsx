import { Link } from 'react-router-dom'

export default function Navbar() {
  const isLoggedIn = !!localStorage.getItem('apnasargam_token')

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-12 py-5 bg-gradient-to-b from-bg/90 to-transparent backdrop-blur-sm">
      <div className="font-display font-bold text-xl flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-gold" />
        ApnaSargam
      </div>

      <div className="hidden md:flex gap-9 text-sm text-muted">
        <a href="#generate" className="hover:text-text transition-colors">
          How it works
        </a>
        <a href="#learn" className="hover:text-text transition-colors">
          Features
        </a>
      </div>

      <div className="flex items-center gap-4">
        {isLoggedIn ? (
          <Link
            to="/dashboard"
            className="px-5 py-2.5 rounded-full bg-text text-bg text-sm font-semibold hover:-translate-y-0.5 transition-transform"
          >
            Open app
          </Link>
        ) : (
          <>
            <Link to="/login" className="text-sm text-muted hover:text-text transition-colors">
              Log in
            </Link>
            <Link
              to="/register"
              className="px-5 py-2.5 rounded-full bg-text text-bg text-sm font-semibold hover:-translate-y-0.5 transition-transform"
            >
              Start creating
            </Link>
          </>
        )}
      </div>
    </nav>
  )
}
