import React from 'react'
import { Link } from 'react-router-dom'

export default function Hero(){
  return (
    <section className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-20">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">Smarter Real Estate Search — AI + SQL</h1>
        <p className="text-lg md:text-xl mb-6">Hybrid semantic + structured search for buy & rent. Fast, affordable, and fully controllable.</p>
        <div className="space-x-3">
          <Link to="/signup" className="px-6 py-3 bg-white text-blue-600 rounded font-semibold">Get Started</Link>
          <a href="#features" className="px-6 py-3 border border-white rounded">Learn More</a>
        </div>
      </div>
    </section>
  )
}
