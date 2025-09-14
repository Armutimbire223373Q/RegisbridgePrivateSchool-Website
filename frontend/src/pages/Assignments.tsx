import React, { useState, useEffect } from 'react'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Eye, 
  Upload, 
  Download,
  Clock,
  CheckCircle,
  XCircle,
  FileText,
  Calendar,
  User
} from 'lucide-react'

interface Assignment {
  id: number
  title: string
  description: string
  subject: string
  teacher: string
  due_date: string
  max_score: number
  status: 'DRAFT' | 'PUBLISHED' | 'CLOSED'
  created_at: string
  submissions: number
  total_students: number
}

interface Submission {
  id: number
  assignment_id: number
  student_id: number
  student_name: string
  file_url: string
  file_name: string
  submitted_at: string
  score?: number
  feedback?: string
  status: 'SUBMITTED' | 'GRADED' | 'LATE'
}

const Assignments: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null)
  const [showSubmissionsModal, setShowSubmissionsModal] = useState(false)
  const [newAssignment, setNewAssignment] = useState({
    title: '',
    description: '',
    subject: '',
    due_date: '',
    max_score: 100
  })

  useEffect(() => {
    fetchAssignments()
    fetchSubmissions()
  }, [])

  const fetchAssignments = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setAssignments([
          {
            id: 1,
            title: 'Mathematics Problem Set 1',
            description: 'Solve the following algebraic equations and show your work.',
            subject: 'Mathematics',
            teacher: 'Mr. Johnson',
            due_date: '2024-02-15',
            max_score: 100,
            status: 'PUBLISHED',
            created_at: '2024-01-15T10:00:00Z',
            submissions: 25,
            total_students: 30
          },
          {
            id: 2,
            title: 'English Essay - Climate Change',
            description: 'Write a 500-word essay on the impact of climate change on developing countries.',
            subject: 'English',
            teacher: 'Ms. Smith',
            due_date: '2024-02-20',
            max_score: 100,
            status: 'PUBLISHED',
            created_at: '2024-01-16T14:30:00Z',
            submissions: 18,
            total_students: 30
          },
          {
            id: 3,
            title: 'Science Lab Report',
            description: 'Complete the lab report for the chemistry experiment conducted last week.',
            subject: 'Chemistry',
            teacher: 'Dr. Brown',
            due_date: '2024-02-10',
            max_score: 50,
            status: 'CLOSED',
            created_at: '2024-01-10T09:00:00Z',
            submissions: 28,
            total_students: 30
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching assignments:', error)
      setLoading(false)
    }
  }

  const fetchSubmissions = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setSubmissions([
          {
            id: 1,
            assignment_id: 1,
            student_id: 1,
            student_name: 'Michael Brown',
            file_url: '/submissions/math_1_brown.pdf',
            file_name: 'math_1_brown.pdf',
            submitted_at: '2024-02-14T15:30:00Z',
            score: 85,
            feedback: 'Good work! Show more steps in problem 3.',
            status: 'GRADED'
          },
          {
            id: 2,
            assignment_id: 1,
            student_id: 2,
            student_name: 'Sarah Johnson',
            file_url: '/submissions/math_1_johnson.pdf',
            file_name: 'math_1_johnson.pdf',
            submitted_at: '2024-02-15T10:00:00Z',
            status: 'SUBMITTED'
          },
          {
            id: 3,
            assignment_id: 2,
            student_id: 3,
            student_name: 'David Wilson',
            file_url: '/submissions/english_2_wilson.pdf',
            file_name: 'english_2_wilson.pdf',
            submitted_at: '2024-02-19T16:45:00Z',
            score: 92,
            feedback: 'Excellent essay! Well-structured and insightful.',
            status: 'GRADED'
          }
        ])
      }, 1000)
    } catch (error) {
      console.error('Error fetching submissions:', error)
    }
  }

  const handleCreateAssignment = async () => {
    const assignment: Assignment = {
      id: Date.now(),
      title: newAssignment.title,
      description: newAssignment.description,
      subject: newAssignment.subject,
      teacher: 'Current Teacher',
      due_date: newAssignment.due_date,
      max_score: newAssignment.max_score,
      status: 'PUBLISHED',
      created_at: new Date().toISOString(),
      submissions: 0,
      total_students: 30
    }

    setAssignments([assignment, ...assignments])
    setShowAddModal(false)
    setNewAssignment({
      title: '',
      description: '',
      subject: '',
      due_date: '',
      max_score: 100
    })
  }

  const handleDeleteAssignment = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this assignment?')) {
      setAssignments(assignments.filter(assignment => assignment.id !== id))
    }
  }

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = 
      assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assignment.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assignment.teacher.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = filterStatus === '' || assignment.status === filterStatus
    
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PUBLISHED':
        return 'bg-green-100 text-green-800'
      case 'DRAFT':
        return 'bg-yellow-100 text-yellow-800'
      case 'CLOSED':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getSubmissionStatusColor = (status: string) => {
    switch (status) {
      case 'GRADED':
        return 'bg-green-100 text-green-800'
      case 'SUBMITTED':
        return 'bg-blue-100 text-blue-800'
      case 'LATE':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

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
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Assignments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage assignments and track submissions
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:w-auto"
            onClick={() => setShowAddModal(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Assignment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search
            </label>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                name="search"
                id="search"
                className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                placeholder="Search assignments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="status"
              name="status"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="PUBLISHED">Published</option>
              <option value="DRAFT">Draft</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Assignments Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assignment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Teacher
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Submissions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAssignments.map((assignment) => (
                  <tr key={assignment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {assignment.title}
                      </div>
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {assignment.description}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assignment.subject}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {assignment.teacher}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                        {new Date(assignment.due_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-1 text-gray-400" />
                        {assignment.submissions}/{assignment.total_students}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(assignment.status)}`}>
                        {assignment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSelectedAssignment(assignment)
                            setShowSubmissionsModal(true)
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedAssignment(assignment)
                            // Handle edit
                          }}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteAssignment(assignment.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create Assignment Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddModal(false)} />
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Create New Assignment
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Title
                    </label>
                    <input
                      type="text"
                      value={newAssignment.title}
                      onChange={(e) => setNewAssignment({ ...newAssignment, title: e.target.value })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Assignment title"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      value={newAssignment.description}
                      onChange={(e) => setNewAssignment({ ...newAssignment, description: e.target.value })}
                      rows={3}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Assignment description"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Subject
                      </label>
                      <input
                        type="text"
                        value={newAssignment.subject}
                        onChange={(e) => setNewAssignment({ ...newAssignment, subject: e.target.value })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        placeholder="Subject"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Max Score
                      </label>
                      <input
                        type="number"
                        value={newAssignment.max_score}
                        onChange={(e) => setNewAssignment({ ...newAssignment, max_score: parseInt(e.target.value) })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        placeholder="100"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Due Date
                    </label>
                    <input
                      type="date"
                      value={newAssignment.due_date}
                      onChange={(e) => setNewAssignment({ ...newAssignment, due_date: e.target.value })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={handleCreateAssignment}
                >
                  Create Assignment
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Submissions Modal */}
      {showSubmissionsModal && selectedAssignment && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowSubmissionsModal(false)} />
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Submissions for "{selectedAssignment.title}"
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Student
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          File
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Submitted
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="relative px-6 py-3">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {submissions.filter(s => s.assignment_id === selectedAssignment.id).map((submission) => (
                        <tr key={submission.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {submission.student_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div className="flex items-center">
                              <FileText className="h-4 w-4 mr-2 text-gray-400" />
                              {submission.file_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(submission.submitted_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {submission.score ? `${submission.score}/${selectedAssignment.max_score}` : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSubmissionStatusColor(submission.status)}`}>
                              {submission.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex space-x-2">
                              <button className="text-blue-600 hover:text-blue-900">
                                <Download className="h-4 w-4" />
                              </button>
                              <button className="text-indigo-600 hover:text-indigo-900">
                                <Edit className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowSubmissionsModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Assignments
