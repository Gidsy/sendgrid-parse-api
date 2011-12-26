import django.dispatch

email_received = django.dispatch.Signal(providing_args=["sma", "app_id", "html", "text", "from_field"])