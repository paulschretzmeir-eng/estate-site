import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import Search from './pages/Search'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { isAuthenticated } from './utils/auth'
import SearchBar from './components/SearchBar'
import PropertyResults from './components/PropertyResults'

function Protected({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [results, setResults] = useState([])

  const handleSearchResults = (res) => {
    setResults(Array.isArray(res) ? res : [])
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <section className="mx-auto max-w-6xl px-4 py-6">
          <div className="mb-6">
            <SearchBar onSearchResults={handleSearchResults} />
          </div>
          <PropertyResults results={results} />
        </section>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Protected><Search /></Protected>} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
