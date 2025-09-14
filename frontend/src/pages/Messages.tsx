import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  MessageCircle, 
  Send, 
  Users, 
  Search, 
  Filter, 
  Paperclip, 
  Smile, 
  MoreVertical,
  Phone,
  Video,
  Star,
  Inbox
} from 'lucide-react'

interface Message {
  id: number
  sender_id: number
  sender_name: string
  sender_role: string
  recipient_id: number
  recipient_name: string
  subject: string
  content: string
  is_read: boolean
  is_starred: boolean
  created_at: string
  thread_id?: number
  attachments?: string[]
}

interface Conversation {
  id: number
  participants: Array<{
    id: number
    name: string
    role: string
    avatar?: string
  }>
  last_message: Message
  unread_count: number
  is_starred: boolean
  is_archived: boolean
}

const Messages: React.FC = () => {
  const { user } = useAuth()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [loading, setLoading] = useState(true)
  const [, setShowCompose] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // Simulate API calls
      setTimeout(() => {
        setConversations([
          {
            id: 1,
            participants: [
              { id: 1, name: 'John Doe', role: 'Student' },
              { id: 2, name: 'Sarah Johnson', role: 'Teacher' }
            ],
            last_message: {
              id: 1,
              sender_id: 2,
              sender_name: 'Sarah Johnson',
              sender_role: 'Teacher',
              recipient_id: 1,
              recipient_name: 'John Doe',
              subject: 'Assignment Submission',
              content: 'Please remember to submit your mathematics assignment by tomorrow.',
              is_read: false,
              is_starred: false,
              created_at: '2024-02-15T14:30:00Z'
            },
            unread_count: 2,
            is_starred: false,
            is_archived: false
          },
          {
            id: 2,
            participants: [
              { id: 1, name: 'John Doe', role: 'Student' },
              { id: 3, name: 'Michael Brown', role: 'Parent' }
            ],
            last_message: {
              id: 2,
              sender_id: 3,
              sender_name: 'Michael Brown',
              sender_role: 'Parent',
              recipient_id: 1,
              recipient_name: 'John Doe',
              subject: 'Parent-Teacher Meeting',
              content: 'I would like to schedule a meeting to discuss your progress.',
              is_read: true,
              is_starred: true,
              created_at: '2024-02-14T10:15:00Z'
            },
            unread_count: 0,
            is_starred: true,
            is_archived: false
          },
          {
            id: 3,
            participants: [
              { id: 1, name: 'John Doe', role: 'Student' },
              { id: 4, name: 'Class 10A', role: 'Group' }
            ],
            last_message: {
              id: 3,
              sender_id: 2,
              sender_name: 'Sarah Johnson',
              sender_role: 'Teacher',
              recipient_id: 4,
              recipient_name: 'Class 10A',
              subject: 'Field Trip Reminder',
              content: 'Don\'t forget about our field trip to the science museum next week!',
              is_read: true,
              is_starred: false,
              created_at: '2024-02-13T16:45:00Z'
            },
            unread_count: 0,
            is_starred: false,
            is_archived: false
          }
        ])

        setMessages([
          {
            id: 1,
            sender_id: 2,
            sender_name: 'Sarah Johnson',
            sender_role: 'Teacher',
            recipient_id: 1,
            recipient_name: 'John Doe',
            subject: 'Assignment Submission',
            content: 'Please remember to submit your mathematics assignment by tomorrow.',
            is_read: false,
            is_starred: false,
            created_at: '2024-02-15T14:30:00Z'
          },
          {
            id: 2,
            sender_id: 1,
            sender_name: 'John Doe',
            sender_role: 'Student',
            recipient_id: 2,
            recipient_name: 'Sarah Johnson',
            subject: 'Re: Assignment Submission',
            content: 'Thank you for the reminder. I will submit it first thing in the morning.',
            is_read: true,
            is_starred: false,
            created_at: '2024-02-15T15:45:00Z'
          }
        ])

        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Student':
        return 'bg-blue-100 text-blue-800'
      case 'Teacher':
        return 'bg-green-100 text-green-800'
      case 'Parent':
        return 'bg-purple-100 text-purple-800'
      case 'Admin':
        return 'bg-red-100 text-red-800'
      case 'Group':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredConversations = conversations.filter(conversation => {
    const matchesSearch = conversation.participants.some(p => 
      p.name.toLowerCase().includes(searchTerm.toLowerCase())
    ) || conversation.last_message.subject.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filterType === 'all' || 
      (filterType === 'unread' && conversation.unread_count > 0) ||
      (filterType === 'starred' && conversation.is_starred) ||
      (filterType === 'archived' && conversation.is_archived)
    
    return matchesSearch && matchesFilter
  })

  const handleSendMessage = () => {
    if (newMessage.trim() && selectedConversation) {
      const message: Message = {
        id: Date.now(),
        sender_id: user?.id || 1,
        sender_name: user?.username || 'You',
        sender_role: user?.role || 'Student',
        recipient_id: selectedConversation.participants[0].id,
        recipient_name: selectedConversation.participants[0].name,
        subject: 'New Message',
        content: newMessage,
        is_read: false,
        is_starred: false,
        created_at: new Date().toISOString()
      }
      
      setMessages(prev => [message, ...prev])
      setNewMessage('')
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
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Messages</h1>
          <p className="mt-2 text-sm text-gray-700">
            Internal messaging system for communication
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowCompose(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Send className="h-4 w-4 mr-2" />
            New Message
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
                  <Inbox className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Messages
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{messages.length}</dd>
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
                  <Send className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Unread Messages
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {conversations.reduce((sum, conv) => sum + conv.unread_count, 0)}
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
                  <Users className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Conversations
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">{conversations.length}</dd>
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
                  <Star className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Starred Messages
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {conversations.filter(c => c.is_starred).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversations List */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Conversations</h3>
                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Filter className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Search and Filter */}
              <div className="space-y-3 mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Search conversations..."
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Messages</option>
                  <option value="unread">Unread</option>
                  <option value="starred">Starred</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              {/* Conversations */}
              <div className="space-y-2">
                {filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => setSelectedConversation(conversation)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedConversation?.id === conversation.id
                        ? 'bg-blue-50 border-2 border-blue-200'
                        : 'hover:bg-gray-50 border-2 border-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {conversation.participants.map(p => p.name).join(', ')}
                          </h4>
                          {conversation.is_starred && (
                            <Star className="h-3 w-3 text-yellow-500 fill-current" />
                          )}
                        </div>
                        <p className="text-sm text-gray-500 truncate">
                          {conversation.last_message.subject}
                        </p>
                        <p className="text-xs text-gray-400 truncate">
                          {conversation.last_message.content}
                        </p>
                      </div>
                      <div className="flex flex-col items-end space-y-1">
                        {conversation.unread_count > 0 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {conversation.unread_count}
                          </span>
                        )}
                        <span className="text-xs text-gray-400">
                          {new Date(conversation.last_message.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg h-96 flex flex-col">
            {selectedConversation ? (
              <>
                {/* Message Header */}
                <div className="px-4 py-3 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">
                          {selectedConversation.participants.map(p => p.name).join(', ')}
                        </h3>
                        <div className="flex space-x-2">
                          {selectedConversation.participants.map((participant, index) => (
                            <span
                              key={index}
                              className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(participant.role)}`}
                            >
                              {participant.role}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Phone className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Video className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <MoreVertical className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.sender_id === user?.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-xs font-medium">{message.sender_name}</span>
                          <span className={`text-xs ${message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'}`}>
                            {message.sender_role}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'}`}>
                          {new Date(message.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="px-4 py-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <Paperclip className="h-4 w-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <Smile className="h-4 w-4" />
                    </button>
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Type a message..."
                    />
                    <button
                      onClick={handleSendMessage}
                      className="p-2 text-blue-600 hover:text-blue-700"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No conversation selected</h3>
                  <p className="text-gray-500">Choose a conversation to start messaging</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Messages