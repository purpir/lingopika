import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api } from '../api/client'
import type { AuthResponse, Profile, User } from '../types'

type AuthContextValue = {
  user: User | null
  profile: Profile | null
  loading: boolean
  refreshProfile: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function getInitData(): string {
  const wa = window.Telegram?.WebApp
  if (wa?.initData) return wa.initData
  return 'user={"id":999001,"first_name":"Dev","username":"devuser","language_code":"en"}'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshProfile = async () => {
    const res = await api.get('/profile')
    setProfile(res.data)
  }

  useEffect(() => {
    let cancelled = false
    async function init() {
      try {
        if (!localStorage.getItem('token')) {
          const initData = getInitData()
          const res = await api.post<AuthResponse>('/auth/telegram', { init_data: initData })
          localStorage.setItem('token', res.data.access_token)
          if (!cancelled) setUser(res.data.user)
        } else {
          // fetch user from profile later
        }
        const pres = await api.get<Profile>('/profile')
        if (!cancelled) {
          setProfile(pres.data)
          setUser(pres.data.user)
        }
      } catch {
        localStorage.removeItem('token')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    init()
    return () => {
      cancelled = true
    }
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setProfile(null)
  }

  return (
    <AuthContext.Provider value={{ user, profile, loading, refreshProfile, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}