
import React, { useState } from 'react'
import axios from 'axios'

export default function App() {
  const [template, setTemplate] = useState('summarize_v1')
  const [text, setText] = useState('The quick brown fox jumps over the lazy dog.')
  const [tone, setTone] = useState('neutral')
  const [length, setLength] = useState(30)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  async function runPrompt() {
    setLoading(true)
    try {
      const payload = { template_id: template, variables: { text, tone, length } }
      const r = await axios.post('/generate', payload)
      setResult(r.data)
    } catch (e:any) {
      alert('Error: ' + (e.message || e))
    } finally { setLoading(false) }
  }

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>PromptForge Playground</h1>
      <div>
        <label>Template: </label>
        <select value={template} onChange={e => setTemplate(e.target.value)}>
          <option value="summarize_v1">Summarize</option>
          <option value="qa_v1">Q&A</option>
        </select>
      </div>
      <div style={{ marginTop: 10 }}>
        <label>Text:</label><br />
        <textarea rows={6} cols={80} value={text} onChange={e => setText(e.target.value)} />
      </div>
      <div style={{ marginTop: 10 }}>
        <label>Tone: </label>
        <input value={tone} onChange={e => setTone(e.target.value)} />
        <label style={{ marginLeft: 10 }}>Length: </label>
        <input type="number" value={length} onChange={e => setLength(Number(e.target.value))} />
      </div>
      <div style={{ marginTop: 12 }}>
        <button onClick={runPrompt} disabled={loading}>{loading ? 'Running...' : 'Run'}</button>
      </div>
      <div style={{ marginTop: 20 }}>
        <h3>Result</h3>
        <pre>{result ? JSON.stringify(result, null, 2) : 'No result yet'}</pre>
      </div>
    </div>
  )
}
