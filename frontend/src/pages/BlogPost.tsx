import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Calendar, User, Tag, ArrowLeft, Share2, Bookmark } from 'lucide-react'

interface BlogPost {
  id: number
  title: string
  slug: string
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
  meta_title?: string
  meta_description?: string
}

const BlogPost: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  const [post, setPost] = useState<BlogPost | null>(null)
  const [loading, setLoading] = useState(true)
  const [relatedPosts, setRelatedPosts] = useState<BlogPost[]>([])

  useEffect(() => {
    if (slug) {
      fetchBlogPost(slug)
    }
  }, [slug])

  const fetchBlogPost = async (postSlug: string) => {
    try {
      // Simulate API call
      setTimeout(() => {
        setPost({
          id: 1,
          title: "New Academic Year Begins",
          slug: postSlug,
          content: `
            <h2>Welcome to the New Academic Year</h2>
            <p>We are thrilled to welcome all our students, parents, and staff to the new academic year at Regisbridge College. This year promises to be filled with exciting opportunities for growth, learning, and achievement.</p>
            
            <h3>What's New This Year</h3>
            <ul>
              <li>Enhanced STEM curriculum with new laboratory equipment</li>
              <li>Expanded sports facilities including a new swimming pool</li>
              <li>Digital learning platform integration</li>
              <li>New extracurricular activities and clubs</li>
            </ul>
            
            <p>Our commitment to academic excellence remains unwavering, and we look forward to supporting each student in reaching their full potential.</p>
            
            <h3>Important Dates</h3>
            <p>Please mark your calendars for the following important dates:</p>
            <ul>
              <li>Parent-Teacher Conference: February 15, 2024</li>
              <li>Science Fair: February 20, 2024</li>
              <li>Sports Day: March 10, 2024</li>
              <li>Mid-term Break: March 25-29, 2024</li>
            </ul>
            
            <p>We encourage all parents to stay engaged with their child's education and take advantage of the various communication channels we have established.</p>
          `,
          featured_image: "/api/placeholder/800/400",
          published_at: "2024-01-15T10:00:00Z",
          author: { first_name: "Admin", last_name: "User" },
          category: "NEWS",
          tags: ["academic", "announcement"],
          view_count: 150,
          meta_title: "New Academic Year Begins - Regisbridge College",
          meta_description: "Welcome to the new academic year at Regisbridge College with exciting new programs and facilities."
        })
        
        setRelatedPosts([
          {
            id: 2,
            title: "Sports Day Success",
            slug: "sports-day-success",
            content: "Content...",
            featured_image: "/api/placeholder/300/200",
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
            content: "Content...",
            featured_image: "/api/placeholder/300/200",
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
      console.error('Error fetching blog post:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Post Not Found</h1>
          <p className="text-gray-600 mb-4">The blog post you're looking for doesn't exist.</p>
          <Link to="/blog" className="text-blue-600 hover:text-blue-800">
            ← Back to Blog
          </Link>
        </div>
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
              <Link to="/blog" className="text-gray-900 hover:text-blue-600">Blog</Link>
              <Link to="/admissions" className="text-gray-900 hover:text-blue-600">Admissions</Link>
              <Link to="/login" className="text-gray-900 hover:text-blue-600">Portal</Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Button */}
        <div className="mb-8">
          <Link 
            to="/blog" 
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Blog
          </Link>
        </div>

        {/* Article Header */}
        <article className="bg-white rounded-lg shadow-sm overflow-hidden">
          <img
            src={post.featured_image}
            alt={post.title}
            className="w-full h-64 md:h-96 object-cover"
          />
          
          <div className="p-8">
            {/* Meta Information */}
            <div className="flex items-center mb-6">
              <span className="bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded">
                {post.category}
              </span>
              <span className="ml-4 text-sm text-gray-500">
                {new Date(post.published_at).toLocaleDateString()}
              </span>
            </div>

            {/* Title */}
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              {post.title}
            </h1>

            {/* Author and Stats */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200">
              <div className="flex items-center">
                <User className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-gray-600">
                  By {post.author.first_name} {post.author.last_name}
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-1" />
                  {post.view_count} views
                </div>
                <button className="flex items-center text-sm text-gray-500 hover:text-blue-600">
                  <Share2 className="h-4 w-4 mr-1" />
                  Share
                </button>
                <button className="flex items-center text-sm text-gray-500 hover:text-blue-600">
                  <Bookmark className="h-4 w-4 mr-1" />
                  Save
                </button>
              </div>
            </div>

            {/* Content */}
            <div 
              className="prose prose-lg max-w-none"
              dangerouslySetInnerHTML={{ __html: post.content }}
            />

            {/* Tags */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {post.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-600 text-sm px-3 py-1 rounded-full"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </article>

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Posts</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {relatedPosts.map((relatedPost) => (
                <Link
                  key={relatedPost.id}
                  to={`/blog/${relatedPost.slug}`}
                  className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <img
                    src={relatedPost.featured_image}
                    alt={relatedPost.title}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-6">
                    <div className="flex items-center mb-3">
                      <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                        {relatedPost.category}
                      </span>
                      <span className="ml-2 text-sm text-gray-500">
                        {new Date(relatedPost.published_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {relatedPost.title}
                    </h3>
                    <div className="flex items-center text-sm text-gray-500">
                      <User className="h-4 w-4 mr-1" />
                      {relatedPost.author.first_name} {relatedPost.author.last_name}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BlogPost
