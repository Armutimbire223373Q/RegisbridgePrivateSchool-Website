import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import { 
  Calendar, 
  Users, 
  BookOpen, 
  Award, 
  Phone, 
  Mail, 
  MapPin, 
  Clock,
  ChevronRight,
  Star,
  Quote,
  Play,
  Facebook,
  Twitter,
  Instagram,
  Linkedin
} from 'lucide-react'

interface BlogPost {
  id: number
  title: string
  excerpt: string
  featured_image: string
  published_at: string
  author: {
    first_name: string
    last_name: string
  }
  category: string
}

interface Event {
  id: number
  title: string
  description: string
  start_date: string
  location: string
  event_type: string
}

interface HomepageContent {
  hero_title: string
  hero_subtitle: string
  hero_image: string
  about_title: string
  about_content: string
  about_image: string
  programs: Array<{
    title: string
    description: string
    icon: string
  }>
  stats: Array<{
    number: string
    label: string
  }>
  testimonials: Array<{
    name: string
    role: string
    content: string
    image: string
  }>
}

const PublicHomepage: React.FC = () => {
  const [homepageContent, setHomepageContent] = useState<HomepageContent | null>(null)
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHomepageData()
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const fetchHomepageData = async () => {
    try {
      // Simulate API calls - in real app, these would be actual API endpoints
      setTimeout(() => {
        setHomepageContent({
          hero_title: "Welcome to Regisbridge College",
          hero_subtitle: "Excellence in Education, Character, and Leadership",
          hero_image: "/api/placeholder/800/400",
          about_title: "About Regisbridge College",
          about_content: "Regisbridge College is a premier educational institution committed to providing world-class education that nurtures academic excellence, character development, and leadership skills. Our holistic approach ensures students are prepared for success in an ever-changing world.",
          about_image: "/api/placeholder/600/400",
          programs: [
            {
              title: "Academic Excellence",
              description: "Rigorous curriculum designed to challenge and inspire students",
              icon: "book"
            },
            {
              title: "Character Development",
              description: "Building strong moral values and ethical leadership",
              icon: "award"
            },
            {
              title: "Extracurricular Activities",
              description: "Sports, arts, and clubs for well-rounded development",
              icon: "users"
            }
          ],
          stats: [
            { number: "500+", label: "Students" },
            { number: "50+", label: "Teachers" },
            { number: "95%", label: "Pass Rate" },
            { number: "25+", label: "Years Experience" }
          ],
          testimonials: [
            {
              name: "Sarah Johnson",
              role: "Parent",
              content: "Regisbridge has transformed my child's learning experience. The teachers are dedicated and the environment is nurturing.",
              image: "/api/placeholder/100/100"
            },
            {
              name: "Michael Brown",
              role: "Alumni",
              content: "The education I received at Regisbridge prepared me for success in university and beyond.",
              image: "/api/placeholder/100/100"
            }
          ]
        })
        
        setBlogPosts([
          {
            id: 1,
            title: "New Academic Year Begins",
            excerpt: "We're excited to welcome students back for another year of learning and growth.",
            featured_image: "/api/placeholder/400/250",
            published_at: "2024-01-15",
            author: { first_name: "Admin", last_name: "User" },
            category: "NEWS"
          },
          {
            id: 2,
            title: "Sports Day Success",
            excerpt: "Our annual sports day was a huge success with record participation.",
            featured_image: "/api/placeholder/400/250",
            published_at: "2024-01-10",
            author: { first_name: "Sports", last_name: "Coordinator" },
            category: "EVENTS"
          }
        ])
        
        setEvents([
          {
            id: 1,
            title: "Parent-Teacher Conference",
            description: "Meet with teachers to discuss your child's progress",
            start_date: "2024-02-15",
            location: "Main Hall",
            event_type: "academic"
          },
          {
            id: 2,
            title: "Science Fair",
            description: "Students showcase their innovative science projects",
            start_date: "2024-02-20",
            location: "Science Lab",
            event_type: "academic"
          }
        ])
        
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching homepage data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner size="xl" text="Loading Regisbridge College..." fullScreen={true} />
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">Regisbridge Private School</h1>
                <p className="text-sm text-gray-600">Primary & Secondary Education with Boarding</p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-8">
              <button onClick={() => scrollToSection('home')} className="text-gray-900 hover:text-blue-600 cursor-pointer">Home</button>
              <button onClick={() => scrollToSection('about')} className="text-gray-900 hover:text-blue-600 cursor-pointer">About</button>
              <button onClick={() => scrollToSection('programs')} className="text-gray-900 hover:text-blue-600 cursor-pointer">Programs</button>
              <button onClick={() => scrollToSection('news')} className="text-gray-900 hover:text-blue-600 cursor-pointer">News</button>
              <button onClick={() => scrollToSection('contact')} className="text-gray-900 hover:text-blue-600 cursor-pointer">Contact</button>
            </nav>
            <div className="flex space-x-4">
              <Link
                to="/login"
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Student Portal
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section id="home" className="relative bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                {homepageContent?.hero_title || "Welcome to Regisbridge Private School"}
              </h1>
              <p className="text-xl mb-8 text-blue-100">
                {homepageContent?.hero_subtitle || "Excellence in Primary & Secondary Education with Boarding Services"}
              </p>
              <div className="flex space-x-4">
                <Link
                  to="/admissions"
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Apply Now
                </Link>
                <button 
                  onClick={() => scrollToSection('about')}
                  className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
                >
                  Learn More
                </button>
              </div>
            </div>
            <div className="relative">
              <img
                src={homepageContent?.hero_image || "/api/placeholder/600/400"}
                alt="Regisbridge Private School"
                className="rounded-lg shadow-2xl"
              />
              <div className="absolute inset-0 bg-blue-600 bg-opacity-20 rounded-lg"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {homepageContent?.stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                {homepageContent?.about_title || "About Regisbridge Private School"}
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                {homepageContent?.about_content || "Regisbridge Private School is a premier educational institution offering both primary and secondary education with comprehensive boarding services. We are committed to providing world-class education that nurtures academic excellence, character development, and leadership skills. Our holistic approach ensures students are prepared for success in an ever-changing world."}
              </p>
              <div className="flex space-x-4">
                <button 
                  onClick={() => scrollToSection('programs')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
                >
                  Learn More
                </button>
                <button 
                  onClick={() => scrollToSection('contact')}
                  className="border border-blue-600 text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50"
                >
                  Take a Tour
                </button>
              </div>
            </div>
            <div>
              <img
                src={homepageContent?.about_image || "/api/placeholder/600/400"}
                alt="About Regisbridge Private School"
                className="rounded-lg shadow-lg"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Programs Section */}
      <section id="programs" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Programs</h2>
            <p className="text-lg text-gray-600">Primary & Secondary Education with Boarding Services</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {homepageContent?.programs.map((program, index) => (
              <div key={index} className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                  {program.icon === 'book' && <BookOpen className="h-8 w-8 text-blue-600" />}
                  {program.icon === 'award' && <Award className="h-8 w-8 text-blue-600" />}
                  {program.icon === 'users' && <Users className="h-8 w-8 text-blue-600" />}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{program.title}</h3>
                <p className="text-gray-600">{program.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* News Section */}
      <section id="news" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Latest News</h2>
            <p className="text-lg text-gray-600">Stay updated with our latest announcements</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {blogPosts.map((post) => (
              <article key={post.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
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
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h3>
                  <p className="text-gray-600 mb-4">{post.excerpt}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      By {post.author.first_name} {post.author.last_name}
                    </span>
                    <button className="text-blue-600 hover:text-blue-800 font-semibold">
                      Read More <ChevronRight className="h-4 w-4 inline ml-1" />
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Events Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Upcoming Events</h2>
            <p className="text-lg text-gray-600">Don't miss our exciting events</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {events.map((event) => (
              <div key={event.id} className="bg-white p-6 rounded-lg shadow-lg">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Calendar className="h-8 w-8 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{event.title}</h3>
                    <p className="text-gray-600 mb-4">{event.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {new Date(event.start_date).toLocaleDateString()}
                      </div>
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {event.location}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">What People Say</h2>
            <p className="text-lg text-gray-600">Hear from our community</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {homepageContent?.testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white p-8 rounded-lg shadow-lg">
                <div className="flex items-center mb-4">
                  <Quote className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-gray-600 mb-6 italic">"{testimonial.content}"</p>
                <div className="flex items-center">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-500">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Contact Us</h2>
            <p className="text-lg text-gray-600">Get in touch with us</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Phone className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Phone</h3>
              <p className="text-gray-600">+254 700 000 000</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Mail className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Email</h3>
              <p className="text-gray-600">info@regisbridge.edu</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <MapPin className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Address</h3>
              <p className="text-gray-600">Nairobi, Kenya</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Regisbridge College</h3>
              <p className="text-gray-400 mb-4">
                Excellence in Education, Character, and Leadership
              </p>
              <div className="flex space-x-4">
                <a href="https://facebook.com/regisbridge" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white cursor-pointer">
                  <Facebook className="h-6 w-6" />
                </a>
                <a href="https://twitter.com/regisbridge" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white cursor-pointer">
                  <Twitter className="h-6 w-6" />
                </a>
                <a href="https://instagram.com/regisbridge" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white cursor-pointer">
                  <Instagram className="h-6 w-6" />
                </a>
                <a href="https://linkedin.com/company/regisbridge" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white cursor-pointer">
                  <Linkedin className="h-6 w-6" />
                </a>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li><button onClick={() => scrollToSection('about')} className="text-gray-400 hover:text-white cursor-pointer">About</button></li>
                <li><button onClick={() => scrollToSection('programs')} className="text-gray-400 hover:text-white cursor-pointer">Programs</button></li>
                <li><button onClick={() => scrollToSection('news')} className="text-gray-400 hover:text-white cursor-pointer">News</button></li>
                <li><button onClick={() => scrollToSection('contact')} className="text-gray-400 hover:text-white cursor-pointer">Contact</button></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Admissions</h3>
              <ul className="space-y-2">
                <li><Link to="/admissions" className="text-gray-400 hover:text-white cursor-pointer">Apply Now</Link></li>
                <li><Link to="/admissions" className="text-gray-400 hover:text-white cursor-pointer">Requirements</Link></li>
                <li><Link to="/login" className="text-gray-400 hover:text-white cursor-pointer">Fees</Link></li>
                <li><Link to="/admissions" className="text-gray-400 hover:text-white cursor-pointer">Scholarships</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact Info</h3>
              <div className="space-y-2 text-gray-400">
                <p>+254 700 000 000</p>
                <p>info@regisbridge.edu</p>
                <p>Nairobi, Kenya</p>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Regisbridge Private School. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default PublicHomepage
