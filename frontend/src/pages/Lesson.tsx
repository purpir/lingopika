import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Pika } from '../components/Pika'
import type { AnswerResult, Exercise, LessonDetail, StudyWord } from '../types'

type Phase = 'study' | 'practice' | 'result' | 'completed'

export function Lesson() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { profile } = useAuth()
  const [detail, setDetail] = useState<LessonDetail | null>(null)
  const [phase, setPhase] = useState<Phase>('study')
  const [studyIndex, setStudyIndex] = useState(0)
  const [practiceIndex, setPracticeIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [available, setAvailable] = useState<string[]>([])
  const [arranged, setArranged] = useState<string[]>([])
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [hearts, setHearts] = useState<number | null>(null)
  const [completed, setCompleted] = useState(false)
  const [totalXp, setTotalXp] = useState(0)

  const studyCards: Exercise[] = detail?.exercises.filter((e) => e.type === 'study_card') || []
  const practiceExercises: Exercise[] = detail?.exercises.filter((e) => e.type !== 'study_card') || []

  const currentStudy: Exercise | undefined = studyCards[studyIndex]
  const currentPractice: Exercise | undefined = practiceExercises[practiceIndex]

  const studyWords: StudyWord[] = studyCards.map((e) => e.data.word as StudyWord)

  useEffect(() => {
    if (!id) return
    api.get(`/lessons/${id}`).then((r) => setDetail(r.data)).catch(() => {})
    api.post(`/lessons/${id}/start`).catch(() => {})
  }, [id])

  useEffect(() => {
    if (!currentPractice) return
    setAnswer('')
    setResult(null)
    setArranged([])
    if (currentPractice.type === 'arrange') setAvailable([...(currentPractice.data.tokens || [])])
    else setAvailable([])
  }, [currentPractice])

  useEffect(() => {
    if (profile) setHearts(profile.hearts.count)
  }, [profile])

  // Переход к следующей карточке изучения
  function nextStudy() {
    if (studyIndex + 1 < studyCards.length) {
      setStudyIndex(studyIndex + 1)
    } else {
      setPhase('practice')
    }
  }

  async function submit() {
    if (!currentPractice) return
    let finalAnswer = answer
    if (currentPractice.type === 'arrange') finalAnswer = arranged.join(' ')
    setSubmitting(true)
    try {
      const res = await api.post('/lessons/answer', {
        exercise_id: currentPractice.id,
        answer: finalAnswer,
        idempotency_key: `${id}-${currentPractice.id}`,
      })
      setResult(res.data)
      if (res.data.hearts_remaining != null) setHearts(res.data.hearts_remaining)
      setTotalXp((x) => x + (res.data.xp_awarded || 0))
    } finally {
      setSubmitting(false)
    }
  }

  async function finish() {
    if (!id) return
    const res = await api.post('/lessons/complete', { lesson_id: Number(id), idempotency_key: `complete-${id}` })
    setTotalXp((x) => x + (res.data.xp_awarded || 0))
    setCompleted(true)
  }

  function nextPractice() {
    if (!detail) return
    if (practiceIndex + 1 < practiceExercises.length) {
      setPracticeIndex(practiceIndex + 1)
      setResult(null)
      setAnswer('')
      setArranged([])
    } else {
      finish()
    }
  }

  if (!detail) return <div className="p-4">Загрузка...</div>

  if (completed) {
    return (
      <div className="p-6 space-y-4 text-center">
        <Pika expression="celebrate" size="lg" message="Урок завершен!" />
        <div className="text-lg font-bold">+{totalXp} опыта</div>
        <button onClick={() => navigate('/courses')} className="px-6 py-3 bg-amber-500 text-white rounded-2xl">К курсам</button>
      </div>
    )
  }

  // ---------- ФАЗА ИЗУЧЕНИЯ ----------
  if (phase === 'study') {
    const progressText = `${studyIndex + 1}/${studyCards.length}`
    return (
      <div className="p-4 space-y-4">
        <div className="flex justify-between text-sm text-gray-500">
          <span>Изучение слов</span>
          <span>{progressText}</span>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow text-center space-y-4">
          <div className="text-sm text-cocoa font-semibold">Новое слово</div>
          <div className="text-3xl font-bold text-cocoa">{currentStudy?.data.word.english}</div>
          {currentStudy?.data.word.transcription && (
            <div className="text-sm text-gray-400">{currentStudy.data.word.transcription}</div>
          )}
          <div className="text-2xl font-semibold text-gray-800">{currentStudy?.data.word.russian}</div>
          <div className="text-xs text-gray-500 italic">{currentStudy?.data.word.example_ru}</div>
        </div>
        <button
          onClick={nextStudy}
          disabled={submitting}
          className="w-full py-4 bg-amber-500 text-white rounded-2xl font-semibold disabled:opacity-50"
        >
          {studyIndex + 1 === studyCards.length ? 'Перейти к заданиям' : 'Далее'}
        </button>
        <Pika expression="encourage" message="Запомни перевод!" />
      </div>
    )
  }

  // ---------- ФАЗА ЗАКРЕПЛЕНИЯ ----------
  const ex: Exercise | undefined = currentPractice

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between text-sm text-gray-500">
        <span>Закрепление {practiceIndex + 1}/{practiceExercises.length}</span>
        <span>Жизни {hearts ?? ''}</span>
      </div>
      <div className="bg-white rounded-2xl p-4 shadow space-y-3">
        <div className="font-semibold text-cocoa">{ex?.question}</div>
        {ex?.type === 'comprehension' && ex.data?.text && (
          <div className="text-sm text-gray-600 bg-cream p-3 rounded-xl">{ex.data.text}</div>
        )}
        {ex?.type === 'multiple_choice' && (
          <div className="grid grid-cols-1 gap-2">
            {(ex.data.options || []).map((opt: string, i: number) => (
              <button
                key={i}
                onClick={() => setAnswer(opt)}
                className={`p-3 rounded-xl border ${answer === opt ? 'border-amber-500 bg-amber-50' : 'border-gray-200'}`}
              >
                {opt}
              </button>
            ))}
          </div>
        )}
        {(ex?.type === 'translate_en_ru' || ex?.type === 'translate_ru_en' || ex?.type === 'fill_blank' || ex?.type === 'comprehension') && (
          <input
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-3 border rounded-xl"
            placeholder="Ваш ответ"
          />
        )}
        {ex?.type === 'fill_blank' && ex.data?.hint && (
          <div className="text-xs text-gray-500">Подсказка: {ex.data.hint}</div>
        )}
        {ex?.type === 'arrange' && (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2 min-h-[40px] p-2 border rounded-xl">
              {arranged.map((t, i) => (
                <button key={i} onClick={() => {
                  setArranged(arranged.filter((_, j) => j !== i))
                  setAvailable([...available, t])
                }} className="px-3 py-1 bg-amber-100 rounded-lg">{t}</button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {available.map((t, i) => (
                <button key={i} onClick={() => {
                  setAvailable(available.filter((_, j) => j !== i))
                  setArranged([...arranged, t])
                }} className="px-3 py-1 bg-white border rounded-lg">{t}</button>
              ))}
            </div>
          </div>
        )}
      </div>

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={`rounded-2xl p-4 ${result.is_correct ? 'bg-green-50' : 'bg-red-50'}`}>
          <Pika expression={result.is_correct ? 'correct' : 'wrong'} message={result.is_correct ? 'Правильно!' : 'Попробуйте еще'} />
          {!result.is_correct && result.correct_answer && (
            <div className="text-sm mt-2">Правильный ответ: {result.correct_answer}</div>
          )}
          {result.explanation && <div className="text-xs text-gray-600 mt-1">{result.explanation}</div>}
        </motion.div>
      )}

      <div className="w-full flex gap-2">
        {!result ? (
          <button onClick={submit} disabled={submitting} className="w-full py-4 bg-orange-500 text-white rounded-2xl border border-orange-600 disabled:opacity-50 font-semibold">
            {submitting ? 'Проверка...' : 'Проверить'}
          </button>
        ) : (
          <button onClick={nextPractice} className="w-full py-4 bg-orange-500 text-white rounded-2xl border border-orange-600 font-semibold">Продолжить</button>
        )}
      </div>
    </div>
  )
}
