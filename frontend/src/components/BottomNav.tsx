import { NavLink } from 'react-router-dom'
import { Home, BookOpen, CreditCard, Trophy, User } from 'lucide-react'

const tabs = [
  { to: '/', icon: Home, label: 'Главная' },
  { to: '/courses', icon: BookOpen, label: 'Курсы' },
  { to: '/cards', icon: CreditCard, label: 'Карточки' },
  { to: '/league', icon: Trophy, label: 'Лига' },
  { to: '/profile', icon: User, label: 'Профиль' },
]

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-amber-100 flex justify-around py-2 z-50">
      {tabs.map((t) => (
        <NavLink key={t.to} to={t.to} className={({ isActive }) => `flex flex-col items-center text-xs ${isActive ? 'text-amber-600' : 'text-cocoa'}`}>
          <t.icon size={22} />
          <span>{t.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}