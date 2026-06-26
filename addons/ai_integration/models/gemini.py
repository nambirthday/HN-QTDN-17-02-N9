import os
import logging

import requests
from odoo import models

_logger = logging.getLogger(__name__)


class AiGemini(models.Model):
    _name = 'ai.gemini'
    _description = 'AI Gemini wrapper'

    def _get_api_key(self):
        # Prefer environment variable for secrets
        key = os.environ.get('GEMINI_API_KEY')
        if key:
            return key
        # Fallback to system parameters (less secure)
        try:
            key = self.env['ir.config_parameter'].sudo().get_param('ai.gemini.key')
            return key
        except Exception:
            return None

    def _get_api_url(self):
        # Allow configuration of endpoint
        url = os.environ.get('GEMINI_API_URL')
        if url:
            return url
        try:
            url = self.env['ir.config_parameter'].sudo().get_param('ai.gemini.url')
            return url
        except Exception:
            return None

    def _get_telegram_bot_token(self):
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if token:
            return token
        try:
            token = self.env['ir.config_parameter'].sudo().get_param('telegram.bot.token')
            return token
        except Exception:
            return None

    def send_telegram_message(
        self,
        chat_id,
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
        timeout=10
    ):
        token = self._get_telegram_bot_token()
        if not token or not chat_id:
            _logger.debug('Telegram bot token or chat_id not configured')
            return False

        telegram_url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
        }
        try:
            resp = requests.post(telegram_url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return True
        except Exception as e:
            _logger.exception('Telegram send failed: %s', e)
            return False

    def generate_text(self, prompt: str, timeout: int = 10) -> str:
        """Call configured Gemini-like API and return text output.

        This is a generic wrapper: set `GEMINI_API_URL` and `GEMINI_API_KEY`
        as environment variables or system parameters `ai.gemini.url` and
        `ai.gemini.key` in Odoo Settings > Technical > System Parameters.
        """
        api_key = self._get_api_key()
        api_url = self._get_api_url()
        if not api_key or not api_url:
            _logger.debug('AI Gemini: API key or URL not configured')
            return ''

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'input': prompt
        }
        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Try common response shapes
            text = ''
            if isinstance(data, dict):
                # Common field names: 'output', 'text', 'result', 'choices'
                if 'output' in data and isinstance(data['output'], str):
                    text = data['output']
                elif 'text' in data and isinstance(data['text'], str):
                    text = data['text']
                elif 'result' in data and isinstance(data['result'], str):
                    text = data['result']
                elif 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                    first = data['choices'][0]
                    if isinstance(first, dict) and 'text' in first:
                        text = first['text']
                    elif isinstance(first, str):
                        text = first
            if not text:
                # fallback to raw text
                text = resp.text
            return text
        except Exception as e:
            _logger.exception('AI Gemini request failed: %s', e)
            return ''
