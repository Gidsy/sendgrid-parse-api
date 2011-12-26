from .models import SendgridMessageAssociation

def create_reply_email(app_id, user=None, obj=None):
    sma = SendgridMessageAssociation(app_id=app_id, user=user, content_object=obj)
    sma.save()
    return sma