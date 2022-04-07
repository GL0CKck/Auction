from django.utils.timezone import utc
import datetime

from .models import SubCategory, SubProduct


def category_context_processor(request):
    context = {}
    context["categorys"] = SubCategory.object.all()
    context["products"] = SubProduct.object.all()
    return context


class LastRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.last_request = datetime.datetime.utcnow().replace(tzinfo=utc)
            request.user.save()
        response = self.get_response(request)
        return response
