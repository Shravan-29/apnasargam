import { Link, NavLink, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'

export default function AppNavbar() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('apnasargam_token')
    navigate('/')
  }

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm transition-colors ${isActive ? 'text-text' : 'text-muted hover:text-text'}`

  return (
    <nav className="sticky top-0 z-40 flex items-center justify-between px-12 py-4 border-b border-white/10 bg-bg/80 backdrop-blur">
      <Link to="/dashboard" className="font-display font-bold text-lg flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-gold" />
        ApnaSargam
      </Link>

      <div className="flex items-center gap-8">
        <NavLink to="/dashboard" className={linkClass}>
          Projects
        </NavLink>
        <NavLink to="/generate" className={linkClass}>
          Generate
        </NavLink>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-sm text-muted hover:text-red-400 transition-colors"
        >
          <LogOut size={15} />
          Log out
        </button>
      </div>
    </nav>
  )
}
