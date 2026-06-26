from odoo import fields, models


class AiIntegrationSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gemini_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='ai.gemini.key',
        help='API key for Gemini AI service.',
    )
    gemini_api_url = fields.Char(
        string='Gemini API URL',
        config_parameter='ai.gemini.url',
        help='Endpoint URL for Gemini API requests.',
    )
    telegram_bot_token = fields.Char(
        string='Telegram Bot Token',
        config_parameter='telegram.bot.token',
        help='Token for Telegram bot. Use environment variable TELEGRAM_BOT_TOKEN for more secure deployment.',
    )
