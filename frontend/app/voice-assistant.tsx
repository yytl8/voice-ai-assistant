'use client';

import { useEffect, useRef, useState } from 'react';
import { API_URL, apiFetch, readApiError } from './api';

type Status = 'idle' | 'connecting' | 'listening' | 'thinking' | 'speaking' | 'error';
type Model = { alias: string; provider: string; model: string };
type ChatMessage = { role: 'user' | 'assistant'; content: string; provider?: string; model?: string };

export default function VoiceAssistant({ token, onLogout }: { token: string; onLogout: () => void }) {
  const [status, setStatus] = useState<Status>('idle');
  const [transcript, setTranscript] = useState('');
  const [answer, setAnswer] = useState('');
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');
  const [memories, setMemories] = useState<{key: string; value: string}[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState('auto');
  const [fallbacks, setFallbacks] = useState<string[]>([]);
  const [autoMode, setAutoMode] = useState(true);
  const [text, setText] = useState('');
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [imageName, setImageName] = useState('');

  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch('/api/memory', token).then(r => r.ok ? r.json() : null),
      apiFetch('/api/ai/models', token).then(r => r.ok ? r.json() : null),
    ]).then(([memoryData, modelData]) => {
      if (memoryData) setMemories(memoryData.memories || []);
      const available = modelData?.models || [];
      setModels(available);
      const recommended = modelData?.recommended_model;
      const order = Array.isArray(modelData?.fallback_order) ? modelData.fallback_order : [];
      if (recommended) {
        setSelectedModel(recommended);
        setFallbacks(order.filter((x: string) => x !== recommended));
      } else if (available.length && !available.some((m: Model) => m.alias === selectedModel)) {
        setSelectedModel(available[0].alias);
      }
    }).catch(() => {});
  }, [token]);

  function logout() { void stopSession(); onLogout(); }

  function sendEvent(event: Record<string, unknown>) {
    const dc = dcRef.current;
    if (dc?.readyState === 'open') dc.send(JSON.stringify(event));
  }

  async function sendText() {
    const content = text.trim();
    if (!content || busy) return;
    setText('');
    setChat(v => [...v, { role: 'user', content }]);
    setBusy(true); setError('');
    try {
      const history = [...chat, { role: 'user' as const, content }].slice(-12);
      const res = await apiFetch('/api/ai/chat', token, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          model: autoMode ? 'auto' : selectedModel,
          fallback: autoMode ? [] : fallbacks,
          messages: history.map(m => ({ role: m.role, content: m.content })),
        }),
      });
      if (!res.ok) throw new Error(await readApiError(res, 'تعذر الحصول على رد من النموذج'));
      const data = await res.json();
      setChat(v => [...v, { role: 'assistant', content: data.content, provider: data.provider, model: data.model }]);
    } catch (e) { setError(e instanceof Error ? e.message : 'حدث خطأ'); }
    finally { setBusy(false); }
  }

  async function executeToolCall(event: any) {
    let argumentsObject: Record<string, unknown> = {};
    try { argumentsObject = JSON.parse(event.arguments || '{}'); } catch {}
    try {
      const response = await apiFetch('/api/tools/execute', token, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: event.name, arguments: argumentsObject}),
      });
      const result = await response.json();
      sendEvent({type: 'conversation.item.create', item: {type: 'function_call_output', call_id: event.call_id, output: JSON.stringify(result)}});
      sendEvent({type: 'response.create'});
    } catch (e) {
      sendEvent({type: 'conversation.item.create', item: {type: 'function_call_output', call_id: event.call_id, output: JSON.stringify({ok: false, error: e instanceof Error ? e.message : 'tool error'})}});
      sendEvent({type: 'response.create'});
    }
  }

  function handleServerEvent(event: any) {
    const type = event?.type || '';
    if (type === 'session.created' || type === 'session.updated') { setConnected(true); setStatus('listening'); return; }
    if (type === 'input_audio_buffer.speech_started') { setStatus('listening'); return; }
    if (type === 'input_audio_buffer.speech_stopped') { setStatus('thinking'); return; }
    if (type === 'conversation.item.input_audio_transcription.completed') { if (event.transcript) setTranscript(event.transcript); return; }
    if (type === 'response.function_call_arguments.done') { void executeToolCall(event); setStatus('thinking'); return; }
    if (type === 'response.created' || type === 'response.output_item.added' || type === 'output_audio_buffer.started') { setStatus('speaking'); return; }
    if (type === 'response.audio_transcript.delta') { setAnswer((prev) => prev + (event.delta || '')); setStatus('speaking'); return; }
    if (type === 'response.audio_transcript.done') { if (event.transcript) setAnswer(event.transcript); return; }
    if (type === 'output_audio_buffer.cleared' || type === 'output_audio_buffer.stopped' || type === 'response.done') { setStatus('listening'); return; }
    if (type === 'error') { setError(event.error?.message || 'حدث خطأ في جلسة الصوت'); setStatus('error'); }
  }

  async function startSession() {
    setError(''); setTranscript(''); setAnswer(''); setStatus('connecting');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, noiseSuppression: true, autoGainControl: true}});
      streamRef.current = stream;
      const pc = new RTCPeerConnection(); pcRef.current = pc;
      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') { setConnected(true); setStatus('listening'); }
        if (['failed', 'disconnected', 'closed'].includes(pc.connectionState)) setConnected(false);
      };
      pc.ontrack = (event) => { const [remoteStream] = event.streams; if (audioRef.current && remoteStream) { audioRef.current.srcObject = remoteStream; void audioRef.current.play(); } };
      stream.getTracks().forEach(track => pc.addTrack(track, stream));
      const dc = pc.createDataChannel('oai-events'); dcRef.current = dc;
      dc.onopen = () => { setConnected(true); setStatus('listening'); sendEvent({type: 'session.update', session: {type: 'realtime', instructions: 'أنت مساعد صوتي عربي طبيعي وسريع. استخدم الأدوات عند الحاجة ولا تخترع نتائجها.', audio: {input: {transcription: {model: 'gpt-4o-mini-transcribe', language: 'ar'}, turn_detection: {type: 'server_vad', threshold: 0.5, prefix_padding_ms: 300, silence_duration_ms: 500, create_response: true, interrupt_response: true}},}, output_modalities: ['audio']}}); };
      dc.onmessage = e => { try { handleServerEvent(JSON.parse(e.data)); } catch {} };
      const offer = await pc.createOffer(); await pc.setLocalDescription(offer);
      const response = await fetch(`${API_URL}/api/realtime/session`, {method: 'POST', headers: {'Content-Type': 'application/sdp', Authorization: `Bearer ${token}`}, body: offer.sdp || ''});
      if (!response.ok) throw new Error(await readApiError(response, 'تعذر إنشاء جلسة الصوت'));
      const answerType = response.headers.get('content-type') || '';
      const answerText = await response.text();
      let answerSdp = answerText;
      if (answerType.includes('application/json')) {
        try { answerSdp = JSON.parse(answerText)?.sdp || ''; } catch {}
      }
      if (!answerSdp) throw new Error('لم يصل SDP صالح من خادم الصوت');
      await pc.setRemoteDescription({type: 'answer', sdp: answerSdp});
    } catch (e) { setError(e instanceof Error ? e.message : 'تعذر تشغيل الميكروفون'); setStatus('error'); await stopSession(); }
  }

  async function sendImage(file: File) {
    if (!file.type.startsWith('image/')) { setError('الملف يجب أن يكون صورة.'); return; }
    setImageName(file.name); setError('');
    if (!dcRef.current || dcRef.current.readyState !== 'open') { setError('شغّل المحادثة الصوتية أولاً لتحليل الصورة عبر جلسة Realtime.'); return; }
    const dataUrl = await new Promise<string>((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.onerror = reject; reader.readAsDataURL(file); });
    sendEvent({type: 'conversation.item.create', item: {type: 'message', role: 'user', content: [{type: 'input_text', text: 'حلل هذه الصورة واذكر أهم ما تراه باختصار.'}, {type: 'input_image', image_url: dataUrl}]}});
    sendEvent({type: 'response.create'}); setStatus('thinking');
  }

  async function stopSession() {
    sendEvent({type: 'response.cancel'}); sendEvent({type: 'output_audio_buffer.clear'});
    dcRef.current?.close(); dcRef.current = null; pcRef.current?.close(); pcRef.current = null;
    streamRef.current?.getTracks().forEach(track => track.stop()); streamRef.current = null;
    if (audioRef.current) audioRef.current.srcObject = null;
    setConnected(false); setStatus('idle');
  }

  useEffect(() => () => { void stopSession(); }, []);
  const label = {idle: 'اضغط للتحدث', connecting: 'جاري الاتصال…', listening: 'أستمع إليك…', thinking: 'أفكر…', speaking: 'أتحدث…', error: 'حدث خطأ'}[status];

  return (
    <main className="page">
      <audio ref={audioRef} autoPlay playsInline />
      <div className="topbar">
        <div className="brand"><span className="brandDot" />VOICE AI</div>
        <div className="topbarActions">
          <label className="autoModel">
            <input type="checkbox" checked={autoMode} onChange={e => setAutoMode(e.target.checked)} disabled={!models.length || busy} />
            تلقائي
          </label>
          <select value={selectedModel} onChange={e => { setSelectedModel(e.target.value); setAutoMode(false); }} disabled={!models.length || busy || autoMode} aria-label="النموذج">
            {models.length ? models.map(m => <option key={m.alias} value={m.alias}>{m.alias} · {m.provider}</option>) : <option value="primary">primary</option>}
          </select>
          {!autoMode && models.length > 1 && <select value={fallbacks[0] || ''} onChange={e => setFallbacks(e.target.value ? [e.target.value] : [])} aria-label="النموذج الاحتياطي"><option value="">بدون احتياطي</option>{models.filter(m => m.alias !== selectedModel).map(m => <option key={m.alias} value={m.alias}>احتياطي: {m.alias}</option>)}</select>}
          <div className={`connection ${connected ? 'online' : ''}`}>{connected ? 'Agent متصل' : 'غير متصل'}</div>
          <button className="logoutButton" onClick={logout}>خروج</button>
        </div>
      </div>

      <section className="hero">
        <div className={`orb orb-${status}`} onClick={() => status === 'idle' || status === 'error' ? void startSession() : void stopSession()}><div className="orbCore" /><div className="ring ring1" /><div className="ring ring2" /><div className="ring ring3" /></div>
        <div className="status">{label}</div>
        <div className="conversation">
          {chat.slice(-4).map((m, i) => <div key={i} className={`bubble ${m.role === 'user' ? 'user' : 'ai'}`}>{m.content}{m.model && <small className="modelMeta">{m.provider} · {m.model}</small>}</div>)}
          {transcript && <div className="bubble user">{transcript}</div>}
          {answer && <div className="bubble ai">{answer}</div>}
          {imageName && <div className="bubble">الصورة: {imageName}</div>}
          {error && <div className="bubble error">{error}</div>}
        </div>
        <div className="textComposer">
          <input value={text} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') void sendText(); }} placeholder="اكتب طلبك أو اسأل النموذج المختار…" disabled={busy} />
          <button onClick={() => void sendText()} disabled={busy || !text.trim()}>{busy ? '…' : 'إرسال'}</button>
        </div>
        <div className="actions">
          <button className="micButton" onClick={() => status === 'idle' || status === 'error' ? void startSession() : void stopSession()}>{status === 'idle' || status === 'error' ? '🎙' : '■'}</button>
          <label className="imageButton">📷 تحليل صورة<input type="file" accept="image/*" hidden onChange={e => { const f = e.target.files?.[0]; if (f) void sendImage(f); e.currentTarget.value = ''; }} /></label>
        </div>
        <div className="memory"><span>الذاكرة: {memories.length} معلومة</span>{memories.slice(0, 3).map(m => <span key={m.key} className="memoryChip">{m.key}: {m.value}</span>)}</div>
        <p className="hint">Realtime + Chat + Tools + Memory + Vision · النموذج المختار: {selectedModel}</p>
      </section>
    </main>
  );
}
