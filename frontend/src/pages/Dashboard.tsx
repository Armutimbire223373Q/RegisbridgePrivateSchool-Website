import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  Users,
  GraduationCap,
  UserCheck,
  BookOpen,
  Calendar,
  CreditCard,
  MessageSquare,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface DashboardStats {
  total_students: number
  total_teachers: number
  total_parents: number
  active_students: number
  total_classes: number
  total_attendance_today: number
  pending_fees: number
  recent_activities: Array<{
    id: number
    type: string
    description: string
    timestamp: string
  }>
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8001/api/v1/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const getRoleDisplayName = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'ADMIN': 'Administrator',
      'TEACHER': 'Teacher',
      'STUDENT': 'Student',
      'PARENT': 'Parent',
      'BOARDING_STAFF': 'Boarding Staff'
    }
    return roleMap[role] || role
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      name: 'Total Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Active Teachers',
      value: stats?.total_teachers || 0,
      icon: GraduationCap,
      color: 'bg-green-500',
      change: '+5%',
      changeType: 'positive'
    },
    {
      name: 'Parents',
      value: stats?.total_parents || 0,
      icon: UserCheck,
      color: 'bg-purple-500',
      change: '+8%',
      changeType: 'positive'
    },
    {
      name: 'Classes',
      value: stats?.total_classes || 0,
      icon: BookOpen,
      color: 'bg-orange-500',
      change: '+2%',
      changeType: 'positive'
    },
    {
      name: 'Attendance Today',
      value: stats?.total_attendance_today || 0,
      icon: Calendar,
      color: 'bg-indigo-500',
      change: '+15%',
      changeType: 'positive'
    },
    {
      name: 'Pending Fees',
      value: `$${stats?.pending_fees || 0}`,
      icon: CreditCard,
      color: 'bg-red-500',
      change: '-3%',
      changeType: 'negative'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <span className="text-xl font-bold text-blue-600">
                  {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                </span>
              </div>
            </div>
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">
                {getGreeting()}, {user?.first_name}!
              </h1>
              <p className="text-gray-600">
                {getRoleDisplayName(user?.role || '')} • Welcome to Regisbridge College Management System
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((card) => (
          <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`p-3 rounded-md ${card.color}`}>
                    <card.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {card.value}
                      </div>
                      <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                        card.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {card.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activities */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Activities
          </h3>
          <div className="flow-root">
            <ul className="-mb-8">
              {stats?.recent_activities?.slice(0, 5).map((activity, index) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {index !== (stats?.recent_activities?.length || 0) - 1 && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                          activity.type === 'success' ? 'bg-green-500' :
                          activity.type === 'warning' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}>
                          {activity.type === 'success' ? (
                            <CheckCircle className="h-5 w-5 text-white" />
                          ) : activity.type === 'warning' ? (
                            <AlertCircle className="h-5 w-5 text-white" />
                          ) : (
                            <Clock className="h-5 w-5 text-white" />
                          )}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">{activity.description}</p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time dateTime={activity.timestamp}>
                            {new Date(activity.timestamp).toLocaleDateString()}
                          </time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300">
              <div>
                <span className="rounded-lg inline-flex p-3 bg-blue-50 text-blue-700 ring-4 ring-white">
                  <Users className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Add Student
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Register a new student
                </p>
              </div>
            </button>

            <button className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300">
              <div>
                <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                  <GraduationCap className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Add Teacher
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Register a new teacher
                </p>
              </div>
            </button>

            <button className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300">
              <div>
                <span className="rounded-lg inline-flex p-3 bg-purple-50 text-purple-700 ring-4 ring-white">
                  <Calendar className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Mark Attendance
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Record daily attendance
                </p>
              </div>
            </button>

            <button className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300">
              <div>
                <span className="rounded-lg inline-flex p-3 bg-orange-50 text-orange-700 ring-4 ring-white">
                  <MessageSquare className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-8">
                <h3 className="text-lg font-medium">
                  <span className="absolute inset-0" aria-hidden="true" />
                  Send Message
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Communicate with users
                </p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
