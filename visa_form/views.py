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

@login_required
def form_view(request):
    """Main form view (authenticated users only)"""
    profile = request.user.profile
    
    # Pre‑fill common fields from profile
    initial_common = {
        'email': request.user.email,
        'phone_local': profile.phone,
        'start_date': profile.default_start_date or (date.today() + timedelta(days=30)),
        'max_date': profile.default_end_date or (date.today() + timedelta(days=45)),
        'passports': '\n'.join(profile.passports) if profile.passports else '',
        'relations': ', '.join(profile.relations) if profile.relations else '',
        # other fields remain as default
    }
    
    ApplicantFormSet = formset_factory(ApplicantForm, extra=profile.default_applicants, max_num=5)
    
    if request.method == 'POST':
        visa_form = VisaApplicationForm(request.POST, initial=initial_common)
        applicant_formset = ApplicantFormSet(request.POST)
        
        if visa_form.is_valid() and applicant_formset.is_valid():
            # Process passports and relations from text fields
            passports_raw = visa_form.cleaned_data.get('passports', '')
            passports_list = [p.strip() for p in passports_raw.split('\n') if p.strip()]
            relations_raw = visa_form.cleaned_data.get('relations', '')
            relations_list = [r.strip() for r in relations_raw.split(',') if r.strip()]
            
            common_data = visa_form.cleaned_data.copy()
            common_data['passports'] = passports_list
            common_data['relations'] = relations_list
            # Remove raw text fields (if needed)
            common_data.pop('passports', None)   # keep only the list version
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
    else:
        visa_form = VisaApplicationForm(initial=initial_common)
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
    json_data = json.dumps({
        'APPLICANT_DATA': data['applicants'],
        'COMMON_DATA': data['common'],
    }, indent=2, ensure_ascii=False)
    return render(request, 'visa_form/preview.html', {
        'data': data,
        'json_data': json_data,
    })

@login_required
def download_json(request):
    if 'visa_data' not in request.session:
        return redirect('form')
    
    data = request.session['visa_data']
    
    # Generate random slot
    slots = ['08:00','08:20','08:40','09:00','09:20','09:40','10:00','10:20','10:40',
             '11:00','11:20','11:40','12:00','12:20','12:40','13:00','13:20','13:40',
             '14:00','14:20','14:40','15:00','15:20']
    random_slot = random.choice(slots)
    data['common']['slot'] = random_slot   # add slot to common data
    
    output = {
        'APPLICANT_DATA': data['applicants'],
        'COMMON_DATA': data['common'],
    }
    
    # Tampermonkey integration code
    tampermonkey_code = f"""// ============================================
// TAMPERMONKEY INTEGRATION CODE
// ============================================
// 1. Replace the APPLICANT_DATA array:
const APPLICANT_DATA = {json.dumps(data['applicants'], indent=2)};

// 2. Replace the COMMON_DATA object:
const COMMON_DATA = {json.dumps(data['common'], indent=2)};

// That's it! Your script is ready to auto-fill.
// ============================================

"""
    
    json_data = json.dumps(output, indent=2, ensure_ascii=False)
    full_content = tampermonkey_code + "\n\n// ============================================\n// RAW JSON DATA (for reference)\n// ============================================\n" + json_data
    
    filename = f"mosaic_visa_data_{uuid.uuid4().hex[:8]}.txt"
    
    # Save submission for admin monitoring
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