import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SendgridMessageAssociation
from .signals import email_received

logger = logging.getLogger('gidsy.apps.sendgrid')


@csrf_exempt
def receiver(request):
    logger.debug("Sendgrid receive: POST: %s, GET: %s"%(request.POST, request.GET) )

    if request.method == 'GET':
        return  HttpResponse(status=400, content="Not Allowed")
        
    data = request.POST
    to = data.get('to')
    
    if '<' in to and '>' in to:
        to = data.get('to').split('<', 1)[1].rstrip('>')

    parse = to.split('+', 1)

    if len(parse) != 2:
        return  HttpResponse(status=400, content="Address not valid")

    app_id = parse[0]
    uuid = parse[1].split('@', 1)[0]
    
    if not app_id:
        return  HttpResponse(status=400, content="Application ID not specified")
        
    if not uuid:
        return  HttpResponse(status=400, content="UUID not specified")
    
    sma = SendgridMessageAssociation.objects.filter(uuid=uuid)
    if not sma:
        return  HttpResponse(status=400, content="UUID not valid")
    else:
        sma = sma[0]
        
    html = data.get('html')
    text = data.get('text')
    from_field = data.get('from')
    
    email_received.send(sender=SendgridMessageAssociation, sma=sma, app_id=app_id, html=html, text=text, from_field=from_field)
    
    return HttpResponse(status=200, content="ok")
    
