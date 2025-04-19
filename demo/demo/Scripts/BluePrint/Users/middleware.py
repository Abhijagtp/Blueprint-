from django.utils.deprecation import MiddlewareMixin
from .models import SiteVisit

class VisitCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        visit, created = SiteVisit.objects.get_or_create(id=1)
        visit.count += 1
        visit.save()