import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import { Lock, User, ChevronDown } from 'lucide-react'

const Login: React.FC = () => {
  const [selectedUser, setSelectedUser] = useState('')
  const [loading, setLoading] = useState(false)
  const { updateUser } = useAuth()
  const navigate = useNavigate()

  const demoUsers = [
    {
      id: 1,
      username: 'admin',
      email: 'admin@regisbridge.edu',
      first_name: 'John',
      last_name: 'Admin',
      role: 'ADMIN',
      is_active: true,
      date_joined: '2024-01-01T00:00:00Z',
      last_login: null
    },
    {
      id: 2,
      username: 'teacher1',
      email: 'teacher1@regisbridge.edu',
      first_name: 'Sarah',
      last_name: 'Johnson',
      role: 'TEACHER',
      is_active: true,
      date_joined: '2024-01-01T00:00:00Z',
      last_login: null
    },
    {
      id: 3,
      username: 'student1',
      email: 'student1@regisbridge.edu',
      first_name: 'Michael',
      last_name: 'Brown',
      role: 'STUDENT',
      is_active: true,
      date_joined: '2024-01-01T00:00:00Z',
      last_login: null
    },
    {
      id: 4,
      username: 'parent1',
      email: 'parent1@regisbridge.edu',
      first_name: 'Jennifer',
      last_name: 'Davis',
      role: 'PARENT',
      is_active: true,
      date_joined: '2024-01-01T00:00:00Z',
      last_login: null
    }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedUser) return
    
    setLoading(true)
    
    // Simulate login delay
    setTimeout(() => {
      const user = demoUsers.find(u => u.username === selectedUser)
      if (user) {
        updateUser(user)
        navigate('/')
      }
      setLoading(false)
    }, 500)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <Lock className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Regisbridge
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            College Management System
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="user-select" className="block text-sm font-medium text-gray-700 mb-2">
              Select Demo User
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <select
                id="user-select"
                name="user-select"
                required
                className="appearance-none relative block w-full px-3 py-2 pl-10 pr-10 border border-gray-300 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
              >
                <option value="">Choose a demo user...</option>
                {demoUsers.map((user) => (
                  <option key={user.id} value={user.username}>
                    {user.first_name} {user.last_name} ({user.role})
                  </option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <ChevronDown className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !selectedUser}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Signing in...
                </div>
              ) : (
                'Sign in as Selected User'
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Quick Demo Access - No Password Required
            </p>
            <div className="mt-2 text-xs text-gray-500">
              <p>Select any user from the dropdown to explore the system</p>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Login
