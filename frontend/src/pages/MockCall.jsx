import { useState, useRef, useEffect } from 'react'
import { startConversation, sendMessage, endConversation, getAgents, synthesizeSpeech } from '../api/client'

const TTS_LANGUAGES = [
  ['en-IN', 'English (India)'],
  ['hi-IN', 'Hindi'],
  ['ml-IN', 'Malayalam'],
  ['ta-IN', 'Tamil'],
  ['te-IN', 'Telugu'],
  ['kn-IN', 'Kannada'],
  ['bn-IN', 'Bengali'],
  ['mr-IN', 'Marathi'],
  ['gu-IN', 'Gujarati'],
  ['pa-IN', 'Punjabi'],
  ['ur-IN', 'Urdu'],
  ['ne-IN', 'Nepali'],
  ['en-US', 'English (US)'],
  ['en-GB', 'English (UK)'],
]

export default function MockCall() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [isActive, setIsActive] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [voiceError, setVoiceError] = useState('')
  const [ttsLanguage, setTtsLanguage] = useState('en-IN')
  const [ttsStyle, setTtsStyle] = useState('default')
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const audioRef = useRef(null)
  const ttsEnabledRef = useRef(true)
  const transcriptRef = useRef('')
  const shouldSubmitRef = useRef(false)
  const sendMessageRef = useRef(null)
  const speechSupported = typeof window !== 'undefined' && (
    'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
  )
  const selectedAgentName = agents.find(agent => String(agent.id) === selectedAgent)?.name || 'Default AI Agent'

  useEffect(() => {
    getAgents().then(setAgents).catch(() => {})
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => () => {
    recognitionRef.current?.stop()
    audioRef.current?.pause()
    window.speechSynthesis?.cancel()
  }, [])

  const handleStart = async () => {
    try {
      const payload = {}
      if (selectedAgent) payload.agent_id = parseInt(selectedAgent)
      const res = await startConversation(payload)
      setSessionId(res.session_id)
      setIsActive(true)
      setMessages([])
      setVoiceError('')

      // A real call starts with the assistant, so request and speak its greeting.
      setSending(true)
      const greeting = await sendMessage(res.session_id, 'Start the call with a brief, professional greeting and ask how you can help.')
      setMessages([{ role: 'assistant', content: greeting.text, meta: {
        provider: greeting.provider,
        model: greeting.model,
        latency: greeting.latency_ms,
        tokens: greeting.usage?.total_tokens || 0,
        intent: greeting.intent,
      } }])
      speak(greeting.text)
    } catch (e) {
      alert('Failed to start: ' + e.message)
    } finally {
      setSending(false)
    }
  }

  const handleSend = async (message = input) => {
    if (!message.trim() || sending || !sessionId) return

    const userMsg = message.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setSending(true)

    try {
      const res = await sendMessage(sessionId, userMsg)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.text,
        meta: {
          provider: res.provider,
          model: res.model,
          latency: res.latency_ms,
          tokens: res.usage?.total_tokens || 0,
          intent: res.intent,
        },
      }])
      speak(res.text)

      if (res.should_end_call) {
        handleEnd()
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ Error: ${e.message}`,
        meta: { error: true },
      }])
    }
    setSending(false)
  }

  sendMessageRef.current = handleSend

  const speak = async (text) => {
    if (!text) return

    if (ttsEnabledRef.current) {
      try {
        const result = await synthesizeSpeech({
          text,
          language: ttsLanguage,
          style: ttsStyle,
        })
        audioRef.current?.pause()
        const audio = new Audio(`data:${result.content_type};base64,${result.audio_b64}`)
        audioRef.current = audio
        await audio.play()
        return
      } catch {
        // Keep the mock call usable when the optional local TTS service is offline.
        ttsEnabledRef.current = false
      }
    }

    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = ttsLanguage
      utterance.rate = 1
      utterance.pitch = 1
      window.speechSynthesis.speak(utterance)
    }
  }

  const toggleListening = () => {
    if (!speechSupported) {
      setVoiceError('Voice input is unavailable in this browser. Type your message instead.')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      return
    }

    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new Recognition()
    recognition.lang = ttsLanguage
    recognition.interimResults = false
    recognition.continuous = false
    transcriptRef.current = ''
    shouldSubmitRef.current = true
    setVoiceError('')

    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join(' ')
        .trim()
      if (transcript) {
        transcriptRef.current = transcript
        setInput(transcript)

        const lastResult = event.results[event.results.length - 1]
        if (lastResult?.isFinal && shouldSubmitRef.current) {
          shouldSubmitRef.current = false
          sendMessageRef.current?.(transcript)
        }
      }
    }
    recognition.onerror = (event) => {
      shouldSubmitRef.current = false
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        setVoiceError('Microphone access was blocked. Allow microphone access and try again.')
      } else if (event.error !== 'aborted') {
        setVoiceError(`Microphone error: ${event.error}. Try again or type a message.`)
      }
      setIsListening(false)
    }
    recognition.onend = () => {
      setIsListening(false)
      const transcript = transcriptRef.current.trim()
      if (shouldSubmitRef.current && transcript) sendMessageRef.current?.(transcript)
      shouldSubmitRef.current = false
      if (!transcript) {
        setVoiceError('No speech detected. Check your microphone and try again.')
      }
    }

    recognitionRef.current = recognition
    try {
      recognition.start()
    } catch (error) {
      shouldSubmitRef.current = false
      setIsListening(false)
      setVoiceError(`Could not start the microphone: ${error.message}.`)
    }
  }

  const handleEnd = async () => {
    if (sessionId) {
      try {
        await endConversation(sessionId)
      } catch (e) { /* ignore */ }
    }
    shouldSubmitRef.current = false
    recognitionRef.current?.stop()
    window.speechSynthesis?.cancel()
    setIsListening(false)
    setIsActive(false)
    setSessionId(null)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Mock Call</h1>
        <p className="page-description">Test the AI conversation — same code path as real telephony calls</p>
      </div>

      <div className="page-content animate-fade-in">
        <div className="glass-card chat-container">
          {/* ── Chat Header ─────────────────────────────────────────── */}
          <div className="chat-header">
            <div className="chat-agent-identity">
              <div className="chat-agent-avatar">✦</div>
              <div>
                <div className="chat-agent-name">{selectedAgentName}</div>
                <div className="chat-status">
                  <span className={`status-dot ${isActive ? 'connected' : 'disconnected'}`}></span>
                  {isActive ? 'Live conversation' : 'Ready to connect'}
                </div>
              </div>
            </div>
            <div className="chat-header-controls">
              {!isActive && (
                <>
                  <select
                    className="form-select"
                    value={selectedAgent}
                    onChange={e => setSelectedAgent(e.target.value)}
                    aria-label="Choose an AI agent"
                  >
                    <option value="">Default Agent</option>
                    {agents.map(a => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                  </select>
                  <button className="btn btn-primary btn-sm" onClick={handleStart}>
                    <span>☎</span> Start Call
                  </button>
                </>
              )}
              {isActive && (
                <button className="btn btn-danger btn-sm" onClick={handleEnd} disabled={sending}>
                  <span>■</span> End Call
                </button>
              )}
            </div>
          </div>

          {/* ── Messages ────────────────────────────────────────────── */}
          <div className="chat-messages">
            {!isActive && messages.length === 0 && (
              <div className="call-empty-state">
                <div className="call-empty-icon">☎</div>
                <div className="call-empty-kicker">VOICE CONSOLE / STANDBY</div>
                <div className="call-empty-title">Start a conversation</div>
                <div className="call-empty-copy">Your agent will greet you, listen through the microphone, and respond aloud.</div>
                <div className="call-capabilities">
                  <span>01 &nbsp; SPEAK</span>
                  <span>02 &nbsp; TRANSCRIBE</span>
                  <span>03 &nbsp; RESPOND</span>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble ${msg.role}`}>
                <div>{msg.content}</div>
                {msg.meta && !msg.meta.error && (
                  <div className="chat-bubble-meta">
                    <span>🔌 {msg.meta.provider}</span>
                    <span>📦 {msg.meta.model}</span>
                    <span>⏱ {msg.meta.latency}ms</span>
                    <span>🔢 {msg.meta.tokens} tokens</span>
                    {msg.meta.intent && <span>🎯 {msg.meta.intent}</span>}
                  </div>
                )}
              </div>
            ))}

            {sending && (
              <div className="chat-bubble assistant" style={{ opacity: 0.6 }}>
                <div className="spinner"></div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ── Input ───────────────────────────────────────────────── */}
          {isActive && (
            <div className="chat-input-area">
              <div className="input-mode-label">
                <span className={`input-live-dot ${isListening ? 'active' : ''}`}></span>
                {isListening ? 'Listening...' : 'Voice or text'}
              </div>
              <select
                className="form-select call-language-select"
                value={ttsLanguage}
                onChange={e => {
                  setTtsLanguage(e.target.value)
                  ttsEnabledRef.current = true
                }}
                aria-label="Choose conversation language"
              >
                {TTS_LANGUAGES.map(([code, label]) => (
                  <option key={code} value={code}>{label}</option>
                ))}
              </select>
              <select
                className="form-select call-style-select"
                value={ttsStyle}
                onChange={e => {
                  setTtsStyle(e.target.value)
                  ttsEnabledRef.current = true
                }}
                aria-label="Choose voice style"
              >
                <option value="default">Calm voice</option>
                <option value="warm">Warm voice</option>
                <option value="formal">Formal voice</option>
              </select>
              <input
                className="chat-input"
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message..."
                disabled={sending}
                autoFocus
              />
              <button
                className={`btn voice-button ${isListening ? 'listening' : ''}`}
                onClick={toggleListening}
                disabled={sending}
                title={speechSupported ? 'Speak a message' : 'Voice input is not supported'}
                aria-label={speechSupported ? 'Speak a message' : 'Voice input is not supported'}
              >
                {isListening ? '⏹' : '🎙'}
              </button>
              <button className="btn btn-primary" onClick={handleSend} disabled={sending || !input.trim()}>
                {sending ? <span className="spinner"></span> : '➤'}
              </button>
            </div>
          )}
          {voiceError && <div className="voice-error">{voiceError}</div>}
        </div>
      </div>
    </>
  )
}
