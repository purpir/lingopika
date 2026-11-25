import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { LeagueStatus } from '../types'

export function League() {
  const [status, setStatus] = useState<LeagueStatus | null>(null)
  const [remaining, setRemaining] = useState(0)

  useEffect(() => {
    api.get('/leagues/status').then((r) => {
      setStatus(r.data)
      setRemaining(r.data.seconds_to_end)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    const t = setInterval(() => setRemaining((x) => (x > 0 ? x - 1 : 0)), 1000)
    return () => clearInterval(t)
  }, [])

  if (!status) return <div className="p-4">Загрузка...</div>

  const hours = Math.floor(remaining / 3600)
  const mins = Math.floor((remaining % 3600) / 60)
  const secs = remaining % 60

  return (
    <div className="p-4 space-y-4">
      <div className="bg-white rounded-2xl p-4 shadow">
        <div className="text-lg font-bold text-cocoa">{status.league.name}</div>
        <div className="text-sm text-gray-600">Лига {status.league.tier}</div>
        <div className="text-sm mt-2">Ваша позиция: {status.user_position ?? '-'}</div>
        <div className="text-sm">XP за неделю: {status.user_weekly_xp}</div>
        <div className="text-sm">Сезон заканчивается через {hours}ч {mins}м {secs}с</div>
        <div className="text-xs text-gray-500 mt-1">Зона повышения: топ {status.promotion_zone} | Зона понижения: низ {status.demotion_zone}</div>
      </div>
      <div className="space-y-2">
        {status.participants.map((p) => (
          <div key={p.id} className={`flex items-center justify-between p-3 rounded-2xl shadow ${p.is_user ? 'bg-amber-50' : 'bg-white'}`}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">{p.avatar || '🐹'}</div>
              <div>
                <div className="font-semibold text-sm">{p.name} {p.is_bot && <span className="text-xs text-gray-400">(бот)</span>}</div>
                <div className="text-xs text-gray-500">#{p.position}</div>
              </div>
            </div>
            <div className="font-bold text-sm">{p.weekly_xp} XP</div>
          </div>
        ))}
      </div>
    </div>
  )
}