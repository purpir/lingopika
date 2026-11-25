import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { PremiumPlan, PremiumStatus } from '../types'

export function Premium() {
  const [plans, setPlans] = useState<PremiumPlan[]>([])
  const [status, setStatus] = useState<PremiumStatus | null>(null)
  const [loading, setLoading] = useState<string | null>(null)

  useEffect(() => {
    api.get('/premium/plans').then((r) => setPlans(r.data)).catch(() => {})
    api.get('/premium/status').then((r) => setStatus(r.data)).catch(() => {})
  }, [])

  async function buy(planId: string) {
    setLoading(planId)
    try {
      const res = await api.post('/premium/invoice', { plan: planId })
      const link = res.data.invoice_link
      const wa = window.Telegram?.WebApp
      if (wa?.openInvoice) {
        wa.openInvoice(link, () => {})
      } else {
        window.open(link, '_blank')
      }
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold text-cocoa">Премиум</h1>
      {status && (
        <div className="bg-white rounded-2xl p-3 shadow text-sm">
          Премиум: {status.is_premium ? 'Активно' : 'Не активно'} {status.premium_until ? `до ${status.premium_until}` : ''}
        </div>
      )}
      <div className="space-y-3">
        {plans.map((p) => (
          <div key={p.id} className={`bg-white rounded-2xl p-4 shadow ${p.best_value ? 'border-2 border-amber-500' : ''}`}>
            <div className="flex justify-between items-center">
              <div>
                <div className="font-semibold text-cocoa">{p.title}</div>
                <div className="text-sm text-gray-600">{p.description}</div>
              </div>
              {p.best_value && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full">Выгодное предложение</span>}
            </div>
            <div className="mt-2 text-lg font-bold">{p.stars} Stars · {p.duration_days} days</div>
            <button
              onClick={() => buy(p.id)}
              disabled={loading === p.id}
              className="mt-3 w-full py-2 bg-amber-500 text-white rounded-xl disabled:opacity-50"
            >
              {loading === p.id ? 'Создание...' : 'Купить'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}