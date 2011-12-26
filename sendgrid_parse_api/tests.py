import logging
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .signals import email_received
from .utils import create_reply_email
from .models import SendgridMessageAssociation

logger = logging.getLogger('gidsy.apps.activity')


class SendgridTest(TestCase):
    fixtures=['initial_users_and_data.json']
    def test_receiver(self):
        c = Client()
        sma = create_reply_email('m', User.objects.get(pk=2), User.objects.get(pk=2))
        response = c.post(reverse("sendgrid_parse_receiver"), {
            "subject": "My test subject", 
            "to": "My test <m+%s@gidsy.com>"%sma.uuid,
            "html": "<div>My test html</div>",
            "text": "My test text",
            "from": "My Test <mytest@gidsy.com>",
            "dkim": "{email.sendgrid.com : passed}",
            "spam_score": "0",
            "spam_report": "not spam"
        })
        logger.debug(response.content)
        self.assertEquals(200, response.status_code)
        
    def test_get_request(self):
        c = Client()
        response = c.get(reverse("sendgrid_parse_receiver"), {})
        self.assertEquals(400, response.status_code)

    def test_uuid_creation(self):
        sma = SendgridMessageAssociation(app_id="m", user=User.objects.get(pk=2),
                                         content_object=User.objects.get(pk=2))
        self.assertEqual('', sma.uuid)
        sma.save()
        self.assertNotEqual(None, sma.uuid)
        uuid = sma.uuid
        sma.save()
        self.assertEqual(uuid, sma.uuid)

    def test_model_creation(self):
        SendgridMessageAssociation.objects.all().delete()
        self.assertEquals(0, SendgridMessageAssociation.objects.count())
        create_reply_email('m', User.objects.get(pk=2), User.objects.get(pk=2))
        self.assertEquals(1, SendgridMessageAssociation.objects.count())
        sendgrid_message = SendgridMessageAssociation.objects.all()[0]
        self.assertEquals(User.objects.get(pk=2), sendgrid_message.user)
        self.assertEquals(User.objects.get(pk=2), sendgrid_message.content_object)
        
    def test_model_creation_with_no_user(self):
        [s.delete() for s in SendgridMessageAssociation.objects.all()]
        self.assertEquals(0, len(SendgridMessageAssociation.objects.all()))
        create_reply_email('m', None, User.objects.get(pk=3))
        self.assertEquals(1, len(SendgridMessageAssociation.objects.all()))
        sendgrid_message = SendgridMessageAssociation.objects.all()[0]
        self.assertEquals(User.objects.get(pk=3), sendgrid_message.content_object)
        
    def test_email_received_signal(self):
        sma_test = create_reply_email('m', User.objects.get(pk=2), User.objects.get(pk=2))
        app_id_test = 'm'
        html_test = "<div>My test html</div>"
        text_test = "My test text"
        from_field_test = "My Test <mytest@gidsy.com>"
        
        def signal_received_email(sender, sma, app_id, html, text, from_field, **kwargs):
            email_received.disconnect(signal_received_email, dispatch_uid="my_test_id")
            logger.debug(sma.uuid)
            self.assertEquals(sma.uuid, sma_test.uuid)
            self.assertEquals(app_id, app_id_test)
            self.assertEquals(html, html_test)
            self.assertEquals(text, text_test)
            self.assertEquals(from_field, from_field_test)
            
        email_received.connect(signal_received_email, dispatch_uid="my_test_id")
        
        c = Client()
        response = c.post(reverse("sendgrid_parse_receiver"), {
            "to": "%s+%s@gidsy.com"%(app_id_test, sma_test.uuid),
            "html": html_test,
            "text": text_test,
            "from": from_field_test,
        })
        logger.debug(response.content)
        self.assertEquals(200, response.status_code)
       
