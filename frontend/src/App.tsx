import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Layout } from './components/Layout'
import { Onboarding } from './pages/Onboarding'
import { Home } from './pages/Home'
import { Courses } from './pages/Courses'
import { CourseDetail } from './pages/CourseDetail'
import { Lesson } from './pages/Lesson'
import { Cards } from './pages/Cards'
import { League } from './pages/League'
import { Profile } from './pages/Profile'
import { Premium } from './pages/Premium'

function RequireOnboarding({ children }: { children: React.ReactNode }) {
  const { loading, profile } = useAuth()
  if (loading) return <div className="p-4">Loading...</div>
  if (profile && !profile.profile.onboarding_completed) return <Navigate to="/onboarding" replace />
  return <>{children}</>
}

function OnboardingRoute() {
  const { loading, profile } = useAuth()
  if (loading) return <div className="p-4">Loading...</div>
  if (profile?.profile.onboarding_completed) return <Navigate to="/" replace />
  return <Onboarding />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/onboarding" element={<OnboardingRoute />} />
      <Route element={<RequireOnboarding><Layout /></RequireOnboarding>}>
        <Route path="/" element={<Home />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/courses/:id" element={<CourseDetail />} />
        <Route path="/lessons/:id" element={<Lesson />} />
        <Route path="/cards" element={<Cards />} />
        <Route path="/league" element={<League />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/premium" element={<Premium />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}