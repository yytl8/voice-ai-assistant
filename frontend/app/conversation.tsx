'use client';

import { useEffect, useRef, useState } from 'react';

type Message = { role: string; content: string; tool_name?: string | null };

export default function ConversationPanel() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState('');
  const [recording, setRecording] = useState(false);
  const recorder = useRef<MediaRecorder | null>(null);

  const api = (path: string, init?: RequestInit) =>
    fetch(path, { credentials: 'include', ...init });

  async function startConversation() {
    const r = await api('/api/conversations', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title: 'محادثة صوتية'}),
    });
    if (!r.ok) return;
    const data = await r.json();
    setConversationId(data.id);
    setMessages([]);
  }

  async function send() {
    if (!text.trim() || !conversationId) return;
    const content = text.trim();
    setText('');
    setMessages(v => [...v, {role: 'user', content}]);
    await api(`/api/conversations/${conversationId}/messages?role=user&content=${encodeURIComponent(content)}`, {
      method: 'POST',
    });
  }

  async function toggleRecording() {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    const r = new MediaRecorder(stream);
    recorder.current = r;
    r.ondataavailable = () => {};
    r.onstop = () => stream.getTracks().forEach(t => t.stop());
    r.start();
    setRecording(true);
  }

  useEffect(() => {
    if (!conversationId) startConversation();
  }, [conversationId]);

  return (
    <section className="conversation-panel">
      <div className="conversation-header">
        <div>
          <strong>ذكاء صناعي متحدث</strong>
          <small>M-One AI Agent</small>
        </div>
        <button onClick={startConversation}>محادثة جديدة</button>
      </div>

      <div className="conversation-messages">
        {messages.length === 0 && (
          <div className="conversation-empty">
            تحدث معي أو اكتب أمراً مثل: «ابحث عن العميل أحمد»
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            {m.content}
          </div>
        ))}
      </div>

      <div className="conversation-input">
        <button className={recording ? 'recording' : ''} onClick={toggleRecording}>
          {recording ? 'إيقاف' : '🎙️'}
        </button>
        <input
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="تحدث أو اكتب طلبك..."
        />
        <button onClick={send}>إرسال</button>
      </div>
    </section>
  );
}
