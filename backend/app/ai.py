import httpx
from .settings import settings

SYSTEM_PROMPT = (
    "أنت مساعد صوتي عربي سريع وواضح. "
    "أجب بإيجاز مناسب للمحادثة الصوتية. "
    "لا تستخدم Markdown معقداً. "
    "لا تختلق بيانات أو نتائج أدوات غير موجودة."
)

class AIService:
    async def respond(self, history: list[dict]) -> str:
        if not settings.ai_api_key or not settings.ai_model:
            return self.demo_response(history[-1]["content"])

        url = settings.ai_base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-12:],
            ],
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    def demo_response(self, text: str) -> str:
        return (
            f"سمعتك تقول: {text}. "
            "وضع Demo يعمل حالياً. أضف إعدادات مزود الذكاء الاصطناعي "
            "في ملف البيئة لتفعيل الإجابات الحقيقية."
        )
