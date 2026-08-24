'use client';

import { useState } from 'react';
import { API_URL } from './api';

export default function AuthPanel({ onAuth }: { onAuth: (token: string) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/auth/${mode}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(mode === 'register'
          ? {email: email.trim(), password, display_name: name.trim() || 'مستخدم'}
          : {email: email.trim(), password}),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'تعذر تنفيذ العملية');
      }
      const data = await res.json();
      localStorage.setItem('voice_ai_token', data.access_token);
      onAuth(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'حدث خطأ غير متوقع');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="authCard" onSubmit={submit}>
      <div className="authTitle">{mode === 'login' ? 'مرحباً بعودتك' : 'إنشاء حساب جديد'}</div>
      <div className="authSubtitle">مساعد صوتي عربي مع أدوات وذاكرة ونماذج AI متعددة.</div>
      {mode === 'register' && (
        <input required placeholder="الاسم" value={name} onChange={(e) => setName(e.target.value)} />
      )}
      <input required dir="ltr" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input required minLength={6} dir="ltr" type="password" placeholder="كلمة المرور" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <div className="authError">{error}</div>}
      <button className="authSubmit" disabled={loading} type="submit">
        {loading ? 'جاري التنفيذ…' : mode === 'login' ? 'تسجيل الدخول' : 'إنشاء الحساب'}
      </button>
      <button type="button" className="authSwitch" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}>
        {mode === 'login' ? 'ليس لديك حساب؟ إنشاء حساب' : 'لديك حساب؟ تسجيل الدخول'}
      </button>
    </form>
  );
}
