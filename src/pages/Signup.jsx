import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../utils/auth'

export default function Signup(){
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const submit = (e) => {
    e.preventDefault()
    // mock signup - store user locally and redirect
    login({ name, email })
    navigate('/search')
  }

  return (
    <div className="max-w-md mx-auto py-12">
      <form onSubmit={submit} className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Sign Up</h2>
        <input value={name} onChange={e=>setName(e.target.value)} placeholder="Full name" className="w-full border px-3 py-2 rounded mb-3" />
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" className="w-full border px-3 py-2 rounded mb-3" />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" className="w-full border px-3 py-2 rounded mb-3" />
        <button className="w-full bg-blue-600 text-white py-2 rounded">Create account</button>
        <div className="text-sm mt-3">Already have an account? <a href="/login" className="text-blue-600">Login</a></div>
      </form>
    </div>
  )
}
