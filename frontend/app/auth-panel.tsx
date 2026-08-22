'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
        body: JSON.stringify(
          mode === 'register'
            ? {email, password, display_name: name || 'مستخدم'}
            : {email, password}
        ),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'فشل تسجيل الدخول');
      localStorage.setItem('voice_ai_token', data.access_token);
      onAuth(data.access_token);
    } catch (err: any) {
      setError(err.message || 'حدث خطأ');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="authCard">
      <div className="authTitle">{mode === 'login' ? 'تسجيل الدخول' : 'إنشاء حساب'}</div>
      {mode === 'register' && (
        <input placeholder="الاسم" value={name} onChange={(e) => setName(e.target.value)} />
      )}
      <input dir="ltr" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input dir="ltr" type="password" placeholder="كلمة المرور" value={password} onChange={(e) => setPassword(e.target.value)} />
      {error && <div className="authError">{error}</div>}
      <button className="authSubmit" disabled={loading}>
        {loading ? 'جاري...' : mode === 'login' ? 'دخول' : 'إنشاء الحساب'}
      </button>
      <button type="button" className="authSwitch" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'ليس لديك حساب؟ إنشاء حساب' : 'لديك حساب؟ تسجيل الدخول'}
      </button>
    </div>
  );
}
