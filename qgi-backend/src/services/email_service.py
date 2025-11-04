import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app
import logging

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@qgi.com')
        self.from_name = os.getenv('FROM_NAME', 'QGI Client Portal')
        
        if not self.api_key or self.api_key == 'your-sendgrid-api-key-here':
            raise ValueError("SENDGRID_API_KEY environment variable not set or using placeholder value")
        
        self.sg = SendGridAPIClient(api_key=self.api_key)
      
    def send_magic_link(self, to_email, magic_link, user_name=None):
        """Send magic link email to user"""
        try:
            # Create email content
            subject = "Your QGI Client Portal Login Link"
            # HTML email template
            html_content = self._get_magic_link_template(magic_link, user_name)
            # Plain text fallback
            text_content = f"""
            Hello{' ' + user_name if user_name else ''},
            Click the link below to securely access your QGI Client Portal:
            {magic_link}
            This link will expire in 10 minutes for your security.
            If you didn't request this login, please ignore this email.
            Best regards,
            QGI Team
            """
            # Create the email
            message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content),
            plain_text_content=Content("text/plain", text_content)
            )
            # Send the email
            response = self.sg.send(message)
            # Log success
            current_app.logger.info(f"Magic link email sent to {to_email}, status: {response.status_code}")
          
            return {
                'success': True,
                'message': 'Magic link sent successfully',
                'status_code': response.status_code
            }
        except Exception as e:
            # Log error
            current_app.logger.error(f"Failed to send magic link email to {to_email}: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }
    def _get_magic_link_template(self, magic_link, user_name=None):
        """Generate professional HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QGI Client Portal - Login Link</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 30px 0;
                    border-bottom: 2px solid #f0f0f0;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1f2937;
                }}
                .content {{
                    padding: 30px 0;
                }}
                .login-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                    text-align: center;
                }}
                .security-note {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    border-left: 4px solid #28a745;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px 0;
                    border-top: 1px solid #f0f0f0;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">📈 QGI Client Portal</div>
                <p>Secure access to your investment portfolio</p>
            </div>
            
            <div class="content">
                <h2>Hello{' ' + user_name if user_name else ''}!</h2>
                
                <p>You requested secure access to your QGI Client Portal. Click the button below to log in:</p>

                <div style="text-align: center;">
                    <a href="{magic_link}" class="login-button">
                        🔐 Access Your Portal
                    </a>
                </div>
                
                <div class="security-note">
                    <strong>🔒 Security Information:</strong>
                    <ul>
                        <li>This link will expire in <strong>10 minutes</strong></li>
                        <li>It can only be used once</li>
                        <li>If you didn't request this, please ignore this email</li>
                    </ul>
                </div>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {magic_link}
                </p>
                
                <p>Need help? Contact our support team at support@qgi.com</p>
            </div>
            
            <div class="footer">
                <p>© 2025 QGI. All rights reserved.</p>
                <p>This email was sent because you requested access to your client portal.</p>
            </div>
        </body>
        </html>
        """
        
# Create global instance
email_service = EmailService()
