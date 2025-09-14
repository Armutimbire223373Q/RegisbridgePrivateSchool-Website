import React, { useState, useEffect } from 'react'
import { 
  Save, 
  Upload, 
  Image, 
  Type, 
  Settings, 
  Eye,
  Plus,
  Trash2,
  Edit,
  X
} from 'lucide-react'

interface HomepageContent {
  hero_title: string
  hero_subtitle: string
  hero_image: string
  about_title: string
  about_content: string
  about_image: string
  programs: Array<{
    id?: number
    title: string
    description: string
    icon: string
  }>
  stats: Array<{
    id?: number
    number: string
    label: string
  }>
  testimonials: Array<{
    id?: number
    name: string
    role: string
    content: string
    image: string
  }>
}

const HomepageManagement: React.FC = () => {
  const [content, setContent] = useState<HomepageContent>({
    hero_title: '',
    hero_subtitle: '',
    hero_image: '',
    about_title: '',
    about_content: '',
    about_image: '',
    programs: [],
    stats: [],
    testimonials: []
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('hero')

  useEffect(() => {
    fetchHomepageContent()
  }, [])

  const fetchHomepageContent = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setContent({
          hero_title: 'Welcome to Regisbridge Private School',
          hero_subtitle: 'Primary & Secondary Education with Boarding Services',
          hero_image: '/api/placeholder/800/400',
          about_title: 'About Regisbridge Private School',
          about_content: 'Regisbridge Private School is a premier educational institution offering both primary and secondary education with comprehensive boarding services...',
          about_image: '/api/placeholder/600/400',
          programs: [
            { id: 1, title: 'Academic Excellence', description: 'Rigorous curriculum designed to challenge and inspire students', icon: 'book' },
            { id: 2, title: 'Character Development', description: 'Building strong moral values and ethical leadership', icon: 'award' },
            { id: 3, title: 'Extracurricular Activities', description: 'Sports, arts, and clubs for well-rounded development', icon: 'users' }
          ],
          stats: [
            { id: 1, number: '500+', label: 'Students' },
            { id: 2, number: '50+', label: 'Teachers' },
            { id: 3, number: '95%', label: 'Pass Rate' },
            { id: 4, number: '25+', label: 'Years Experience' }
          ],
          testimonials: [
            { id: 1, name: 'Sarah Johnson', role: 'Parent', content: 'Regisbridge has transformed my child\'s learning experience...', image: '/api/placeholder/100/100' },
            { id: 2, name: 'Michael Brown', role: 'Alumni', content: 'The education I received at Regisbridge prepared me for success...', image: '/api/placeholder/100/100' }
          ]
        })
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching homepage content:', error)
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      alert('Homepage content saved successfully!')
    } catch (error) {
      console.error('Error saving content:', error)
      alert('Error saving content')
    } finally {
      setSaving(false)
    }
  }

  const addProgram = () => {
    setContent(prev => ({
      ...prev,
      programs: [...prev.programs, { title: '', description: '', icon: 'book' }]
    }))
  }

  const removeProgram = (index: number) => {
    setContent(prev => ({
      ...prev,
      programs: prev.programs.filter((_, i) => i !== index)
    }))
  }

  const updateProgram = (index: number, field: string, value: string) => {
    setContent(prev => ({
      ...prev,
      programs: prev.programs.map((program, i) => 
        i === index ? { ...program, [field]: value } : program
      )
    }))
  }

  const addStat = () => {
    setContent(prev => ({
      ...prev,
      stats: [...prev.stats, { number: '', label: '' }]
    }))
  }

  const removeStat = (index: number) => {
    setContent(prev => ({
      ...prev,
      stats: prev.stats.filter((_, i) => i !== index)
    }))
  }

  const updateStat = (index: number, field: string, value: string) => {
    setContent(prev => ({
      ...prev,
      stats: prev.stats.map((stat, i) => 
        i === index ? { ...stat, [field]: value } : stat
      )
    }))
  }

  const addTestimonial = () => {
    setContent(prev => ({
      ...prev,
      testimonials: [...prev.testimonials, { name: '', role: '', content: '', image: '' }]
    }))
  }

  const removeTestimonial = (index: number) => {
    setContent(prev => ({
      ...prev,
      testimonials: prev.testimonials.filter((_, i) => i !== index)
    }))
  }

  const updateTestimonial = (index: number, field: string, value: string) => {
    setContent(prev => ({
      ...prev,
      testimonials: prev.testimonials.map((testimonial, i) => 
        i === index ? { ...testimonial, [field]: value } : testimonial
      )
    }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const tabs = [
    { id: 'hero', name: 'Hero Section', icon: Image },
    { id: 'about', name: 'About Section', icon: Type },
    { id: 'programs', name: 'Programs', icon: Settings },
    { id: 'stats', name: 'Statistics', icon: Settings },
    { id: 'testimonials', name: 'Testimonials', icon: Settings }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Homepage Management</h1>
          <p className="text-gray-600">Manage Regisbridge Private School's homepage content</p>
        </div>
        <div className="flex space-x-4">
          <button className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Hero Section */}
      {activeTab === 'hero' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Hero Section</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hero Title
                  </label>
                  <input
                    type="text"
                    value={content.hero_title}
                    onChange={(e) => setContent(prev => ({ ...prev, hero_title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter hero title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hero Subtitle
                  </label>
                  <textarea
                    value={content.hero_subtitle}
                    onChange={(e) => setContent(prev => ({ ...prev, hero_subtitle: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter hero subtitle"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hero Image
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <img
                    src={content.hero_image}
                    alt="Hero preview"
                    className="mx-auto h-32 w-auto rounded-lg"
                  />
                  <button className="mt-4 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                    <Upload className="h-4 w-4 mr-2" />
                    Change Image
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* About Section */}
      {activeTab === 'about' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">About Section</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    About Title
                  </label>
                  <input
                    type="text"
                    value={content.about_title}
                    onChange={(e) => setContent(prev => ({ ...prev, about_title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter about title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    About Content
                  </label>
                  <textarea
                    value={content.about_content}
                    onChange={(e) => setContent(prev => ({ ...prev, about_content: e.target.value }))}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter about content"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  About Image
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <img
                    src={content.about_image}
                    alt="About preview"
                    className="mx-auto h-32 w-auto rounded-lg"
                  />
                  <button className="mt-4 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                    <Upload className="h-4 w-4 mr-2" />
                    Change Image
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Programs Section */}
      {activeTab === 'programs' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Programs</h3>
              <button
                onClick={addProgram}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Program
              </button>
            </div>
            <div className="space-y-4">
              {content.programs.map((program, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="font-medium text-gray-900">Program {index + 1}</h4>
                    <button
                      onClick={() => removeProgram(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Title
                      </label>
                      <input
                        type="text"
                        value={program.title}
                        onChange={(e) => updateProgram(index, 'title', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Program title"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Icon
                      </label>
                      <select
                        value={program.icon}
                        onChange={(e) => updateProgram(index, 'icon', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="book">Book</option>
                        <option value="award">Award</option>
                        <option value="users">Users</option>
                        <option value="star">Star</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <textarea
                        value={program.description}
                        onChange={(e) => updateProgram(index, 'description', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Program description"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Statistics Section */}
      {activeTab === 'stats' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Statistics</h3>
              <button
                onClick={addStat}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Statistic
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {content.stats.map((stat, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">Stat {index + 1}</h4>
                    <button
                      onClick={() => removeStat(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={stat.number}
                      onChange={(e) => updateStat(index, 'number', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Number (e.g., 500+)"
                    />
                    <input
                      type="text"
                      value={stat.label}
                      onChange={(e) => updateStat(index, 'label', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Label (e.g., Students)"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Testimonials Section */}
      {activeTab === 'testimonials' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Testimonials</h3>
              <button
                onClick={addTestimonial}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Testimonial
              </button>
            </div>
            <div className="space-y-4">
              {content.testimonials.map((testimonial, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="font-medium text-gray-900">Testimonial {index + 1}</h4>
                    <button
                      onClick={() => removeTestimonial(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Name
                      </label>
                      <input
                        type="text"
                        value={testimonial.name}
                        onChange={(e) => updateTestimonial(index, 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Person's name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Role
                      </label>
                      <input
                        type="text"
                        value={testimonial.role}
                        onChange={(e) => updateTestimonial(index, 'role', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Person's role"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Testimonial
                      </label>
                      <textarea
                        value={testimonial.content}
                        onChange={(e) => updateTestimonial(index, 'content', e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Testimonial content"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Image URL
                      </label>
                      <input
                        type="text"
                        value={testimonial.image}
                        onChange={(e) => updateTestimonial(index, 'image', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Image URL"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HomepageManagement
