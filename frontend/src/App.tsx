import React, { useEffect, useMemo, useState } from 'react'

type Flashcard = {
  id_vocabulary: number
  english_term: string
  target_language_term: string
  transliteration?: string | null
  example_sentence?: string | null
  example_sentence_explained?: string | null
  notes?: string | null
  correct_counter: number
}

const API_BASE = import.meta.env.VITE_API_BASE_URL

export const App: React.FC = () => {
  const [card, setCard] = useState<Flashcard | null>(null)
  const [answer, setAnswer] = useState('')
  const [mode, setMode] = useState<'english' | 'arabic'>('arabic')
  const [feedback, setFeedback] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchCard = async () => {
    setLoading(true)
    setFeedback(null)
    setAnswer('')
    try {
      const res = await fetch(`${API_BASE}/flashcards/random?language_code=ar`)
      if (!res.ok) throw new Error('No card available')
      const data = await res.json()
      setCard(data)
    } catch (e) {
      setCard(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCard()
  }, [])

  const submit = async () => {
    if (!card) return
    const res = await fetch(`${API_BASE}/flashcards/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term_id: card.id_vocabulary, user_answer: answer, answer_type: mode })
    })
    const data = await res.json()
    setFeedback(data.message)
    if (data.correct) {
      await fetchCard()
    }
  }

  const arabicStyle: React.CSSProperties = useMemo(() => ({
    fontSize: '64px',
    lineHeight: 1.2,
    fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Noto Sans Arabic, Arial, sans-serif',
    direction: 'rtl',
    textAlign: 'center',
    margin: '20px 0'
  }), [])

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: 24, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif' }}>
      <h1>Flashcards</h1>
      <div style={{ marginBottom: 12 }}>
        <label>
          Mode:&nbsp;
          <select value={mode} onChange={e => setMode(e.target.value as any)}>
            <option value="arabic">Type Arabic (show English)</option>
            <option value="english">Type English (show Arabic)</option>
          </select>
        </label>
        <button style={{ marginLeft: 12 }} onClick={fetchCard} disabled={loading}>Next</button>
      </div>

      {card ? (
        <div>
          <div style={arabicStyle}>
            {mode === 'arabic' ? card.english_term : card.target_language_term}
          </div>

          <input
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            placeholder={mode === 'arabic' ? 'Type Arabic…' : 'Type English…'}
            style={{ width: '100%', padding: 12, fontSize: 18 }}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }}
          />
          <button style={{ marginTop: 12 }} onClick={submit}>Check</button>

          {feedback && (
            <div style={{ marginTop: 12 }}>{feedback}</div>
          )}

          <div style={{ marginTop: 16, opacity: 0.8 }}>
            {card.example_sentence && <div><strong>Example:</strong> {card.example_sentence}</div>}
            {card.example_sentence_explained && <div><strong>Explained:</strong> {card.example_sentence_explained}</div>}
          </div>
        </div>
      ) : (
        <div>{loading ? 'Loading…' : 'No card available'}</div>
      )}
    </div>
  )
}


