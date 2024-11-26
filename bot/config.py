BOT_TOKEN = "5973522500:AAFbdBnRKDPJJflVmfUIIUydA0qW2itU8mk"

SUPER_ADMIN_ID = 37454511
ADMIN_IDS = [37454511]

WORKING_HOURS = {
    "start": 9,
    "end": 21,
    "interval": 30
}

PAYMENT = {
    "merchant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "callback_url": "https://example.com/verify",
}

AI_CONFIG = {
    "api_key": "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",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 150,
    "responses": {
        "greeting": "سلام! من دستیار هوشمند سالن زیبایی هستم. چطور میتونم کمکتون کنم؟",
        "booking": "برای رزرو نوبت میتونید از منوی اصلی گزینه «رزرو نوبت» رو انتخاب کنید.",
        "services": "خدمات ما شامل کوتاهی مو، رنگ مو، اصلاح ابرو، میکاپ و... میشه.",
        "fallback": "متوجه نشدم. لطفا واضح‌تر بگید یا از منوی اصلی استفاده کنید."
    }
}
