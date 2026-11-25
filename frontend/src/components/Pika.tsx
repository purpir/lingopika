import { motion } from 'framer-motion'
import type { Expression } from '../types'

const colors: Record<Expression, string> = {
  happy: 'bg-amber-100',
  sad: 'bg-blue-100',
  surprised: 'bg-purple-100',
  tired: 'bg-gray-100',
  celebrate: 'bg-yellow-100',
  encourage: 'bg-orange-100',
  correct: 'bg-green-100',
  wrong: 'bg-red-100',
}

const badges: Record<Expression, string> = {
  happy: '😊',
  sad: '😢',
  surprised: '😲',
  tired: '😴',
  celebrate: '🎉',
  encourage: '💪',
  correct: '✅',
  wrong: '❌',
}

type PikaProps = {
  expression: Expression
  size?: 'sm' | 'md' | 'lg'
  message?: string
}

export function Pika({ expression, size = 'md', message }: PikaProps) {
  const sizeClass = size === 'sm' ? 'w-12 h-12 text-2xl' : size === 'lg' ? 'w-24 h-24 text-5xl' : 'w-16 h-16 text-3xl'
  return (
    <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex items-center gap-3">
      <div className={`${sizeClass} ${colors[expression]} rounded-full flex items-center justify-center relative shadow`}>
        <span>🐹</span>
        <span className="absolute -bottom-1 -right-1 text-lg">{badges[expression]}</span>
      </div>
      {message && <div className="bg-white rounded-2xl px-4 py-2 shadow text-sm max-w-xs">{message}</div>}
    </motion.div>
  )
}