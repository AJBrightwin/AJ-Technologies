import json
import logging
import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import ClientReview, ContactEnquiry, ShowcaseProject

log = logging.getLogger(__name__)


def _projects(home_only=False):
    """Published showcase projects from the database, in the shape the page JavaScript expects."""
    qs = ShowcaseProject.objects.filter(is_published=True)
    if home_only:
        qs = qs.filter(show_on_home=True)[:3]
    try:
        return [p.to_public_dict() for p in qs]
    except Exception:  # never break the page if the database is briefly unreachable
        log.exception('Could not load showcase projects')
        return []


def _reviews():
    """Published client reviews for the home page (max 20)."""
    try:
        return [r.to_public_dict() for r in ClientReview.objects.filter(is_published=True)[:20]]
    except Exception:  # never break the page if the database is briefly unreachable (or the table is not created yet)
        log.exception('Could not load client reviews')
        return []


def index(request):
    """AJ Technologies home page."""
    return render(request, 'index.html', {'projects': _projects(home_only=True), 'reviews': _reviews()})


def about(request):
    """About Us page."""
    return render(request, 'about.html')


def services(request):
    """Services page."""
    return render(request, 'services.html')


def portfolio(request):
    """Portfolio page: projects come from the showcase_projects table."""
    return render(request, 'portfolio.html', {'projects': _projects()})


def contact(request):
    """Contact page."""
    return render(request, 'contact.html')


# ---------------------------------------------------------------------------
# Legal pages
# ---------------------------------------------------------------------------
def privacy(request):
    """Privacy Policy."""
    return render(request, 'privacy.html')


def terms(request):
    """Terms & Conditions."""
    return render(request, 'terms.html')


def service_delivery(request):
    """Service Delivery Policy."""
    return render(request, 'service_delivery.html')


def page_not_found(request, exception=None):
    """Custom 404 page. Django uses it automatically when DEBUG=False (see handler404 in config/urls.py)."""
    return render(request, '404.html', status=404)


# ---------------------------------------------------------------------------
# Quote form endpoint: both the home page form and the contact page form post here.
# ---------------------------------------------------------------------------
TIMELINES = {c for c, _ in ContactEnquiry.Timeline.choices}
METHODS = {c for c, _ in ContactEnquiry.ContactMethod.choices}


def _clean(value, limit):
    return str(value or '').strip()[:limit]


@require_POST
def submit_enquiry(request):
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'invalid'}, status=400)

    # Spam trap: real visitors never see or fill the hidden "website" field
    if _clean(data.get('website'), 100):
        return JsonResponse({'ok': True})

    errors = {}
    name = _clean(data.get('name'), 120)
    phone = _clean(data.get('phone'), 30)
    email = _clean(data.get('email'), 254)

    if not name:
        errors['name'] = 'required'
    if len(re.sub(r'\D', '', phone)) < 10:
        errors['phone'] = 'invalid'
    if email:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'invalid'
    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    services = data.get('services') or []
    if not isinstance(services, list):
        services = []
    services = [_clean(s, 80) for s in services if _clean(s, 80)][:15]

    timeline = _clean(data.get('timeline'), 10)
    method = _clean(data.get('contactMethod'), 10)
    source = _clean(data.get('source'), 10)
    via = _clean(data.get('via'), 10)

    try:
        ContactEnquiry.objects.create(
            name=name,
            phone=phone,
            email=email,
            business_name=_clean(data.get('business'), 160),
            services=services,
            timeline=timeline if timeline in TIMELINES else '',
            contact_method=method if method in METHODS else '',
            message=_clean(data.get('message'), 2000),
            source=source if source in ('home', 'contact') else 'contact',
            submitted_via=via if via in ('form', 'whatsapp') else 'form',
            language='ta' if data.get('lang') == 'ta' else 'en',
        )
    except Exception:  # database unreachable: the page shows a friendly "try again / use WhatsApp" message
        log.exception('Could not save contact enquiry')
        return JsonResponse({'ok': False, 'error': 'unavailable'}, status=503)
    return JsonResponse({'ok': True})