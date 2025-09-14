import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  BookOpen, 
  TrendingUp, 
  Award, 
  Plus, 
  Edit, 
  Trash2, 
  Download,
  Filter,
  Search
} from 'lucide-react'

interface Assessment {
  id: number
  name: string
  subject: string
  type: string
  max_score: number
  due_date: string
  created_at: string
}

interface Grade {
  id: number
  student_id: number
  student_name: string
  assessment_id: number
  assessment_name: string
  score: number
  max_score: number
  percentage: number
  letter_grade: string
  created_at: string
}

const Grades: React.FC = () => {
  const { user } = useAuth()
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [grades, setGrades] = useState<Grade[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showGradeModal, setShowGradeModal] = useState(false)
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSubject, setFilterSubject] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // Simulate API calls
      setTimeout(() => {
        setAssessments([
          {
            id: 1,
            name: 'Mathematics Quiz 1',
            subject: 'Mathematics',
            type: 'Quiz',
            max_score: 100,
            due_date: '2024-02-15',
            created_at: '2024-02-01T10:00:00Z'
          },
          {
            id: 2,
            name: 'English Essay',
            subject: 'English',
            type: 'Assignment',
            max_score: 50,
            due_date: '2024-02-20',
            created_at: '2024-02-05T14:30:00Z'
          },
          {
            id: 3,
            name: 'Science Test',
            subject: 'Science',
            type: 'Test',
            max_score: 80,
            due_date: '2024-02-25',
            created_at: '2024-02-10T09:15:00Z'
          }
        ])

        setGrades([
          {
            id: 1,
            student_id: 1,
            student_name: 'John Doe',
            assessment_id: 1,
            assessment_name: 'Mathematics Quiz 1',
            score: 85,
            max_score: 100,
            percentage: 85,
            letter_grade: 'B+',
            created_at: '2024-02-15T10:30:00Z'
          },
          {
            id: 2,
            student_id: 2,
            student_name: 'Jane Smith',
            assessment_id: 1,
            assessment_name: 'Mathematics Quiz 1',
            score: 92,
            max_score: 100,
            percentage: 92,
            letter_grade: 'A-',
            created_at: '2024-02-15T10:30:00Z'
          },
          {
            id: 3,
            student_id: 1,
            student_name: 'John Doe',
            assessment_id: 2,
            assessment_name: 'English Essay',
            score: 45,
            max_score: 50,
            percentage: 90,
            letter_grade: 'A-',
            created_at: '2024-02-20T14:45:00Z'
          }
        ])

        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const getGradeColor = (letterGrade: string) => {
    switch (letterGrade) {
      case 'A+':
      case 'A':
      case 'A-':
        return 'bg-green-100 text-green-800'
      case 'B+':
      case 'B':
      case 'B-':
        return 'bg-blue-100 text-blue-800'
      case 'C+':
      case 'C':
      case 'C-':
        return 'bg-yellow-100 text-yellow-800'
      case 'D+':
      case 'D':
      case 'D-':
        return 'bg-orange-100 text-orange-800'
      case 'F':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Quiz':
        return 'bg-blue-100 text-blue-800'
      case 'Test':
        return 'bg-red-100 text-red-800'
      case 'Assignment':
        return 'bg-green-100 text-green-800'
      case 'Project':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredAssessments = assessments.filter(assessment => {
    const matchesSearch = assessment.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assessment.subject.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = !filterSubject || assessment.subject === filterSubject
    return matchesSearch && matchesFilter
  })

  const subjects = [...new Set(assessments.map(a => a.subject))]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Grades & Assessments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage student grades and academic assessments
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Assessment
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-blue-500">
                  <BookOpen className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Assessments
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{assessments.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-green-500">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Average Grade
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {grades.length > 0 ? 
                      (grades.reduce((sum, grade) => sum + grade.percentage, 0) / grades.length).toFixed(1) + '%' 
                      : 'N/A'
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-purple-500">
                  <Award className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Grades Recorded
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{grades.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-orange-500">
                  <Filter className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Subjects
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{subjects.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Assessments
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Search by name or subject..."
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Subject
              </label>
              <select
                value={filterSubject}
                onChange={(e) => setFilterSubject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Subjects</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Assessments Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Assessments
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assessment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Max Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAssessments.map((assessment) => (
                  <tr key={assessment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {assessment.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assessment.subject}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(assessment.type)}`}>
                        {assessment.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assessment.max_score}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(assessment.due_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => {
                          setSelectedAssessment(assessment)
                          setShowGradeModal(true)
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        <Download className="h-4 w-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Recent Grades */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Grades
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assessment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Grade
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {grades.slice(0, 10).map((grade) => (
                  <tr key={grade.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {grade.student_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {grade.assessment_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {grade.score}/{grade.max_score}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeColor(grade.letter_grade)}`}>
                        {grade.letter_grade} ({grade.percentage}%)
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(grade.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Grades
