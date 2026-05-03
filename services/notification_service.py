"""
Notification Service for UAV Security ML.

Sends threat alerts via:
  - Telegram Bot API (instant push to phone/watch)
  - Email (SMTP fallback)
  - Browser Push Notifications (handled client-side)
"""
import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Manages threat alert notifications across multiple channels."""

    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.email_host = os.getenv('EMAIL_HOST', '')
        self.email_port = int(os.getenv('EMAIL_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_recipient = os.getenv('EMAIL_RECIPIENT', '')
        self.notifications_enabled = os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'

    @property
    def telegram_configured(self):
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def email_configured(self):
        return bool(self.email_host and self.email_user and self.email_password)

    def send_threat_alert(self, prediction, confidence, threat_level, features=None, detection_id=None):
        """
        Send a threat alert through all configured channels.

        Args:
            prediction: Threat type string (e.g., 'Jamming Attack')
            confidence: Float confidence score (0-1)
            threat_level: Severity string ('Low', 'Medium', 'High', 'Critical')
            features: Optional dict of feature values
            detection_id: Optional detection record ID

        Returns:
            dict with results from each channel
        """
        if not self.notifications_enabled:
            return {'sent': False, 'reason': 'notifications disabled'}

        # Only send for actual threats, not normal
        if prediction == 'Normal':
            return {'sent': False, 'reason': 'normal prediction, no alert needed'}

        results = {}

        # Telegram
        if self.telegram_configured:
            try:
                results['telegram'] = self._send_telegram(
                    prediction, confidence, threat_level, features, detection_id
                )
            except Exception as e:
                logger.error(f"Telegram notification error: {e}")
                results['telegram'] = {'success': False, 'error': str(e)}

        # Email
        if self.email_configured:
            try:
                results['email'] = self._send_email(
                    prediction, confidence, threat_level, features, detection_id
                )
            except Exception as e:
                logger.error(f"Email notification error: {e}")
                results['email'] = {'success': False, 'error': str(e)}

        sent = any(r.get('success') for r in results.values())
        return {'sent': sent, 'channels': results}

    def _send_telegram(self, prediction, confidence, threat_level, features, detection_id):
        """Send alert via Telegram Bot API."""
        severity_emoji = {
            'Critical': '🚨🔴',
            'High': '⚠️🟠',
            'Medium': '⚡🟡',
            'Low': '🟢',
        }
        emoji = severity_emoji.get(threat_level, '⚠️')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = (
            f"{emoji} *UAV THREAT DETECTED*\n\n"
            f"🎯 *Threat:* {prediction}\n"
            f"📊 *Confidence:* {confidence:.1%}\n"
            f"🔒 *Severity:* {threat_level}\n"
            f"🕐 *Time:* {timestamp}\n"
        )

        if detection_id:
            message += f"🆔 *Detection ID:* #{detection_id}\n"

        if features:
            message += "\n📋 *Key Telemetry:*\n"
            key_features = ['signal_strength', 'gps_accuracy', 'altitude', 'speed', 'vibration']
            for feat in key_features:
                if feat in features:
                    display_name = feat.replace('_', ' ').title()
                    message += f"  • {display_name}: {features[feat]}\n"

        message += "\n⚡ _Check UAV Security Dashboard for details_"

        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True,
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        logger.info(f"Telegram alert sent: {prediction} ({threat_level})")
        return {'success': result.get('ok', False)}

    def _send_email(self, prediction, confidence, threat_level, features, detection_id):
        """Send alert via SMTP email."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        subject = f"[UAV Security] {threat_level} Alert: {prediction}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #1e293b; color: #e2e8f0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #0f172a; border-radius: 12px; padding: 30px; border: 1px solid #334155;">
                <h2 style="color: #ef4444; margin: 0 0 20px;">🚨 UAV Threat Detected</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px; color: #94a3b8;">Threat Type:</td><td style="padding: 8px; font-weight: bold; color: #f8fafc;">{prediction}</td></tr>
                    <tr><td style="padding: 8px; color: #94a3b8;">Confidence:</td><td style="padding: 8px; font-weight: bold; color: #f8fafc;">{confidence:.1%}</td></tr>
                    <tr><td style="padding: 8px; color: #94a3b8;">Severity:</td><td style="padding: 8px; font-weight: bold; color: {'#ef4444' if threat_level == 'Critical' else '#f59e0b'};">{threat_level}</td></tr>
                    <tr><td style="padding: 8px; color: #94a3b8;">Time:</td><td style="padding: 8px; color: #f8fafc;">{timestamp}</td></tr>
                    {'<tr><td style="padding: 8px; color: #94a3b8;">Detection ID:</td><td style="padding: 8px; color: #f8fafc;">#' + str(detection_id) + '</td></tr>' if detection_id else ''}
                </table>
                <p style="margin-top: 20px; color: #94a3b8; font-size: 12px;">— UAV Security ML System</p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = self.email_recipient
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(self.email_host, self.email_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, self.email_recipient, msg.as_string())

        logger.info(f"Email alert sent: {prediction} ({threat_level})")
        return {'success': True}

    def send_test_notification(self):
        """Send a test notification to verify configuration."""
        return self.send_threat_alert(
            prediction='Test Alert',
            confidence=0.95,
            threat_level='Medium',
            features={'signal_strength': 25, 'gps_accuracy': 15, 'altitude': 50},
            detection_id=0,
        )

    def get_status(self):
        """Return notification configuration status."""
        return {
            'enabled': self.notifications_enabled,
            'telegram': {
                'configured': self.telegram_configured,
                'bot_token_set': bool(self.telegram_bot_token),
                'chat_id_set': bool(self.telegram_chat_id),
            },
            'email': {
                'configured': self.email_configured,
                'host': self.email_host or 'not set',
            },
        }


# Global notification service instance
notification_service = NotificationService()
