import Navbar from './Navbar'
import Hero from './Hero'
import PromptDemo from './PromptDemo'
import Features from './Features'
import Footer from './Footer'

export default function LandingPage() {
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