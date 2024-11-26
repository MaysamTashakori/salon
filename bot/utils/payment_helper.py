import requests
from ..config import PAYMENT

class PaymentGateway:
    @staticmethod
    def create_payment(amount, appointment_id):
        try:
            # ایجاد تراکنش در درگاه پرداخت
            data = {
                'merchant_id': PAYMENT['merchant_id'],
                'amount': amount,
                'callback_url': f"{PAYMENT['callback_url']}?appointment_id={appointment_id}",
                'description': f"پرداخت نوبت شماره {appointment_id}"
            }
            
            response = requests.post(
                'https://api.zarinpal.com/pg/v4/payment/request.json',
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['data']['code'] == 100:
                    return {
                        'status': 'success',
                        'payment_url': f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}",
                        'authority': result['data']['authority']
                    }
            
            return {
                'status': 'error',
                'message': 'خطا در ایجاد تراکنش'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @staticmethod
    def verify_payment(authority, amount):
        try:
            data = {
                'merchant_id': PAYMENT['merchant_id'],
                'authority': authority,
                'amount': amount
            }
            
            response = requests.post(
                'https://api.zarinpal.com/pg/v4/payment/verify.json',
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['data']['code'] == 100:
                    return {
                        'status': 'success',
                        'ref_id': result['data']['ref_id']
                    }
            
            return {
                'status': 'error',
                'message': 'تراکنش تایید نشد'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
def create_payment_link(amount, appointment_id):
    """Create payment link for ZarinPal gateway"""
    data = {
        "merchant_id": PAYMENT["merchant_id"],
        "amount": amount,
        "callback_url": f"{PAYMENT['callback_url']}?appointment_id={appointment_id}",
        "description": f"پرداخت نوبت شماره {appointment_id}"
    }
    
    # For testing without real payment gateway
    return f"https://example.com/pay/{appointment_id}?amount={amount}"

def verify_payment(authority, appointment_id):
    """Verify payment with ZarinPal"""
    # For testing purposes always return success
    return {
        "success": True,
        "ref_id": f"TEST-{appointment_id}-{authority}"
    }

def format_price(amount):
    """Format price in Toman"""
    return f"{amount:,} تومان"