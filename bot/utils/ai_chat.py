import openai
from ..config import AI_CONFIG

class BeautySalonAI:
    def __init__(self):
        openai.api_key = AI_CONFIG['api_key']
        self.context = """
این یک ربات هوشمند برای سالن زیبایی است که می‌تواند:
- به سوالات درباره خدمات پاسخ دهد
- راهنمایی برای انتخاب خدمات ارائه دهد
- مشاوره زیبایی بدهد
- به سوالات متداول پاسخ دهد
"""
    
    def get_response(self, message):
        try:
            response = openai.ChatCompletion.create(
                model=AI_CONFIG['model'],
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return "متأسفانه در حال حاضر قادر به پاسخگویی نیستم. لطفاً بعداً تلاش کنید."
