'use client';

import { useEffect, useRef, useState } from 'react';

type Status = 'idle' | 'connecting' | 'listening' | 'thinking' | 'speaking' | 'error';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function VoiceAssistant() {
  const [status, setStatus] = useState<Status>('idle');
  const [transcript, setTranscript] = useState('');
  const [answer, setAnswer] = useState('');
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');
  const [memories, setMemories] = useState<{key: string; value: string}[]>([]);
  const [imageName, setImageName] = useState('');
  const token = typeof window !== 'undefined' ? localStorage.getItem('voice_ai_token') || '' : '';

  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/api/memory`, {headers: {Authorization: `Bearer ${token}`}})
      .then((r) => r.json())
      .then((data) => setMemories(data.memories || []))
      .catch(() => {});
  }, [token]);

  function sendEvent(event: Record<string, unknown>) {
    const dc = dcRef.current;
    if (dc?.readyState === 'open') dc.send(JSON.stringify(event));
  }

  async function executeToolCall(event: any) {
    const name = event.name;
    let argumentsObject: Record<string, unknown> = {};
    try {
      argumentsObject = JSON.parse(event.arguments || '{}');
    } catch {
      argumentsObject = {};
    }

    try {
      const response = await fetch(`${API_URL}/api/tools/execute`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`},
        body: JSON.stringify({name, arguments: argumentsObject}),
      });
      const result = await response.json();

      sendEvent({
        type: 'conversation.item.create',
        item: {
          type: 'function_call_output',
          call_id: event.call_id,
          output: JSON.stringify(result),
        },
      });
      sendEvent({type: 'response.create'});
    } catch (e: any) {
      sendEvent({
        type: 'conversation.item.create',
        item: {
          type: 'function_call_output',
          call_id: event.call_id,
          output: JSON.stringify({ok: false, error: e?.message || 'tool error'}),
        },
      });
      sendEvent({type: 'response.create'});
    }
  }

  function handleServerEvent(event: any) {
    const type = event?.type || '';

    if (type === 'session.created' || type === 'session.updated') {
      setConnected(true);
      setStatus('listening');
      return;
    }

    if (type === 'input_audio_buffer.speech_started') {
      setStatus('listening');
      return;
    }

    if (type === 'input_audio_buffer.speech_stopped') {
      setStatus('thinking');
      return;
    }

    if (type === 'conversation.item.input_audio_transcription.completed') {
      if (event.transcript) setTranscript(event.transcript);
      return;
    }

    if (type === 'response.function_call_arguments.done') {
      void executeToolCall(event);
      setStatus('thinking');
      return;
    }

    if (type === 'response.created' || type === 'response.output_item.added') {
      setStatus('speaking');
      return;
    }

    if (type === 'response.audio_transcript.delta') {
      setAnswer((prev) => prev + (event.delta || ''));
      setStatus('speaking');
      return;
    }

    if (type === 'response.audio_transcript.done') {
      if (event.transcript) setAnswer(event.transcript);
      return;
    }

    if (type === 'output_audio_buffer.started') {
      setStatus('speaking');
      return;
    }

    if (type === 'output_audio_buffer.cleared') {
      setStatus('listening');
      return;
    }

    if (type === 'output_audio_buffer.stopped' || type === 'response.done') {
      setStatus('listening');
      return;
    }

    if (type === 'error') {
      setError(event.error?.message || 'حدث خطأ في جلسة الصوت');
      setStatus('error');
    }
  }

  async function startSession() {
    setError('');
    setTranscript('');
    setAnswer('');
    setStatus('connecting');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {echoCancellation: true, noiseSuppression: true, autoGainControl: true},
      });
      streamRef.current = stream;

      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      pc.onconnectionstatechange = () => {
        const state = pc.connectionState;
        if (state === 'connected') {
          setConnected(true);
          setStatus('listening');
        } else if (state === 'failed' || state === 'disconnected' || state === 'closed') {
          setConnected(false);
        }
      };

      pc.ontrack = (event) => {
        const [remoteStream] = event.streams;
        if (audioRef.current && remoteStream) {
          audioRef.current.srcObject = remoteStream;
          void audioRef.current.play();
        }
      };

      stream.getTracks().forEach((track) => pc.addTrack(track, stream));

      const dc = pc.createDataChannel('oai-events');
      dcRef.current = dc;

      dc.onopen = () => {
        setConnected(true);
        setStatus('listening');

        sendEvent({
          type: 'session.update',
          session: {
            type: 'realtime',
            instructions:
              'تذكر المعلومات التي يضعها المستخدم في سياق المحادثة. استخدم الأدوات عند الحاجة. إذا طلب المستخدم حفظ معلومة دائمة، أخبر الواجهة أن هذه الميزة متاحة.',
            audio: {
              input: {
                transcription: {model: 'gpt-4o-mini-transcribe', language: 'ar'},
                turn_detection: {
                  type: 'server_vad',
                  threshold: 0.5,
                  prefix_padding_ms: 300,
                  silence_duration_ms: 500,
                  create_response: true,
                  interrupt_response: true,
                },
              },
            },
            output_modalities: ['audio'],
          },
        });
      };

      dc.onmessage = (event) => {
        try { handleServerEvent(JSON.parse(event.data)); } catch {}
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const response = await fetch(`${API_URL}/api/realtime/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/sdp',
          Authorization: `Bearer ${token}`,
        },
        body: offer.sdp,
      });

      if (!response.ok) throw new Error((await response.text()) || 'تعذر إنشاء جلسة Realtime');

      const answerSdp = await response.text();
      await pc.setRemoteDescription({type: 'answer', sdp: answerSdp});
    } catch (e: any) {
      setError(e?.message || 'تعذر تشغيل الميكروفون');
      setStatus('error');
      await stopSession();
    }
  }

  async function sendImage(file: File) {
    if (!dcRef.current || dcRef.current.readyState !== 'open') {
      setError('شغّل المحادثة الصوتية أولاً لإرسال صورة.');
      return;
    }
    if (!file.type.startsWith('image/')) {
      setError('الملف يجب أن يكون صورة.');
      return;
    }

    setImageName(file.name);
    setError('');

    const dataUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

    sendEvent({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {type: 'input_text', text: 'حلل هذه الصورة واذكر أهم ما تراه باختصار.'},
          {type: 'input_image', image_url: dataUrl},
        ],
      },
    });
    sendEvent({type: 'response.create'});
    setStatus('thinking');
  }

  async function stopSession() {
    sendEvent({type: 'response.cancel'});
    sendEvent({type: 'output_audio_buffer.clear'});
    dcRef.current?.close();
    dcRef.current = null;
    pcRef.current?.close();
    pcRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (audioRef.current) audioRef.current.srcObject = null;
    setConnected(false);
    setStatus('idle');
  }

  async function toggle() {
    if (status === 'idle' || status === 'error') await startSession();
    else await stopSession();
  }

  useEffect(() => () => { void stopSession(); }, []);

  const label = {
    idle: 'اضغط للتحدث',
    connecting: 'جاري الاتصال…',
    listening: 'أستمع إليك…',
    thinking: 'أفكر…',
    speaking: 'أتحدث…',
    error: 'حدث خطأ',
  }[status];

  return (
    <main className="page">
      <audio ref={audioRef} autoPlay playsInline />

      <div className="topbar">
        <div className="brand"><span className="brandDot" />VOICE AI</div>
        <div className={`connection ${connected ? 'online' : ''}`}>
          {connected ? 'Agent متصل' : 'غير متصل'}
        </div>
      </div>

      <section className="hero">
        <div className={`orb orb-${status}`} onClick={toggle}>
          <div className="orbCore" />
          <div className="ring ring1" />
          <div className="ring ring2" />
          <div className="ring ring3" />
        </div>

        <div className="status">{label}</div>

        <div className="conversation">
          <div className="bubble user">{transcript || 'تحدث مع المساعد أو أرسل صورة'}</div>
          {answer && <div className="bubble ai">{answer}</div>}
          {imageName && <div className="bubble">الصورة: {imageName}</div>}
          {error && <div className="bubble error">{error}</div>}
        </div>

        <div className="actions">
          <button className="micButton" onClick={toggle}>
            {status === 'idle' || status === 'error' ? '🎙' : '■'}
          </button>

          <label className="imageButton">
            📷 تحليل صورة
            <input
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void sendImage(file);
                e.currentTarget.value = '';
              }}
            />
          </label>
        </div>

        <div className="memory">
          <span>الذاكرة: {memories.length} معلومة</span>
          {memories.slice(0, 3).map((m) => (
            <span key={m.key} className="memoryChip">{m.key}: {m.value}</span>
          ))}
        </div>

        <p className="hint">Realtime + Tools + Memory + Vision</p>
      </section>
    </main>
  );
}
