'use client';

import { useEffect, useState } from 'react';
import AuthPanel from './auth-panel';
import VoiceAssistant from './voice-assistant';

export default function Page() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem('voice_ai_token'));
  }, []);

  if (!token) {
    return (
      <main className="authPage">
        <div className="brand authBrand"><span className="brandDot" />VOICE AI AGENT</div>
        <AuthPanel onAuth={setToken} />
      </main>
    );
  }

  return <VoiceAssistant />;
}
