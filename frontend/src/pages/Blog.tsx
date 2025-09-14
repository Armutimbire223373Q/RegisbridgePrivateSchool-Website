import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, User, Tag, Search, Filter } from 'lucide-react'

interface BlogPost {
  id: number
  title: string
  slug: string
  excerpt: string
  content: string
  featured_image: string
  published_at: string
  author: {
    first_name: string
    last_name: string
  }
  category: string
  tags: string[]
  view_count: number
}

const Blog: React.FC = () => {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedTag, setSelectedTag] = useState('')

  useEffect(() => {
    fetchBlogPosts()
  }, [])

  const fetchBlogPosts = async () => {
    try {
      // Simulate API call
      setTimeout(() => {
        setPosts([
          {
            id: 1,
            title: "New Academic Year Begins",
            slug: "new-academic-year-begins",
            excerpt: "We're excited to welcome students back for another year of learning and growth.",
            content: "Full content here...",
            featured_image: "/api/placeholder/400/250",
            published_at: "2024-01-15T10:00:00Z",
            author: { first_name: "Admin", last_name: "User" },
            category: "NEWS",
            tags: ["academic", "announcement"],
            view_count: 150
          },
          {
            id: 2,
            title: "Sports Day Success",
            slug: "sports-day-success",
            excerpt: "Our annual sports day was a huge success with record participation.",
            content: "Full content here...",
            featured_image: "/api/placeholder/400/250",
            published_at: "2024-01-10T14:30:00Z",
            author: { first_name: "Sports", last_name: "Coordinator" },
            category: "EVENTS",
            tags: ["sports", "events"],
            view_count: 89
          },
          {
            id: 3,
            title: "Science Fair Winners",
            slug: "science-fair-winners",
            excerpt: "Congratulations to our students who won awards at the regional science fair.",
            content: "Full content here...",
            featured_image: "/api/placeholder/400/250",
            published_at: "2024-01-05T09:15:00Z",
            author: { first_name: "Science", last_name: "Department" },
            category: "ACADEMIC",
            tags: ["science", "achievement"],
            view_count: 203
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching blog posts:', error)
      setLoading(false)
    }
  }

  const categories = ['ALL', 'NEWS', 'EVENTS', 'ANNOUNCEMENTS', 'ACADEMIC', 'SPORTS']
  const tags = ['academic', 'announcement', 'sports', 'events', 'science', 'achievement']

  const filteredPosts = posts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === '' || post.category === selectedCategory
    const matchesTag = selectedTag === '' || post.tags.includes(selectedTag)
    
    return matchesSearch && matchesCategory && matchesTag
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                Regisbridge College
              </Link>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Link to="/" className="text-gray-900 hover:text-blue-600">Home</Link>
              <Link to="/blog" className="text-blue-600 font-semibold">Blog</Link>
              <Link to="/admissions" className="text-gray-900 hover:text-blue-600">Admissions</Link>
              <Link to="/login" className="text-gray-900 hover:text-blue-600">Portal</Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">School News & Updates</h1>
          <p className="text-xl text-gray-600">Stay informed about the latest happenings at Regisbridge College</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search posts..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Filter className="h-5 w-5 text-gray-400" />
              </div>
              <select
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                {categories.slice(1).map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            {/* Tag Filter */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Tag className="h-5 w-5 text-gray-400" />
              </div>
              <select
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedTag}
                onChange={(e) => setSelectedTag(e.target.value)}
              >
                <option value="">All Tags</option>
                {tags.map(tag => (
                  <option key={tag} value={tag}>{tag}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Blog Posts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredPosts.map((post) => (
            <article key={post.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-lg transition-shadow">
              <img
                src={post.featured_image}
                alt={post.title}
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                    {post.category}
                  </span>
                  <span className="ml-2 text-sm text-gray-500">
                    {new Date(post.published_at).toLocaleDateString()}
                  </span>
                </div>
                
                <h2 className="text-xl font-semibold text-gray-900 mb-3">
                  <Link to={`/blog/${post.slug}`} className="hover:text-blue-600">
                    {post.title}
                  </Link>
                </h2>
                
                <p className="text-gray-600 mb-4">{post.excerpt}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-sm text-gray-500">
                    <User className="h-4 w-4 mr-1" />
                    {post.author.first_name} {post.author.last_name}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {post.view_count} views
                  </div>
                </div>
                
                <div className="mt-4 flex flex-wrap gap-2">
                  {post.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>

        {filteredPosts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No posts found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Blog
