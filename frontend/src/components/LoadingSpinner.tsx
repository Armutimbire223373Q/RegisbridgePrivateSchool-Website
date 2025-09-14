import React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  text?: string
  fullScreen?: boolean
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text = 'Loading...', 
  fullScreen = false 
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
    xl: 'h-24 w-24'
  }

  const containerClasses = fullScreen 
    ? 'min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100'
    : 'flex items-center justify-center p-4'

  return (
    <div className={containerClasses}>
      <div className="text-center">
        {/* School Logo/Icon */}
        <div className="mb-6">
          <div className={`${sizeClasses[size]} mx-auto bg-blue-600 rounded-full flex items-center justify-center shadow-lg`}>
            <svg 
              className="w-1/2 h-1/2 text-white" 
              fill="currentColor" 
              viewBox="0 0 24 24"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
          </div>
        </div>

        {/* Animated Spinner */}
        <div className="relative">
          <div className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto`}></div>
          <div className={`${sizeClasses[size]} border-4 border-transparent border-t-blue-400 rounded-full animate-spin mx-auto absolute top-0 left-0`} style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>

        {/* Loading Text */}
        <div className="mt-4">
          <p className="text-blue-600 font-semibold text-lg">{text}</p>
          <div className="flex justify-center mt-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>

        {/* School Name */}
        {fullScreen && (
          <div className="mt-8">
            <h1 className="text-2xl font-bold text-blue-600">Regisbridge College</h1>
            <p className="text-gray-600 mt-2">Excellence in Education, Character, and Leadership</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LoadingSpinner
