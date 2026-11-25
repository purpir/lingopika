import { Outlet } from 'react-router-dom'
import { BottomNav } from './BottomNav'

export function Layout() {
  return (
    <div className="min-h-screen bg-cream pb-20 max-w-md mx-auto">
      <Outlet />
      <BottomNav />
    </div>
  )
}