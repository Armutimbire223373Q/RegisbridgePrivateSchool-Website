import React, { useEffect, useState } from 'react'
import { GraduationCap, BookOpen, Users, Award, Shield, Building } from 'lucide-react'

interface LoadingScreenProps {
  isLoading: boolean
  onComplete?: () => void
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ isLoading, onComplete }) => {
  const [progress, setProgress] = useState(0)
  const [currentText, setCurrentText] = useState('Initializing...')

  const loadingSteps = [
    { text: 'Initializing...', duration: 500 },
    { text: 'Loading Database...', duration: 800 },
    { text: 'Preparing Interface...', duration: 600 },
    { text: 'Setting up Security...', duration: 700 },
    { text: 'Finalizing...', duration: 400 }
  ]

  useEffect(() => {
    if (!isLoading) return

    let stepIndex = 0
    let currentProgress = 0
    const totalSteps = loadingSteps.length
    const progressPerStep = 100 / totalSteps

    const updateProgress = () => {
      if (stepIndex < totalSteps) {
        const step = loadingSteps[stepIndex]
        setCurrentText(step.text)
        
        // Animate progress bar
        const targetProgress = (stepIndex + 1) * progressPerStep
        const progressInterval = setInterval(() => {
          currentProgress += 2
          setProgress(Math.min(currentProgress, targetProgress))
          
          if (currentProgress >= targetProgress) {
            clearInterval(progressInterval)
            stepIndex++
            setTimeout(updateProgress, 100)
          }
        }, 20)
      } else {
        // Complete loading
        setTimeout(() => {
          onComplete?.()
        }, 500)
      }
    }

    updateProgress()
  }, [isLoading, onComplete])

  if (!isLoading) return null

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-gray-900 to-blue-900 overflow-hidden">
      {/* 3D Background Elements */}
      <div className="absolute inset-0">
        {/* Floating 3D Shapes */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-blue-600/10 rounded-full animate-pulse transform rotate-45"></div>
        <div className="absolute top-40 right-32 w-24 h-24 bg-slate-600/10 rounded-full animate-bounce transform rotate-12"></div>
        <div className="absolute bottom-32 left-40 w-28 h-28 bg-gray-600/10 rounded-full animate-pulse transform -rotate-12"></div>
        <div className="absolute bottom-20 right-20 w-20 h-20 bg-blue-700/10 rounded-full animate-bounce transform rotate-45"></div>
        
        {/* 3D Grid Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="grid grid-cols-12 grid-rows-12 h-full w-full">
            {Array.from({ length: 144 }).map((_, i) => (
              <div
                key={i}
                className="border border-white/10 transform rotate-45 hover:bg-white/5 transition-all duration-300"
                style={{
                  animationDelay: `${i * 0.1}s`,
                  animation: 'pulse 2s infinite'
                }}
              ></div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        {/* 3D School Logo */}
        <div className="relative mb-12">
          <div className="relative transform perspective-1000">
            {/* 3D Container */}
            <div className="relative w-32 h-32 mx-auto transform-gpu">
              {/* Front Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl shadow-2xl transform translate-z-8 flex items-center justify-center">
                <GraduationCap className="w-16 h-16 text-white" />
              </div>
              
              {/* Back Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl shadow-2xl transform translate-z-0"></div>
              
              {/* Left Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-teal-600 rounded-2xl shadow-2xl transform rotate-y-90 origin-left"></div>
              
              {/* Right Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl shadow-2xl transform -rotate-y-90 origin-right"></div>
              
              {/* Top Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl shadow-2xl transform -rotate-x-90 origin-top"></div>
              
              {/* Bottom Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl shadow-2xl transform rotate-x-90 origin-bottom"></div>
            </div>
          </div>
          
          {/* Rotating Ring */}
          <div className="absolute -inset-4 border-4 border-white/20 rounded-full animate-spin-slow"></div>
          <div className="absolute -inset-6 border-2 border-white/10 rounded-full animate-spin-reverse"></div>
        </div>

        {/* School Name with 3D Effect */}
        <div className="text-center mb-8">
          <h1 className="text-6xl md:text-8xl font-bold text-white mb-4 transform-gpu">
            <span className="inline-block transform-gpu hover:scale-110 transition-transform duration-300" 
                  style={{ 
                    textShadow: '0 0 20px rgba(255,255,255,0.5), 0 0 40px rgba(59,130,246,0.5)',
                    filter: 'drop-shadow(0 0 10px rgba(59,130,246,0.8))'
                  }}>
              REGISBRIDGE
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-blue-200 font-light tracking-wider">
            College Management System
          </p>
        </div>

        {/* 3D Progress Bar */}
        <div className="w-full max-w-md mb-8">
          <div className="relative">
            {/* Background */}
            <div className="w-full h-4 bg-white/20 rounded-full overflow-hidden shadow-inner">
              {/* Progress Fill with 3D Effect */}
              <div 
                className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
                style={{ width: `${progress}%` }}
              >
                {/* Shine Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 blur-sm opacity-50"></div>
              </div>
            </div>
            
            {/* Progress Percentage */}
            <div className="absolute -top-8 right-0 text-white font-bold text-lg">
              {Math.round(progress)}%
            </div>
          </div>
        </div>

        {/* Loading Text with Typewriter Effect */}
        <div className="text-center">
          <p className="text-lg text-blue-200 font-medium mb-4 min-h-[1.5rem]">
            {currentText}
          </p>
          
          {/* Animated Dots */}
          <div className="flex justify-center space-x-1">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>

        {/* 3D Icons Animation */}
        <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 flex space-x-8">
          <div className="relative group">
            <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-transform duration-300">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div className="absolute inset-0 bg-white/5 rounded-full animate-ping"></div>
          </div>
          
          <div className="relative group">
            <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-transform duration-300">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div className="absolute inset-0 bg-white/5 rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
          </div>
          
          <div className="relative group">
            <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-transform duration-300">
              <Award className="w-6 h-6 text-white" />
            </div>
            <div className="absolute inset-0 bg-white/5 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
          </div>
        </div>
      </div>

      {/* Particle System */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/30 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}
          ></div>
        ))}
      </div>
    </div>
  )
}

export default LoadingScreen
