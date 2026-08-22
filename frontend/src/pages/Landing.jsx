import { Link } from 'react-router-dom'

const capabilities = [
  {
    number: '01',
    title: 'Voice conversations',
    text: 'Speak naturally through the browser microphone. The agent transcribes your words and answers aloud in real time.',
    tone: 'landing-card-blue',
  },
  {
    number: '02',
    title: 'Provider freedom',
    text: 'Switch between Google Gemini and local Ollama models without changing the conversation engine.',
    tone: 'landing-card-yellow',
  },
  {
    number: '03',
    title: 'Agent control',
    text: 'Create focused agents with their own prompts, models, languages, voices, and fallback settings.',
    tone: 'landing-card-green',
  },
  {
    number: '04',
    title: 'Call intelligence',
    text: 'Every response includes usage, latency, intent, and call-state signals for clear operational visibility.',
    tone: 'landing-card-pink',
  },
]

export default function Landing() {
  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link className="landing-brand" to="/">AI CALL AGENT</Link>
        <nav className="landing-nav-links" aria-label="Landing page navigation">
          <a href="#capabilities">Capabilities</a>
          <a href="#architecture">Architecture</a>
          <Link to="/dashboard">Control room</Link>
        </nav>
        <Link className="landing-nav-cta" to="/mock-call">Start call -&gt;</Link>
      </header>
      <section className="landing-hero">
        <div className="landing-hero-grid" aria-hidden="true"></div>
        <div className="landing-hero-copy">
          <div className="landing-eyebrow">AI CALLING AGENT / SYSTEM 01</div>
          <h1>Make every<br /><mark>conversation</mark><br />count.</h1>
          <p className="landing-lead">
            A provider-agnostic voice agent that listens, thinks, and responds with the speed of software and the clarity of a great operator.
          </p>
          <div className="landing-actions">
            <Link className="btn btn-primary landing-button" to="/mock-call">Start a voice call <span>-&gt;</span></Link>
            <Link className="landing-text-link" to="/dashboard">Open control room</Link>
          </div>
          <div className="landing-proof-row">
            <span><b className="proof-dot proof-green"></b> Browser voice</span>
            <span><b className="proof-dot proof-blue"></b> Gemini ready</span>
            <span><b className="proof-dot proof-yellow"></b> Ollama ready</span>
          </div>
          <div className="landing-hero-rail">
            <span><b>REC</b> / 001</span>
            <span><b>MODE</b> / LISTEN</span>
            <span><b>STATUS</b> / READY</span>
          </div>
        </div>
        <div className="landing-hero-art" aria-label="AI calling robot illustration">
          <div className="landing-art-label">INCOMING / AI-001</div>
          <div className="landing-art-signal signal-a"></div>
          <div className="landing-art-signal signal-b"></div>
          <div className="landing-robot-antenna"></div>
          <div className="landing-robot-head">
            <span className="landing-robot-eye"></span>
            <span className="landing-robot-eye"></span>
            <div className="landing-robot-mouth"><i></i><i></i><i></i></div>
          </div>
          <div className="landing-robot-body">
            <div className="landing-robot-screen">HELLO<br /><small>LISTENING</small></div>
            <div className="landing-robot-bars"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="landing-robot-arm landing-arm-left"></div>
          <div className="landing-robot-arm landing-arm-right"></div>
          <div className="landing-robot-hand landing-hand-left">+</div>
          <div className="landing-robot-hand landing-hand-right">+</div>
          <div className="landing-robot-leg landing-leg-left"></div>
          <div className="landing-robot-leg landing-leg-right"></div>
          <div className="landing-call-tag tag-one">VOICE<br /><b>ON</b></div>
          <div className="landing-call-tag tag-two">24<br /><small>MS</small></div>
          <div className="landing-live-panel">
            <div className="landing-live-header"><span className="landing-live-dot"></span> LIVE CALL MONITOR <b>00:24</b></div>
            <div className="landing-waveform" aria-hidden="true">
              <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
            </div>
            <div className="landing-live-footer"><span>LISTENING FOR INPUT</span><strong>AI-001</strong></div>
          </div>
        </div>
      </section>

      <section className="landing-section landing-statement">
        <div className="landing-section-index">/ 02</div>
        <div>
          <div className="landing-section-label">THE IDEA</div>
          <h2>One conversation layer.<br /><span>Every model underneath.</span></h2>
        </div>
        <p>Calling AI Agent keeps telephony-facing conversation logic independent from the LLM provider. Configure the model, keep the experience.</p>
      </section>

      <section className="landing-section" id="capabilities">
        <div className="landing-section-heading">
          <div>
            <div className="landing-section-label">WHAT IT DOES</div>
            <h2>Built for the<br />moment of contact.</h2>
          </div>
          <span className="landing-section-index">/ 03</span>
        </div>
        <div className="landing-capability-grid">
          {capabilities.map(capability => (
            <article className={`landing-capability ${capability.tone}`} key={capability.number}>
              <div className="landing-card-number">{capability.number}</div>
              <h3>{capability.title}</h3>
              <p>{capability.text}</p>
              <span className="landing-card-arrow">-&gt;</span>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section landing-architecture" id="architecture">
        <div className="landing-section-label">UNDER THE HOOD / 04</div>
        <div className="landing-flow">
          <div className="landing-flow-node"><b>01</b><span>VOICE</span><small>Browser mic</small></div>
          <div className="landing-flow-line"></div>
          <div className="landing-flow-node"><b>02</b><span>MANAGER</span><small>Conversation state</small></div>
          <div className="landing-flow-line"></div>
          <div className="landing-flow-node landing-flow-node-dark"><b>03</b><span>LLM</span><small>Gemini / Ollama</small></div>
          <div className="landing-flow-line"></div>
          <div className="landing-flow-node"><b>04</b><span>REPLY</span><small>Voice + transcript</small></div>
        </div>
      </section>

      <section className="landing-bottom-cta">
        <div>
          <div className="landing-eyebrow">READY WHEN YOU ARE</div>
          <h2>Put your next call<br /><span>on the record.</span></h2>
        </div>
        <Link className="btn btn-primary landing-button" to="/mock-call">Enter mock call <span>-&gt;</span></Link>
      </section>

      <footer className="landing-footer">
        <span>CALLING AI AGENT</span>
        <span>FASTAPI / REACT / GEMINI / OLLAMA</span>
        <span>01.2026</span>
      </footer>
    </div>
  )
}
