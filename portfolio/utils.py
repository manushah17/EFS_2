from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    #context = Context(context_dict)
    html  = template.render(context_dict)
    #result = StringIO.StringIO()
    result = BytesIO()

    #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
        #return result.getvalue()
    return HttpResponse('We had some errors')

