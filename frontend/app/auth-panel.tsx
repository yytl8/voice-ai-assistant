'use client';

import { useState } from 'react';
import { API_URL } from './api';

const STATUS_MESSAGES: Record<number, string> = {
  400: 'البيانات المرسلة غير صحيحة. تحقق من الحقول وحاول مجدداً.',
  401: 'البريد الإلكتروني أو كلمة المرور غير صحيحة.',
  403: 'هذا الحساب غير مفعّل حالياً.',
  404: 'تعذر الوصول إلى الخادم (المسار غير موجود). تأكد من إعداد الاتصال بالخادم.',
  409: 'هذا البريد الإلكتروني مستخدم بالفعل.',
  422: 'بيانات التسجيل غير صحيحة. تحقق من البريد الإلكتروني وكلمة المرور.',
  429: 'محاولات كثيرة جداً. حاول مرة أخرى بعد قليل.',
  500: 'حدث خطأ داخلي في الخادم. حاول لاحقاً.',
  502: 'الخادم غير متاح حالياً. حاول لاحقاً.',
  503: 'الخدمة غير متاحة حالياً. حاول لاحقاً.',
};

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

    if (!API_URL) {
      // NEXT_PUBLIC_API_URL wasn't baked into this build, so every request
      // would silently hit the frontend's own origin. Fail fast with a
      // clear message instead of a confusing 404 further down.
      if (process.env.NODE_ENV !== 'production') {
        console.error('[auth] NEXT_PUBLIC_API_URL is empty; requests would go to the frontend origin.');
      }
      setError('تعذر الاتصال بالخادم: لم يتم ضبط عنوان الـ API. تواصل مع الدعم الفني.');
      setLoading(false);
      return;
    }

    const url = `${API_URL}/api/auth/${mode}`;
    const body = JSON.stringify(mode === 'register'
      ? {email: email.trim(), password, display_name: name.trim() || 'مستخدم'}
      : {email: email.trim(), password});

    let res: Response;
    try {
      res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body,
      });
    } catch (err) {
      // fetch() throws before we get a Response for network failures and
      // CORS rejections (the browser hides the real reason from JS in the
      // CORS case). Distinguish this from an HTTP error response below.
      if (process.env.NODE_ENV !== 'production') {
        console.error('[auth] network/CORS error', { url, method: 'POST', error: err });
      }
      setError('تعذر الاتصال بالخادم. تحقق من اتصالك بالإنترنت أو حاول لاحقاً.');
      setLoading(false);
      return;
    }

    try {
      if (!res.ok) {
        const raw = await res.text();
        let detail: string | undefined;
        try {
          detail = JSON.parse(raw)?.detail;
        } catch {
          // Non-JSON body (e.g. an HTML error page from a misrouted
          // request) -- fall through to the status-based message below.
        }
        if (process.env.NODE_ENV !== 'production') {
          console.error('[auth] request failed', { url, method: 'POST', status: res.status, body: raw.slice(0, 500) });
        }
        throw new Error(detail || STATUS_MESSAGES[res.status] || 'تعذر تنفيذ العملية. حاول مرة أخرى.');
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
