# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from . import settings

class SendgridMessageAssociation(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    app_id = models.CharField(max_length=9)
    uuid = models.CharField(max_length=36)
    user = models.ForeignKey(User, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def get_from_email(self):
        if self.user:
            return '"%s %s." <messaging@%s>'%(self.user.first_name, self.user.last_name[0], settings.SENDGRID_EMAIL_DOMAIN)
        else:
            return 'messaging@%s'%(settings.SENDGRID_EMAIL_DOMAIN)

    def get_reply_to_email(self):
        return '"Reply to Message" <%s+%s@%s>'%(self.app_id, self.uuid, settings.SENDGRID_EMAIL_DOMAIN)
		    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid=str(uuid.uuid4())
        super(SendgridMessageAssociation, self).save(*args, **kwargs)
	
    def __unicode__(self):
        return "%s-%s"%(self.uuid, self.user)

