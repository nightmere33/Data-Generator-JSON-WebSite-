from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import formset_factory
from .forms import VisaApplicationForm, ApplicantForm
import json
import uuid
from datetime import datetime, date

def index(request):
    """Home page"""
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

def form_view(request):
    """Main form view"""
    ApplicantFormSet = formset_factory(ApplicantForm, extra=1, max_num=5)
    
    if request.method == 'POST':
        visa_form = VisaApplicationForm(request.POST)
        applicant_formset = ApplicantFormSet(request.POST)
        
        if visa_form.is_valid() and applicant_formset.is_valid():
            # Save data to session (converting dates to strings)
            cleaned_applicants = []
            for form in applicant_formset:
                if form.cleaned_data and form.cleaned_data.get('name'):
                    cleaned_applicants.append(convert_dates_for_session(form.cleaned_data))
            
            session_data = {
                'common': convert_dates_for_session(visa_form.cleaned_data),
                'applicants': cleaned_applicants
            }
            request.session['visa_data'] = session_data
            return redirect('preview')
    else:
        visa_form = VisaApplicationForm()
        applicant_formset = ApplicantFormSet()
    
    return render(request, 'visa_form/form.html', {
        'visa_form': visa_form,
        'applicant_formset': applicant_formset,
    })

def preview_view(request):
    """Preview page"""
    if 'visa_data' not in request.session:
        return redirect('form_view')
    
    data = request.session['visa_data']
    
    # Create JSON for display
    json_data = json.dumps({
        'APPLICANT_DATA': data['applicants'],
        'COMMON_DATA': data['common'],
    }, indent=2, ensure_ascii=False)
    
    return render(request, 'visa_form/preview.html', {
        'data': data,
        'json_data': json_data,
    })

def download_json(request):
        """Download JSON file with Tampermonkey integration code"""
        if 'visa_data' not in request.session:
            return redirect('form_view')
        
        data = request.session['visa_data']
        
        # Create JSON structure
        output = {
            'APPLICANT_DATA': data['applicants'],
            'COMMON_DATA': data['common'],
        }
        
        # Create Tampermonkey integration code
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
        
        # Create JSON data
        json_data = json.dumps(output, indent=2, ensure_ascii=False)
        
        # Combine both
        full_content = tampermonkey_code + "\n\n// ============================================\n// RAW JSON DATA (for reference)\n// ============================================\n" + json_data
        
        # Create response
        filename = f"mosaic_visa_data_{uuid.uuid4().hex[:8]}.txt"
        
        response = HttpResponse(full_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clear session
        if 'visa_data' in request.session:
            del request.session['visa_data']
        
        return response

def success_view(request):
    """Success page (optional)"""
    return render(request, 'visa_form/success.html')