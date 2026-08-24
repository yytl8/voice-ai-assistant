'use client';

import { useEffect, useState } from 'react';
import AuthPanel from './auth-panel';
import VoiceAssistant from './voice-assistant';
import { apiFetch } from './api';

export default function Page() {
  const [token, setToken] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem('voice_ai_token');
    if (!saved) { setChecking(false); return; }
    apiFetch('/api/auth/me', saved)
      .then((res) => {
        if (res.ok) setToken(saved);
        else localStorage.removeItem('voice_ai_token');
      })
      .catch(() => localStorage.removeItem('voice_ai_token'))
      .finally(() => setChecking(false));
  }, []);

  if (checking) return <main className="authPage"><div className="loadingScreen">جاري التحقق من الجلسة…</div></main>;
  if (!token) {
    return <main className="authPage"><div className="brand authBrand"><span className="brandDot" />VOICE AI AGENT</div><AuthPanel onAuth={setToken} /></main>;
  }
  return <VoiceAssistant token={token} onLogout={() => { localStorage.removeItem('voice_ai_token'); setToken(null); }} />;
}
