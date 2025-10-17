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
  const arabicFontFamily = '"KFGQPC Uthman Taha Naskh Regular", "Amiri", "Scheherazade New", "Noto Naskh Arabic", "Traditional Arabic", "Arabic Typesetting", "Simplified Arabic", "Tahoma", "Arial Unicode MS", serif'

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

  const arabicStyle: React.CSSProperties = useMemo(() => ({
    fontSize: '64px',
    lineHeight: 1.2,
    fontFamily: arabicFontFamily,
    direction: 'rtl',
    textAlign: 'center',
    margin: '20px 0',
    fontWeight: 'normal',
    letterSpacing: '0.05em'
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
        <button style={{ marginLeft: 12 }} onClick={() => fetchCard(card?.id_vocabulary)} disabled={loading}>Next</button>
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
            style={{
              width: '100%',
              padding: 12,
              fontSize: 18,
              fontFamily: mode === 'arabic' ? arabicFontFamily : undefined,
              direction: mode === 'arabic' ? ('rtl' as const) : undefined,
              textAlign: mode === 'arabic' ? ('center' as const) : undefined,
            }}
            disabled={hasAnswered}
            onKeyDown={(e) => { if (e.key === 'Enter') submit() }}
          />
                {!hasAnswered ? (
                  <button style={{ marginTop: 12 }} onClick={submit}>Check</button>
                ) : (
                  <button style={{ marginTop: 12 }} onClick={() => fetchCard(card?.id_vocabulary)}>
                    Continue
                  </button>
                )}

                 {feedback && (
                   <div style={{ marginTop: 12 }}>{feedback}</div>
                 )}

                 {showConfetti && (
                   <div style={{ 
                     marginTop: 16, 
                     fontSize: '48px', 
                     textAlign: 'center',
                     animation: 'bounce 0.6s ease-in-out'
                   }}>
                     🎉
                   </div>
                 )}

                 {showDetailedInfo && card && (
                   <div style={{ 
                     marginTop: 20, 
                     padding: 16, 
                     backgroundColor: '#f0f8ff', 
                     borderRadius: 8, 
                     border: '1px solid #e0e0e0' 
                   }}>
                                          
                     <div style={{ marginBottom: 12 }}>
                       <strong>English:</strong> {card.english_term}
                     </div>
                     
                     <div style={{ marginBottom: 12 }}>
                       <strong>Arabic:</strong>{' '}
                       <span style={{ fontFamily: arabicFontFamily, direction: 'rtl' as const, fontSize: '20px' }}>
                         {card.target_language_term}
                       </span>
                     </div>
                     
                     {card.transliteration && (
                       <div style={{ marginBottom: 12 }}>
                         <strong>Transliteration:</strong> {card.transliteration}
                       </div>
                     )}
                     
                     {card.example_sentence && (
                       <div style={{ marginBottom: 12 }}>
                         <strong>Example:</strong>{' '}
                         <span style={isArabicText(card.example_sentence) ? { fontFamily: arabicFontFamily, direction: 'rtl' as const } : undefined}>
                           {card.example_sentence}
                         </span>
                       </div>
                     )}
                     
                     {card.example_sentence_explained && (
                       <div style={{ marginBottom: 12 }}>
                         <strong>Example Translation:</strong> {card.example_sentence_explained}
                       </div>
                     )}
                     
                     {card.notes && (
                       <div style={{ marginBottom: 12 }}>
                         <strong>Notes:</strong> {card.notes}
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


