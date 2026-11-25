import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Pika } from '../components/Pika'

const levels = [
  { value: 'nothing', title: 'Ничего', description: 'Начинаю с нуля' },
  { value: 'a1', title: 'A1 Начальный', description: 'Основные слова и фразы' },
  { value: 'a2', title: 'A2 Элементарный', description: 'Простые разговоры' },
  { value: 'b1', title: 'B1 Средний', description: 'Повседневные темы' },
  { value: 'b2', title: 'B2 Выше среднего', description: 'Свободные дискуссии' },
  { value: 'c1', title: 'C1 Продвинутый', description: 'Почти носитель языка' },
]

export function Onboarding() {
  const [selected, setSelected] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { refreshProfile } = useAuth()

  async function submit() {
    if (!selected) return
    setLoading(true)
    try {
      await api.post('/profile/onboarding', null, { params: { level: selected } })
      await refreshProfile()
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <Pika expression="happy" size="lg" message="Добро пожаловать в LingoPika! Выберите ваш уровень." />
      <div className="space-y-3">
        {levels.map((l) => (
          <motion.button
            key={l.value}
            whileTap={{ scale: 0.98 }}
            onClick={() => setSelected(l.value)}
            className={`w-full text-left p-4 rounded-2xl border-2 ${selected === l.value ? 'border-amber-500 bg-amber-50' : 'border-amber-100 bg-white'}`}
          >
            <div className="font-semibold text-cocoa">{l.title}</div>
            <div className="text-sm text-gray-600">{l.description}</div>
          </motion.button>
        ))}
      </div>
      <button
        onClick={submit}
        disabled={!selected || loading}
        className="w-full py-3 rounded-2xl bg-amber-500 text-white font-semibold disabled:opacity-50"
      >
        {loading ? 'Сохранение...' : 'Продолжить'}
      </button>
    </div>
  )
}