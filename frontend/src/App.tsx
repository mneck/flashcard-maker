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
  const [showConfetti, setShowConfetti] = useState(false)
  const [showDetailedInfo, setShowDetailedInfo] = useState(false)
  const [hasAnswered, setHasAnswered] = useState(false)
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null)

  // Centralized Arabic font stack for consistency
  const arabicFontFamily = '"Noto Naskh Arabic", serif, "Scheherazade New"'

  // Simple detector to see if a string contains Arabic characters
  const isArabicText = (text?: string | null): boolean => {
    if (!text) return false
    return /[\u0600-\u06FF]/.test(text)
  }

  const fetchCard = async (excludeId?: number) => {
    setLoading(true)
    setFeedback(null)
    setAnswer('')
    setShowDetailedInfo(false)
    setHasAnswered(false)
    setWasCorrect(null)
    try {
      const url = excludeId
        ? `${API_BASE}/flashcards/random?language_code=ar&exclude_id=${excludeId}`
        : `${API_BASE}/flashcards/random?language_code=ar`
      const res = await fetch(url)
      if (!res.ok) throw new Error('No card available')
      const data = await res.json()
      setCard(data)
    } catch (e) {
      // Keep current card if we have only one available
      if (!card) setCard(null)
      setFeedback('No other card available')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCard()
  }, [])

  const submit = async () => {
    if (!card) return
    if (hasAnswered) return
    const res = await fetch(`${API_BASE}/flashcards/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term_id: card.id_vocabulary, user_answer: answer, answer_type: mode })
    })
    const data = await res.json()
    setFeedback(data.message)
    setHasAnswered(true)
    setWasCorrect(Boolean(data.correct))
    setShowDetailedInfo(true)
    if (data.correct) {
      setShowConfetti(true)
      setTimeout(() => setShowConfetti(false), 2000) // Hide confetti after 2 seconds
    }
  }

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: 24, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif' }}>
      <h1>Flashcards</h1>
      <div className="mode-selector">
        <label>
          Mode:&nbsp;
          <select value={mode} onChange={e => setMode(e.target.value as any)}>
            <option value="arabic">Type Arabic (show English)</option>
            <option value="english">Type English (show Arabic)</option>
          </select>
        </label>
        <button className="next-button" onClick={() => fetchCard(card?.id_vocabulary)} disabled={loading}>Next</button>
      </div>

      {card ? (
        <div>
          <div className={`${mode === 'arabic' ? 'english-font' : 'arabic-font'} flashcard-display`}>
            {mode === 'arabic' ? card.english_term : card.target_language_term}
          </div>

          <input
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            placeholder={mode === 'arabic' ? 'Type Arabic' : 'Type English'}
            className={`${mode === 'arabic' ? 'arabic-font' : 'english-font'} flashcard-input`}
            disabled={hasAnswered}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }}
          />
                {!hasAnswered ? (
                  <button className="button-primary" onClick={submit}>Check</button>
                ) : (
                  <button className="button-primary" onClick={() => fetchCard(card?.id_vocabulary)}>
                    Continue
                  </button>
                )}

                 {feedback && (
                   <div className={`${isArabicText(feedback) ? 'arabic-font' : 'english-font'} feedback-message`}>{feedback}</div>
                 )}

                 {showConfetti && (
                   <div className="confetti">
                     🎉
                   </div>
                 )}

                 {showDetailedInfo && card && (
                   <div className="details-panel">
                                          
                     <div className="details-item">
                       <strong>English:</strong> <span className="english-font">{card.english_term}</span>
                     </div>
                     
                     <div className="details-item">
                       <strong>Arabic:</strong>{' '}
                       <span className="arabic-font arabic-details">
                         {card.target_language_term}
                       </span>
                     </div>
                     
                     {card.transliteration && (
                       <div className="details-item">
                         <strong>Transliteration:</strong> <span className="english-font">{card.transliteration}</span>
                       </div>
                     )}
                     
                     {card.example_sentence && (
                       <div className="details-item">
                         <strong>Example:</strong>{' '}
                         <span className={`${isArabicText(card.example_sentence) ? 'arabic-font' : 'english-font'} example-sentence`}>
                           {card.example_sentence}
                         </span>
                       </div>
                     )}
                     
                     {card.example_sentence_explained && (
                       <div className="details-item">
                         <strong>Example Translation:</strong> <span className="english-font">{card.example_sentence_explained}</span>
                       </div>
                     )}
                     
                     {card.notes && (
                       <div className="details-item">
                         <strong>Notes:</strong> <span className="english-font">{card.notes}</span>
                       </div>
                     )}
                   </div>
                 )}

          {/* Example content is now only shown after answering correctly via the detailed panel above */}
        </div>
      ) : (
        <div>{loading ? 'Loading…' : 'No card available'}</div>
      )}
    </div>
  )
}


