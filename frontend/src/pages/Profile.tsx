import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import type { Profile } from '../types'

export function Profile() {
  const { profile, refreshProfile } = useAuth()
  const [data, setData] = useState<Profile | null>(profile)
  const [notifications, setNotifications] = useState(true)
  const [reminderHour, setReminderHour] = useState(9)
  const [timezone, setTimezone] = useState('UTC')

  useEffect(() => {
    if (profile) {
      setData(profile)
      setNotifications(profile.settings.notifications_enabled)
      setReminderHour(profile.settings.reminder_hour)
      setTimezone(profile.settings.timezone)
    }
  }, [profile])

  async function saveSettings() {
    await api.patch('/users/settings', {
      notifications_enabled: notifications,
      reminder_hour: reminderHour,
      timezone,
    })
    await refreshProfile()
  }

  if (!data) return <div className="p-4">Загрузка...</div>

  return (
    <div className="p-4 space-y-4">
      <div className="bg-white rounded-2xl p-4 shadow flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center text-3xl">🐹</div>
        <div>
          <div className="font-bold text-cocoa">{data.user.first_name} {data.user.last_name}</div>
          <div className="text-sm text-gray-500">@{data.user.username}</div>
          <div className="text-sm">Уровень {data.profile.level} · {data.profile.english_level}</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow grid grid-cols-2 gap-3 text-sm">
        <div>Опыт: {data.profile.total_xp}</div>
        <div>Слов выучено: {data.profile.words_learned}</div>
        <div>Уроков: {data.profile.lessons_completed}</div>
        <div>Серия: {data.streak.current_streak} (лучшая {data.streak.longest_streak})</div>
        <div>Премиум: {data.profile.is_premium ? 'Да' : 'Нет'}</div>
        <div>Жизни: {data.hearts.count}/{data.hearts.max_count}</div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow space-y-3">
        <div className="font-semibold">Настройки</div>
        <label className="flex items-center justify-between text-sm">
          Уведомления
          <input type="checkbox" checked={notifications} onChange={(e) => setNotifications(e.target.checked)} />
        </label>
        <label className="block text-sm">
          Час напоминания
          <input type="number" value={reminderHour} onChange={(e) => setReminderHour(Number(e.target.value))} className="ml-2 border rounded px-2" />
        </label>
        <label className="block text-sm">
          Часовой пояс
          <input value={timezone} onChange={(e) => setTimezone(e.target.value)} className="ml-2 border rounded px-2" />
        </label>
        <button onClick={saveSettings} className="px-4 py-2 bg-amber-500 text-white rounded-xl">Сохранить</button>
      </div>
    </div>
  )
}