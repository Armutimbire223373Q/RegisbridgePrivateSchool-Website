import React, { useEffect, useState } from 'react'
import { GraduationCap, BookOpen, Users, Award, Shield, Building } from 'lucide-react'

interface SplashScreenProps {
  onComplete: () => void
}

const SplashScreen: React.FC<SplashScreenProps> = ({ onComplete }) => {
  const [currentPhase, setCurrentPhase] = useState(0)
  const [isVisible, setIsVisible] = useState(true)

  const phases = [
    { duration: 2000, text: 'Welcome to Regisbridge' },
    { duration: 1500, text: 'Excellence in Education' },
    { duration: 1500, text: 'Character & Leadership' },
    { duration: 1000, text: 'Loading...' }
  ]

  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPhase < phases.length - 1) {
        setCurrentPhase(currentPhase + 1)
      } else {
        setIsVisible(false)
        setTimeout(onComplete, 500)
      }
    }, phases[currentPhase].duration)

    return () => clearTimeout(timer)
  }, [currentPhase, onComplete])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-gray-900 to-blue-900 overflow-hidden">
      {/* 3D Background */}
      <div className="absolute inset-0">
        {/* Animated 3D Shapes */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-gradient-to-br from-blue-600/10 to-slate-600/10 rounded-full animate-float-3d transform rotate-45"></div>
        <div className="absolute top-1/3 right-1/4 w-48 h-48 bg-gradient-to-br from-gray-600/10 to-blue-700/10 rounded-full animate-float-3d-reverse transform -rotate-12"></div>
        <div className="absolute bottom-1/4 left-1/3 w-56 h-56 bg-gradient-to-br from-slate-600/10 to-gray-700/10 rounded-full animate-float-3d transform rotate-12"></div>
        
        {/* 3D Grid */}
        <div className="absolute inset-0 opacity-5">
          <div className="grid grid-cols-20 grid-rows-20 h-full w-full">
            {Array.from({ length: 400 }).map((_, i) => (
              <div
                key={i}
                className="border border-white/10 transform rotate-45 hover:bg-white/5 transition-all duration-500"
                style={{
                  animationDelay: `${i * 0.02}s`,
                  animation: 'pulse 3s infinite'
                }}
              ></div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        {/* 3D School Logo with Complex Animation */}
        <div className="relative mb-16">
          <div className="relative transform perspective-1000">
            {/* Main 3D Cube */}
            <div className="relative w-40 h-40 mx-auto transform-gpu animate-rotate-3d">
              {/* Front Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 rounded-3xl shadow-2xl transform translate-z-10 flex items-center justify-center border border-blue-500/30">
                <GraduationCap className="w-20 h-20 text-white drop-shadow-lg" />
              </div>
              
              {/* Back Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 rounded-3xl shadow-2xl transform translate-z-0 border border-slate-600/30"></div>
              
              {/* Left Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-gray-600 via-gray-700 to-gray-800 rounded-3xl shadow-2xl transform rotate-y-90 origin-left border border-gray-500/30"></div>
              
              {/* Right Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-700 via-blue-800 to-blue-900 rounded-3xl shadow-2xl transform -rotate-y-90 origin-right border border-blue-600/30"></div>
              
              {/* Top Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 rounded-3xl shadow-2xl transform -rotate-x-90 origin-top border border-slate-500/30"></div>
              
              {/* Bottom Face */}
              <div className="absolute inset-0 bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900 rounded-3xl shadow-2xl transform rotate-x-90 origin-bottom border border-gray-600/30"></div>
            </div>
          </div>
          
          {/* Rotating Rings */}
          <div className="absolute -inset-6 border-4 border-white/20 rounded-full animate-spin-slow"></div>
          <div className="absolute -inset-10 border-2 border-white/10 rounded-full animate-spin-reverse"></div>
          <div className="absolute -inset-14 border border-white/5 rounded-full animate-spin-slow"></div>
          
          {/* Floating Icons */}
          <div className="absolute -top-8 -left-8 w-8 h-8 bg-blue-600/30 rounded-full flex items-center justify-center animate-float border border-blue-500/50">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <div className="absolute -top-8 -right-8 w-8 h-8 bg-slate-600/30 rounded-full flex items-center justify-center animate-float border border-slate-500/50" style={{ animationDelay: '0.5s' }}>
            <Users className="w-4 h-4 text-white" />
          </div>
          <div className="absolute -bottom-8 -left-8 w-8 h-8 bg-gray-600/30 rounded-full flex items-center justify-center animate-float border border-gray-500/50" style={{ animationDelay: '1s' }}>
            <Award className="w-4 h-4 text-white" />
          </div>
          <div className="absolute -bottom-8 -right-8 w-8 h-8 bg-blue-700/30 rounded-full flex items-center justify-center animate-float border border-blue-600/50" style={{ animationDelay: '1.5s' }}>
            <Building className="w-4 h-4 text-white" />
          </div>
        </div>

        {/* School Name with 3D Text Effect */}
        <div className="text-center mb-12">
          <h1 className="text-7xl md:text-9xl font-black text-white mb-6 transform-gpu">
            <span 
              className="inline-block transform-gpu hover:scale-110 transition-all duration-500"
              style={{ 
                textShadow: `
                  0 0 10px rgba(255,255,255,0.8),
                  0 0 20px rgba(59,130,246,0.6),
                  0 0 30px rgba(147,51,234,0.4),
                  0 0 40px rgba(236,72,153,0.2)
                `,
                filter: 'drop-shadow(0 0 20px rgba(59,130,246,0.8))'
              }}
            >
              REGISBRIDGE
            </span>
          </h1>
          
          <div className="relative">
            <p className="text-2xl md:text-3xl text-blue-200 font-light tracking-widest mb-2">
              College Management System
            </p>
            <div className="w-32 h-1 bg-gradient-to-r from-blue-600 via-slate-600 to-gray-600 mx-auto rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Animated Text */}
        <div className="text-center mb-12">
          <div className="h-16 flex items-center justify-center">
            <p className="text-2xl md:text-3xl text-white font-medium animate-fade-in-out">
              {phases[currentPhase].text}
            </p>
          </div>
        </div>

        {/* 3D Progress Indicator */}
        <div className="w-full max-w-sm">
          <div className="relative">
            {/* Background */}
            <div className="w-full h-6 bg-white/10 rounded-full overflow-hidden shadow-inner backdrop-blur-sm">
              {/* Progress Fill */}
              <div 
                className="h-full bg-gradient-to-r from-blue-600 via-slate-600 to-gray-600 rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
                style={{ width: `${((currentPhase + 1) / phases.length) * 100}%` }}
              >
                {/* Shine Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer"></div>
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-slate-500 blur-md opacity-60"></div>
              </div>
        </div>

            {/* Progress Dots */}
            <div className="flex justify-between mt-4">
              {phases.map((_, index) => (
                <div
                  key={index}
                  className={`w-3 h-3 rounded-full transition-all duration-500 ${
                    index <= currentPhase 
                      ? 'bg-white shadow-lg shadow-white/50' 
                      : 'bg-white/30'
                  }`}
                ></div>
              ))}
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="absolute animate-float-sparkle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${2 + Math.random() * 3}s`
              }}
            >
              <Shield className="w-4 h-4 text-blue-400/40" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SplashScreen