import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { api } from '../api/client'
import { Pika } from '../components/Pika'
import type { UserWord, VocabularyStats } from '../types'

export function Cards() {
  const [tab, setTab] = useState<'due' | 'new'>('due')
  const [cards, setCards] = useState<UserWord[]>([])
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [stats, setStats] = useState<VocabularyStats | null>(null)

  async function load() {
    const endpoint = tab === 'due' ? '/cards/due' : '/cards/new'
    const res = await api.get(endpoint)
    setCards(res.data)
    setIndex(0)
    setFlipped(false)
  }

  useEffect(() => {
    load().catch(() => {})
    api.get('/cards/stats').then((r) => setStats(r.data)).catch(() => {})
  }, [tab])

  const card = cards[index]

  async function review(known: boolean) {
    if (!card) return
    await api.post('/cards/review', { word_id: card.word.id, known, idempotency_key: `${card.word.id}-${Date.now()}` })
    setFlipped(false)
    if (index + 1 < cards.length) setIndex(index + 1)
    else load()
    api.get('/cards/stats').then((r) => setStats(r.data)).catch(() => {})
  }

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold text-cocoa">Карточки</h1>
      <div className="flex gap-2">
        <button onClick={() => setTab('due')} className={`px-4 py-2 rounded-xl ${tab === 'due' ? 'bg-amber-500 text-white' : 'bg-white'}`}>К повторению</button>
        <button onClick={() => setTab('new')} className={`px-4 py-2 rounded-xl ${tab === 'new' ? 'bg-amber-500 text-white' : 'bg-white'}`}>Новые</button>
      </div>
      {stats && (
        <div className="bg-white rounded-2xl p-3 shadow text-sm flex justify-between">
          <span>Всего {stats.total}</span>
          <span>Новые {stats.new}</span>
          <span>Знаю {stats.known}</span>
          <span>К повторению {stats.due_for_review}</span>
        </div>
      )}
      {card ? (
        <div className="space-y-4">
          <motion.div
            onClick={() => setFlipped(!flipped)}
            className="bg-white rounded-2xl p-6 shadow min-h-[160px] flex items-center justify-center cursor-pointer"
          >
            {!flipped ? (
              <div className="text-center">
                <div className="text-2xl font-bold">{card.word.english}</div>
                <div className="text-sm text-gray-500">{card.word.transcription}</div>
              </div>
            ) : (
              <div className="text-center">
                <div className="text-2xl font-bold">{card.word.russian}</div>
                {card.word.example_en && <div className="text-xs text-gray-500 mt-2">{card.word.example_en}</div>}
              </div>
            )}
          </motion.div>
          <div className="flex gap-2">
            <button onClick={() => review(false)} className="flex-1 py-3 bg-red-100 text-red-700 rounded-2xl">Повторить</button>
            <button onClick={() => review(true)} className="flex-1 py-3 bg-green-100 text-green-700 rounded-2xl">Знаю</button>
          </div>
          <Pika expression="encourage" />
        </div>
      ) : (
        <div className="text-center text-gray-500">Нет карточек</div>
      )}
    </div>
  )
}