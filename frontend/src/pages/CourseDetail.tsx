import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Lesson } from '../types'

export function CourseDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [title, setTitle] = useState('')

  useEffect(() => {
    if (!id) return
    api.get(`/courses/${id}`).then((r) => setTitle(r.data.title)).catch(() => {})
    api.get(`/courses/${id}/lessons`).then((r) => setLessons(r.data)).catch(() => {})
  }, [id])

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold text-cocoa">{title}</h1>
      <div className="grid grid-cols-4 gap-3">
        {lessons.map((l) => (
          <button
            key={l.id}
            disabled={l.status === 'locked'}
            onClick={() => navigate(`/lessons/${l.id}`)}
            className={`aspect-square rounded-2xl flex items-center justify-center font-bold shadow ${l.status === 'locked' ? 'bg-gray-200 text-gray-400' : l.status === 'completed' ? 'bg-green-200 text-green-800' : 'bg-white text-cocoa'}`}
          >
            {l.number}
          </button>
        ))}
      </div>
    </div>
  )
}