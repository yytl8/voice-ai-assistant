# Voice AI Assistant — Stage 11 Full Production Integration

هذه المرحلة تربط مكونات النظام في طبقة Agent Runtime موحدة وتضيف اختبار E2E.

## Agent Runtime

كل Tool Call يمر:

```text
Realtime Event
  ↓
AgentRuntime
  ↓
RBAC
  ↓
Confirmation Gate
  ↓
Business Tool
  ↓
M-One
  ↓
Tool Result
  ↓
Realtime Event
```

## Confirmation

التأكيد ليس Boolean ثابتاً فقط؛ يوجد token قصير العمر مرتبط بـ:
- session
- tool
- arguments

ويُستهلك مرة واحدة.

## Resume

Redis يحتفظ بآخر الأحداث مع `sequence`.
عند reconnect يستطيع العميل طلب الأحداث بعد آخر sequence.

## E2E

تمت إضافة Playwright scaffold لاختبار واجهة المساعد.

## Local production-like stack

```bash
docker compose up --build
docker compose exec backend alembic upgrade head
```

ثم:

```bash
cd frontend
npm install
npx playwright install --with-deps chromium
npm run e2e
```

## ملاحظة

لا يتم اعتبار اختبار WebRTC أو M-One ناجحاً لمجرد وجود الكود. يجب تنفيذ الاختبار في بيئة staging مع credentials وخدمات فعلية.
