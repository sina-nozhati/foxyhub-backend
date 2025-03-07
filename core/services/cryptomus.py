import hashlib
import json
import uuid
from typing import Dict, Any

import requests
from django.conf import settings


class CryptomusClient:
    """
    Client for interacting with the Cryptomus payment gateway API.
    """
    BASE_URL = "https://api.cryptomus.com/v1"
    
    def __init__(self):
        self.merchant_id = settings.CRYPTOMUS_MERCHANT_ID
        self.api_key = settings.CRYPTOMUS_API_KEY
        
    def _generate_sign(self, payload: Dict[str, Any]) -> str:
        """
        Generate signature for Cryptomus API requests.
        """
        encoded_payload = json.dumps(payload).encode()
        sign = hashlib.md5(
            base64.b64encode(encoded_payload) + self.api_key.encode()
        ).hexdigest()
        return sign
    
    def _get_headers(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate headers for Cryptomus API requests.
        """
        sign = self._generate_sign(payload)
        return {
            'merchant': self.merchant_id,
            'sign': sign,
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, amount: float, currency: str, order_id: str, 
                       description: str, callback_url: str) -> Dict[str, Any]:
        """
        Create a new payment in Cryptomus.
        """
        endpoint = f"{self.BASE_URL}/payment"
        
        payload = {
            'amount': str(amount),
            'currency': currency,
            'order_id': order_id,
            'description': description,
            'url_callback': callback_url,
            'is_payment_multiple': False,
        }
        
        headers = self._get_headers(payload)
        
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_payment_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of a payment by order ID.
        """
        endpoint = f"{self.BASE_URL}/payment/info"
        
        payload = {
            'order_id': order_id
        }
        
        headers = self._get_headers(payload)
        
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()

