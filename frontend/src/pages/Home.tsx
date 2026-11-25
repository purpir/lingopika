import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Pika } from '../components/Pika'
import type { Course } from '../types'

export function Home() {
  const { user, profile } = useAuth()
  const navigate = useNavigate()
  const [courses, setCourses] = useState<Course[]>([])

  useEffect(() => {
    api.get('/courses').then((r) => setCourses(r.data)).catch(() => {})
  }, [])

  const currentCourse = courses[0]

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-gray-500">Привет</div>
          <div className="text-xl font-bold text-cocoa">{user?.first_name || 'Ученик'}</div>
        </div>
        <div className="text-right">
          <div className="text-sm">Уровень {profile?.profile.level}</div>
          <div className="text-xs text-gray-500">{profile?.profile.english_level}</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow flex items-center justify-between">
        <div>
          <div className="text-sm text-gray-500">Жизни</div>
          <div className="text-lg font-bold">{profile?.hearts.count}/{profile?.hearts.max_count}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Опыт</div>
          <div className="text-lg font-bold">{profile?.profile.total_xp}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Серия</div>
          <div className="text-lg font-bold">{profile?.streak.current_streak}</div>
        </div>
      </div>

      <motion.div whileTap={{ scale: 0.98 }} className="bg-amber-50 rounded-2xl p-4 shadow cursor-pointer" onClick={() => {
        if (profile?.profile.current_lesson_id) navigate(`/lessons/${profile.profile.current_lesson_id}`)
        else navigate('/courses')
      }}>
        <div className="font-semibold text-cocoa">Продолжить урок</div>
        <div className="text-sm text-gray-600">Продолжить с того места, где остановились</div>
      </motion.div>

      <div className="bg-white rounded-2xl p-4 shadow">
        <div className="font-semibold mb-2">Активность дня</div>
        <button onClick={() => api.post('/users/activity').then(() => alert('Активность зафиксирована'))} className="px-4 py-2 bg-amber-500 text-white rounded-xl">Зафиксировать активность</button>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow cursor-pointer" onClick={() => navigate('/cards')}>
        <div className="font-semibold">Карточки</div>
        <div className="text-sm text-gray-600">Повторите слова</div>
      </div>

      {currentCourse && (
        <div className="bg-white rounded-2xl p-4 shadow">
          <div className="font-semibold">{currentCourse.title}</div>
          <div className="text-sm text-gray-600">{currentCourse.completed_lessons}/{currentCourse.total_lessons} уроков</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${currentCourse.total_lessons ? (currentCourse.completed_lessons / currentCourse.total_lessons) * 100 : 0}%` }} />
          </div>
        </div>
      )}

      <Pika expression="encourage" message="Молодец!" />
    </div>
  )
}