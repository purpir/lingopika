import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Course } from '../types'

export function Courses() {
  const [courses, setCourses] = useState<Course[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/courses').then((r) => setCourses(r.data)).catch(() => {})
  }, [])

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold text-cocoa">Курсы</h1>
      <div className="space-y-3">
        {courses.map((c) => (
          <div key={c.id} onClick={() => navigate(`/courses/${c.id}`)} className="bg-white rounded-2xl p-4 shadow cursor-pointer">
            <div className="flex justify-between items-center">
              <div>
                <div className="font-semibold text-cocoa">{c.title}</div>
                <div className="text-sm text-gray-600">{c.description}</div>
              </div>
              {c.is_premium && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">Премиум</span>}
            </div>
            <div className="mt-2 text-xs text-gray-500">{c.completed_lessons}/{c.total_lessons} уроков</div>
            <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
              <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${c.total_lessons ? (c.completed_lessons / c.total_lessons) * 100 : 0}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}