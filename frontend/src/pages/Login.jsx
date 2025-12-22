import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../utils/auth'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const submit = (e) => {
    e.preventDefault()
    // mock auth - accept any credentials
    login({ email, name: email.split('@')[0] })
    navigate('/search')
  }

  return (
    <div className="max-w-md mx-auto py-12">
      <form onSubmit={submit} className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Login</h2>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" className="w-full border px-3 py-2 rounded mb-3" />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" className="w-full border px-3 py-2 rounded mb-3" />
        <button className="w-full bg-blue-600 text-white py-2 rounded">Login</button>
        <div className="text-sm mt-3">No account? <a href="/signup" className="text-blue-600">Sign up</a></div>
      </form>
    </div>
  )
}
