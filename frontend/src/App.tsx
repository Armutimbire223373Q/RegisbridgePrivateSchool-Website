import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import SplashScreen from './components/SplashScreen'
import LoadingScreen from './components/LoadingScreen'
import Login from './pages/Login'
import PublicHomepage from './pages/PublicHomepage'
import Admissions from './pages/Admissions'
import Dashboard from './pages/Dashboard'
import Students from './pages/Students'
import Teachers from './pages/Teachers'
import Parents from './pages/Parents'
import Grades from './pages/Grades'
import Attendance from './pages/Attendance'
import Fees from './pages/Fees'
import Payment from './pages/Payment'
import Messages from './pages/Messages'
import Profile from './pages/Profile'
import HomepageManagement from './pages/admin/HomepageManagement'
import Blog from './pages/Blog'
import BlogPost from './pages/BlogPost'
import Inventory from './pages/Inventory'
import Reports from './pages/Reports'
import Assignments from './pages/Assignments'
import './App.css'

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: string[] }> = ({ 
  children, 
  allowedRoles = [] 
}) => {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen isLoading={true} />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

// Main App Component
const AppContent: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PublicHomepage />} />
        <Route path="/admissions" element={<Admissions />} />
        <Route path="/login" element={<Login />} />
        <Route path="/portal" element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/students" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER', 'BOARDING_STAFF']}>
            <Layout>
              <Students />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/teachers" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STUDENT', 'PARENT']}>
            <Layout>
              <Teachers />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/parents" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER']}>
            <Layout>
              <Parents />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/grades" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER', 'STUDENT', 'PARENT']}>
            <Layout>
              <Grades />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/attendance" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER', 'BOARDING_STAFF']}>
            <Layout>
              <Attendance />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/fees" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STUDENT', 'PARENT']}>
            <Layout>
              <Fees />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/payments" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STUDENT', 'PARENT']}>
            <Layout>
              <Payment />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/messages" element={
          <ProtectedRoute>
            <Layout>
              <Messages />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <Layout>
              <Profile />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/admin/homepage" element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <Layout>
              <HomepageManagement />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:slug" element={<BlogPost />} />
        <Route path="/inventory" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STAFF']}>
            <Layout>
              <Inventory />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/reports" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER']}>
            <Layout>
              <Reports />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/payment" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STUDENT', 'PARENT']}>
            <Layout>
              <Payment />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/assignments" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'TEACHER', 'STUDENT']}>
            <Layout>
              <Assignments />
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  )
}

const App: React.FC = () => {
  const [showSplash, setShowSplash] = useState(true)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if splash screen has been shown before
    const splashShown = localStorage.getItem('splashShown')
    
    if (splashShown) {
      // If splash was shown before, show a shorter loading
      setTimeout(() => {
        setIsLoading(false)
      }, 1000)
    } else {
      // First time visit - show full splash screen
      setTimeout(() => {
        setShowSplash(false)
        setIsLoading(false)
        localStorage.setItem('splashShown', 'true')
      }, 4000)
    }
  }, [])

  const handleSplashComplete = () => {
    setShowSplash(false)
  }

  if (showSplash) {
    return <SplashScreen onComplete={handleSplashComplete} />
  }

  if (isLoading) {
    return <LoadingScreen isLoading={true} onComplete={() => setIsLoading(false)} />
  }

  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App