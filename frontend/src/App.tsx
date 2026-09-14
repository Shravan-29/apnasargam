import Navbar from './components/Navbar'
import Hero from './components/Hero'
import PromptDemo from './components/PromptDemo'
import Features from './components/Features'
import Footer from './components/Footer'

function App() {
  return (
    <div className="bg-bg text-text">
      <Navbar />
      <Hero />
      <PromptDemo />
      <Features />
      <Footer />
    </div>
  )
}

export default App