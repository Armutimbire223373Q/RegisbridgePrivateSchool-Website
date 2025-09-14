import React, { useState, useEffect } from 'react'
import { 
  Download, 
  FileText, 
  BarChart3, 
  PieChart, 
  TrendingUp,
  Users,
  GraduationCap,
  Calendar,
  CreditCard,
  BookOpen,
  Filter,
  RefreshCw
} from 'lucide-react'

interface ReportData {
  id: string
  title: string
  description: string
  type: 'attendance' | 'academic' | 'financial' | 'inventory' | 'general'
  generated_at: string
  file_size: string
  status: 'ready' | 'generating' | 'error'
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<ReportData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState('')
  const [dateRange, setDateRange] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setReports([
          {
            id: '1',
            title: 'Monthly Attendance Report',
            description: 'Student attendance summary for January 2024',
            type: 'attendance',
            generated_at: '2024-01-31T10:00:00Z',
            file_size: '2.3 MB',
            status: 'ready'
          },
          {
            id: '2',
            title: 'Academic Performance Report',
            description: 'Grade analysis and student performance metrics',
            type: 'academic',
            generated_at: '2024-01-30T14:30:00Z',
            file_size: '1.8 MB',
            status: 'ready'
          },
          {
            id: '3',
            title: 'Financial Summary Report',
            description: 'Fee collection and financial overview',
            type: 'financial',
            generated_at: '2024-01-29T09:15:00Z',
            file_size: '3.1 MB',
            status: 'ready'
          },
          {
            id: '4',
            title: 'Inventory Status Report',
            description: 'Current inventory levels and stock analysis',
            type: 'inventory',
            generated_at: '2024-01-28T16:45:00Z',
            file_size: '1.2 MB',
            status: 'ready'
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching reports:', error)
      setLoading(false)
    }
  }

  const generateReport = async (type: string) => {
    setIsGenerating(true)
    
    // Simulate report generation
    setTimeout(() => {
      const newReport: ReportData = {
        id: Date.now().toString(),
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Report`,
        description: `Generated ${type} report for ${new Date().toLocaleDateString()}`,
        type: type as any,
        generated_at: new Date().toISOString(),
        file_size: '1.5 MB',
        status: 'ready'
      }
      
      setReports([newReport, ...reports])
      setIsGenerating(false)
    }, 3000)
  }

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'attendance':
        return <Calendar className="h-6 w-6" />
      case 'academic':
        return <BookOpen className="h-6 w-6" />
      case 'financial':
        return <CreditCard className="h-6 w-6" />
      case 'inventory':
        return <BarChart3 className="h-6 w-6" />
      default:
        return <FileText className="h-6 w-6" />
    }
  }

  const getReportColor = (type: string) => {
    switch (type) {
      case 'attendance':
        return 'bg-blue-500'
      case 'academic':
        return 'bg-green-500'
      case 'financial':
        return 'bg-purple-500'
      case 'inventory':
        return 'bg-orange-500'
      default:
        return 'bg-gray-500'
    }
  }

  const filteredReports = reports.filter(report => 
    selectedType === '' || report.type === selectedType
  )

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
          <h1 className="text-2xl font-semibold text-gray-900">Reports & Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            Generate and download comprehensive reports for school management
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-blue-500">
                  <Users className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Students
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">485</dd>
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
                  <GraduationCap className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Teachers
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">52</dd>
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
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Attendance Rate
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">94.2%</dd>
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
                  <CreditCard className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Fee Collection
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">87.5%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Generate Reports Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Generate New Report</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <button
            onClick={() => generateReport('attendance')}
            disabled={isGenerating}
            className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <div className={`p-3 rounded-md ${getReportColor('attendance')} mr-4`}>
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Attendance Report</div>
              <div className="text-sm text-gray-500">Student attendance analysis</div>
            </div>
          </button>

          <button
            onClick={() => generateReport('academic')}
            disabled={isGenerating}
            className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <div className={`p-3 rounded-md ${getReportColor('academic')} mr-4`}>
              <BookOpen className="h-6 w-6 text-white" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Academic Report</div>
              <div className="text-sm text-gray-500">Grades and performance</div>
            </div>
          </button>

          <button
            onClick={() => generateReport('financial')}
            disabled={isGenerating}
            className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <div className={`p-3 rounded-md ${getReportColor('financial')} mr-4`}>
              <CreditCard className="h-6 w-6 text-white" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Financial Report</div>
              <div className="text-sm text-gray-500">Fee collection summary</div>
            </div>
          </button>

          <button
            onClick={() => generateReport('inventory')}
            disabled={isGenerating}
            className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            <div className={`p-3 rounded-md ${getReportColor('inventory')} mr-4`}>
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Inventory Report</div>
              <div className="text-sm text-gray-500">Stock and supplies</div>
            </div>
          </button>
        </div>

        {isGenerating && (
          <div className="mt-4 flex items-center justify-center">
            <RefreshCw className="h-5 w-5 animate-spin text-blue-600 mr-2" />
            <span className="text-sm text-gray-600">Generating report...</span>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="type" className="block text-sm font-medium text-gray-700">
              Report Type
            </label>
            <select
              id="type"
              name="type"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="">All Types</option>
              <option value="attendance">Attendance</option>
              <option value="academic">Academic</option>
              <option value="financial">Financial</option>
              <option value="inventory">Inventory</option>
            </select>
          </div>
          <div>
            <label htmlFor="dateRange" className="block text-sm font-medium text-gray-700">
              Date Range
            </label>
            <select
              id="dateRange"
              name="dateRange"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            >
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Filter className="h-4 w-4 mr-2" />
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Reports</h3>
          <div className="space-y-4">
            {filteredReports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="flex items-center">
                  <div className={`p-3 rounded-md ${getReportColor(report.type)} mr-4`}>
                    {getReportIcon(report.type)}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{report.title}</div>
                    <div className="text-sm text-gray-500">{report.description}</div>
                    <div className="text-xs text-gray-400">
                      Generated: {new Date(report.generated_at).toLocaleDateString()} • Size: {report.file_size}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    report.status === 'ready' ? 'bg-green-100 text-green-800' :
                    report.status === 'generating' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {report.status}
                  </span>
                  <button
                    disabled={report.status !== 'ready'}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports
