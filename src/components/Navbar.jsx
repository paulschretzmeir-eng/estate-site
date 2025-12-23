import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { isAuthenticated, logout, currentUser } from '../utils/auth'

export default function Navbar(){
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <nav className="bg-white shadow">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-2xl font-semibold text-blue-600">EstateGPT</Link>
          <div className="hidden md:flex space-x-3 text-gray-600">
            <Link to="/search" className="hover:text-blue-600">Search</Link>
            <a href="#features" className="hover:text-blue-600">Features</a>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {isAuthenticated() ? (
            <>
              <span className="text-gray-700">{currentUser()?.name || 'You'}</span>
              <button onClick={handleLogout} className="px-3 py-1 bg-gray-100 rounded">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-3 py-1 border rounded border-blue-600 text-blue-600">Login</Link>
              <Link to="/signup" className="px-3 py-1 bg-blue-600 text-white rounded">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
