from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.forms import formset_factory
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import VisaApplicationForm, ApplicantForm, AgencyRegistrationForm
from .models import AgencyProfile, InviteLink, Submission
import json
import uuid
import random
from datetime import datetime, date, timedelta
from django.utils.translation import gettext as _

def index(request):
    return render(request, 'visa_form/index.html')

def convert_dates_for_session(obj):
    """Convert date objects to strings for session storage"""
    if isinstance(obj, dict):
        return {k: convert_dates_for_session(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_for_session(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    else:
        return obj

def js_object_dumps(obj, level=0, indent=2):
    """Convert Python object to JavaScript object literal string with unquoted keys."""
    spaces = ' ' * (level * indent)
    next_spaces = ' ' * ((level + 1) * indent)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            key = str(k)
            val_str = js_object_dumps(v, level + 1, indent)
            items.append(f"{next_spaces}{key}: {val_str}")
        if items:
            return "{{\n{0}\n{1}}}".format(",\n".join(items), spaces)
        else:
            return "{}"
    elif isinstance(obj, list):
        items = [js_object_dumps(item, level + 1, indent) for item in obj]
        if items:
            return "[\n{0}\n{1}]".format(",\n".join([next_spaces + item for item in items]), spaces)
        else:
            return "[]"
    elif isinstance(obj, str):
        escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped}"'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif obj is None:
        return 'null'
    elif isinstance(obj, (int, float)):
        return str(obj)
    else:
        return str(obj)

@login_required
def form_view(request):
    """Main form view (authenticated users only)"""
    profile = request.user.profile

    if request.method == 'POST':
        visa_form = VisaApplicationForm(request.POST)
        ApplicantFormSet = formset_factory(ApplicantForm, extra=0, max_num=5)
        applicant_formset = ApplicantFormSet(request.POST)

        if visa_form.is_valid() and applicant_formset.is_valid():
            # Process relations from text field
            relations_raw = visa_form.cleaned_data.get('relations', '')
            relations_list = [r.strip() for r in relations_raw.split(',') if r.strip()]

            common_data = visa_form.cleaned_data.copy()
            common_data['relations'] = relations_list
            common_data.pop('relations', None)

            # Process applicants
            cleaned_applicants = []
            for form in applicant_formset:
                if form.cleaned_data and form.cleaned_data.get('name'):
                    cleaned_applicants.append(convert_dates_for_session(form.cleaned_data))

            session_data = {
                'common': convert_dates_for_session(common_data),
                'applicants': cleaned_applicants
            }
            request.session['visa_data'] = session_data
            return redirect('preview')
        # If invalid, fall through to re-render with errors
    else:
        # GET request
        if request.GET.get('edit') == '1' and 'visa_data' in request.session:
            # Editing existing data – use raw strings from session
            session_data = request.session['visa_data']
            common_data = session_data['common']
            applicants_data = session_data['applicants']

            visa_form = VisaApplicationForm(initial=common_data)

            # Prepare initial for applicants (keep as strings)
            initial_applicants = []
            for app in applicants_data:
                app_copy = {}
                for key, value in app.items():
                    app_copy[key] = value
                initial_applicants.append(app_copy)

            ApplicantFormSet = formset_factory(ApplicantForm, extra=0, max_num=5)
            applicant_formset = ApplicantFormSet(initial=initial_applicants)
        else:
            # New form
            visa_form = VisaApplicationForm()
            ApplicantFormSet = formset_factory(ApplicantForm, extra=profile.default_applicants, max_num=5)
            applicant_formset = ApplicantFormSet()

    return render(request, 'visa_form/form.html', {
        'visa_form': visa_form,
        'applicant_formset': applicant_formset,
    })

@login_required
def preview_view(request):
    if 'visa_data' not in request.session:
        return redirect('form')
    data = request.session['visa_data']
    return render(request, 'visa_form/preview.html', {
        'data': data,
    })

@login_required
def download_json(request):
    if 'visa_data' not in request.session:
        return redirect('form')

    data = request.session['visa_data']

    # Force slot to empty string
    data['common']['slot'] = ""

    core_fields = ['slot', 'visa', 'nationality', 'contact_address', 'contact_city',
                   'contact_postcode', 'departure_date', 'return_date']
    common_core = {}
    for field in core_fields:
        if field in data['common']:
            common_core[field] = data['common'][field]

    additional_info = {k: v for k, v in data['common'].items() if k not in core_fields}

    # Prepare applicants for Tampermonkey (without passport_number)
    applicants_script = []
    for app in data['applicants']:
        app_copy = app.copy()
        app_copy.pop('passport_number', None)
        applicants_script.append(app_copy)

    output = {
        'COMMON_DATA': common_core,
        'APPLICANT_DATA': data['applicants'],
        'ADDITIONAL_INFO': additional_info,
    }

    applicants_js = js_object_dumps(applicants_script, level=1, indent=2)
    common_core_js = js_object_dumps(common_core, level=1, indent=2)

    tampermonkey_code = f"""// ============================================
// TAMPERMONKEY INTEGRATION CODE
// ============================================
const COMMON_DATA = {common_core_js};

const APPLICANT_DATA = {applicants_js};

// That's it! Your script is ready to auto-fill.
// ============================================

"""

    json_data = json.dumps(output, indent=2, ensure_ascii=False)
    full_content = tampermonkey_code + "\n\n// ============================================\n// RAW JSON DATA (for reference)\n// ============================================\n" + json_data

    # Generate filename
    if data['applicants']:
        first = data['applicants'][0]
        first_name = first.get('name', '').replace(' ', '_')
        surname = first.get('surname', '').replace(' ', '_')
        phone = data['common'].get('phone_local', '').replace(' ', '_')
        filename = f"{first_name}_{surname}_{phone}.txt"
    else:
        filename = f"mosaic_visa_data_{uuid.uuid4().hex[:8]}.txt"

    Submission.objects.create(
        user=request.user,
        data=output,
        filename=filename
    )

    response = HttpResponse(full_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    del request.session['visa_data']
    return response

def register_with_invite(request, token):
    invite = get_object_or_404(InviteLink, token=token, is_used=False)
    if request.method == 'POST':
        form = AgencyRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            AgencyProfile.objects.create(
                user=user,
                agency_name=form.cleaned_data['agency_name'],
                phone=form.cleaned_data['phone']
            )
            invite.is_used = True
            invite.used_by = user
            invite.save()
            login(request, user)
            return redirect('form')
    else:
        form = AgencyRegistrationForm()
    return render(request, 'visa_form/register.html', {'form': form, 'token': token})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('form')
        else:
            return render(request, 'visa_form/login.html', {'error': _('Invalid credentials')})
    return render(request, 'visa_form/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def preview_print(request):
    if 'visa_data' not in request.session:
        return redirect('form')
    data = request.session['visa_data']
    return render(request, 'visa_form/preview_print.html', {'data': data})