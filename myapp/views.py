import logging
from functools import wraps

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .models import contactform, homeproject, portfolioproject, testimonial


logger = logging.getLogger(__name__)

ADMIN_USERNAME = 'AJB'
ADMIN_PASSWORD = '0803'


def _admin_session_required(view_func):

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        if not request.session.get('admin_logged_in'):

            return redirect('adminsignin')

        return view_func(request, *args, **kwargs)

    return _wrapped



def adminsignin(request):
    error_message = ''

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            request.session['admin_logged_in'] = True
            request.session['admin_username'] = ADMIN_USERNAME
            request.session['admin_login_fresh'] = True
            return redirect('admindashboard')

        error_message = 'Invalid admin username or password.'

    return render(request, 'adminsignin.html', {'error_message': error_message})


def adminlogout(request):

    request.session.pop('admin_logged_in', None)
    request.session.pop('admin_username', None)
    request.session.pop('admin_login_fresh', None)
    return redirect('adminsignin')


def _handle_contact_submission(request):

    uname = request.POST.get('username')
    mnumber = request.POST.get('phone')
    email = request.POST.get('email')
    message = request.POST.get('message')

    user = contactform(
        username=uname,
        mobile_number=mnumber,
        email=email,
        message=message,
    )
    user.save()

    try:
        from_email = (
            settings.DEFAULT_FROM_EMAIL
            or settings.EMAIL_HOST_USER
            or 'no-reply@ajtechnologiesltd.com'
        )
        email_subject = f"New Contact Message from {uname}"
        email_body = (
            f"Name: {uname}\n"
            f"Phone: {mnumber}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}\n"
        )
        email_message = EmailMessage(
            email_subject,
            email_body,
            from_email,
            ['ajtechnologieslimited@gmail.com'],
            reply_to=[email] if email else None,
        )
        email_message.send(fail_silently=False)
    except Exception as exc:
        logger.exception('Contact form email failed to send: %s', exc)

    request.session['user_id'] = user.id
    request.session['submission_success'] = True
    request.session['submission_message'] = 'Your email is received and our team will contact you soon.'


def _consume_submission_context(request):

    return {
        'submission_success': request.session.pop('submission_success', False),
        'submission_message': request.session.pop('submission_message', 'Your email is received and our team will contact you soon.'),
    }


def home(request):

    if request.method == 'POST':
        _handle_contact_submission(request)
        return redirect('success_page')

    return render(
        request,
        'index.html',
        {
            'homeprojects': homeproject.objects.all(),
            'testimonials': testimonial.objects.all(),
        },
    )


def about(request):

    return render(request, 'about.html')


def contact(request):

    if request.method == 'POST':
        _handle_contact_submission(request)
        return redirect('success_page')

    return render(request, 'contact.html')


def success(request):

    context = _consume_submission_context(request)

    return render(request, 'success.html', context)


def portfolio(request):

    return render(request, 'portfolio.html', {'portfolioprojects': portfolioproject.objects.all()})


def services(request):

    return render(request, 'services.html')


@_admin_session_required
def admindashboard(request):

    if request.method == 'GET':

        if not request.session.pop('admin_login_fresh', False):

            return redirect('adminsignin')

    if request.method == 'POST':

        if 'home_submit' in request.POST:

            homeproject.objects.create(
                project_name=request.POST.get('name'),
                project_Title=request.POST.get('title'),
                project_description=request.POST.get('description'),
                project_tag=request.POST.get('tag'),
                project_link=request.POST.get('link'),
                project_photo=request.FILES.get('project_photo'),
            )

            return redirect('/admindashboard/#index-dataview')

        elif 'portfolio_submit' in request.POST:

            portfolioproject.objects.create(
                portfolio_Title=request.POST.get('ptitle'),
                portfolio_description=request.POST.get('pdescription'),
                portfolio_tag=request.POST.get('ptag'),
                portfolio_link=request.POST.get('plink'),
                portfolio_image=request.FILES.get('portfolio_photo'),
            )

            return redirect('/admindashboard/#portfolio-dataview')

        elif 'delete_home_project' in request.POST:

            project_id = request.POST.get('project_id')

            try:
                homeproject.objects.get(id=project_id).delete()
                return redirect('/admindashboard/#index-dataview')
            except:
                return redirect('/admindashboard/#index-dataview')

        elif 'delete_portfolio_project' in request.POST:

            project_id = request.POST.get('project_id')

            try:
                portfolioproject.objects.get(id=project_id).delete()
                return redirect('/admindashboard/#portfolio-dataview')
            except:
                return redirect('/admindashboard/#portfolio-dataview')

        elif 'testimonial_submit' in request.POST:

            testimonial.objects.create(
                client_name=request.POST.get('client_name'),
                client_testimonial=request.POST.get('client_testimonial'),
                client_company=request.POST.get('client_company'),
            )

            return redirect('/admindashboard/#testimonials-dataview')

        elif 'delete_testimonial' in request.POST:

            testimonial_id = request.POST.get('testimonial_id')

            try:
                testimonial.objects.get(id=testimonial_id).delete()
                return redirect('/admindashboard/#testimonials-dataview')
            except:
                return redirect('/admindashboard/#testimonials-dataview')

        elif 'delete_contact_form' in request.POST:

            contact_id = request.POST.get('contact_id')

            try:
                contactform.objects.get(id=contact_id).delete()
                return redirect('/admindashboard/#enquiries-dataview')
            except:
                return redirect('/admindashboard/#enquiries-dataview')

    return render(
        request,
        'admindashboard.html',
        {
            'homeprojects': homeproject.objects.all(),
            'portfolioprojects': portfolioproject.objects.all(),
            'contactforms': contactform.objects.all(),
            'testimonials': testimonial.objects.all(),
        },
    )
