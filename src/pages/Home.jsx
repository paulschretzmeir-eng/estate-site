import React from 'react'
import Hero from '../components/Hero'

export default function Home(){
  return (
    <div>
      <Hero />
      <section id="features" className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-semibold mb-4">Why choose RealEstateAI?</h2>
        <ul className="grid md:grid-cols-3 gap-6 text-gray-700">
          <li className="bg-white p-4 rounded shadow">AI-assisted natural language search with structured filters.</li>
          <li className="bg-white p-4 rounded shadow">Hybrid semantic + SQL search for relevancy and control.</li>
          <li className="bg-white p-4 rounded shadow">Cost efficient per-search AI usage.</li>
        </ul>
      </section>
    </div>
  )
}
