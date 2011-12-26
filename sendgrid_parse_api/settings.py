from django.conf import settings

SENDGRID_EMAIL_DOMAIN = getattr(settings, 'SENDGRID_EMAIL_DOMAIN', "test.com")
SPAM_TRESHOLD = getattr(settings, 'SPAM_TRESHOLD', 4)