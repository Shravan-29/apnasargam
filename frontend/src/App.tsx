import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import Register from './components/Register'
import Generator from './components/Generator'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/generate" element={<Generator />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App