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




from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO


#from django.template.loader import render_to_string
#from xhtml2pdf import pisa
#from io import BytesIO

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

def format_date_dmy(date_str):
    """Convert YYYY-MM-DD to DD.MM.YYYY"""
    if date_str:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            return d.strftime('%d.%m.%Y')
        except:
            return date_str
    return ""

@login_required
def form_view(request):
    """Main form view (authenticated users only)"""
    profile = request.user.profile

    if request.method == 'POST':
        visa_form = VisaApplicationForm(request.POST)
        ApplicantFormSet = formset_factory(ApplicantForm, extra=0, max_num=5)
        applicant_formset = ApplicantFormSet(request.POST)

        if visa_form.is_valid() and applicant_formset.is_valid():
            # Count applicants that have a name (i.e., are filled)
            cleaned_applicants = []
            for form in applicant_formset:
                if form.cleaned_data and form.cleaned_data.get('name'):
                    cleaned_applicants.append(convert_dates_for_session(form.cleaned_data))

            # Validate relation for each applicant beyond first
            num_applicants = len(cleaned_applicants)
            has_relation_error = False
            for idx, app in enumerate(cleaned_applicants):
                if idx == 0:
                    # First applicant: relation must be empty
                    if app.get('relation'):
                        applicant_formset.forms[idx].add_error('relation', _("Le premier demandeur ne doit pas avoir de relation."))
                        has_relation_error = True
                else:
                    # Subsequent applicants: relation must be selected
                    if not app.get('relation'):
                        applicant_formset.forms[idx].add_error('relation', _("Veuillez sélectionner une relation pour ce demandeur."))
                        has_relation_error = True

            if not has_relation_error:
                common_data = visa_form.cleaned_data.copy()
                session_data = {
                    'common': convert_dates_for_session(common_data),
                    'applicants': cleaned_applicants
                }
                request.session['visa_data'] = session_data
                return redirect('preview')
        # If invalid, re-render with errors
    else:
        # GET request
        if request.GET.get('edit') == '1' and 'visa_data' in request.session:
            session_data = request.session['visa_data']
            common_data = session_data['common']
            applicants_data = session_data['applicants']

            visa_form = VisaApplicationForm(initial=common_data)

            initial_applicants = []
            for app in applicants_data:
                app_copy = {}
                for key, value in app.items():
                    app_copy[key] = value
                initial_applicants.append(app_copy)

            ApplicantFormSet = formset_factory(ApplicantForm, extra=0, max_num=5)
            applicant_formset = ApplicantFormSet(initial=initial_applicants)
        else:
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

    # Prepare applicants for Tampermonkey (without passport_number and without relation)
    applicants_script = []
    for app in data['applicants']:
        app_copy = app.copy()
        app_copy.pop('passport_number', None)
        app_copy.pop('relation', None)  # remove relation from individual objects
        applicants_script.append(app_copy)

    # Prepare data for second script
    num_applicants = len(data['applicants'])
    passports = [app.get('passport_number', '') for app in data['applicants']]
    # Pad to 5 with placeholders "2emepersonne", "3emepersonne", ...
    for i in range(len(passports), 5):
        passports.append(f"{i+1}emepersonne")

    # Build relations array: first element empty, then relation for each applicant beyond first
    relations_array = [""]  # first applicant always empty
    for app in data['applicants'][1:]:  # skip first
        relations_array.append(app.get('relation', ''))
    # Pad to 5 with empty strings (or placeholders if needed)
    while len(relations_array) < 5:
        relations_array.append("")

    email = data['common'].get('email', '')
    phone = data['common'].get('phone_local', '')

    # Format dates to DD.MM.YYYY
    start_date_dmy = format_date_dmy(data['common'].get('start_date', ''))
    max_date_dmy = format_date_dmy(data['common'].get('max_date', ''))

    # Part 1: Tampermonkey integration
    applicants_js = js_object_dumps(applicants_script, level=1, indent=2)
    common_core_js = js_object_dumps(common_core, level=1, indent=2)
    tampermonkey_code = f"""// ============================================

// ============================================
const COMMON_DATA = {common_core_js};

const APPLICANT_DATA = {applicants_js};



"""

    # Part 2: Second script configuration
    second_script = f"""// ============================================
// ============================================
const START_DATE_FORMATTED = "{start_date_dmy}"; // Date minimale souhaitée (DD.MM.YYYY)
const MAX_DATE_FORMATTED   = "{max_date_dmy}"; // Date maximale autorisée

const CONFIG = {{
    defaultApplicants: {num_applicants},
    passports: {json.dumps(passports, indent=2)},
    email: "{email}",
    phoneLocal: "{phone}",
    relations: {json.dumps(relations_array, indent=2)}
}};

"""

    full_content = tampermonkey_code + "\n" + second_script

    # Generate filename (as before)
    if data['applicants']:
        first = data['applicants'][0]
        first_name = first.get('name', '').replace(' ', '_')
        surname = first.get('surname', '').replace(' ', '_')
        phone = data['common'].get('phone_local', '').replace(' ', '_')
        filename = f"{first_name}_{surname}_{phone}.txt"
    else:
        filename = f"mosaic_visa_data_{uuid.uuid4().hex[:8]}.txt"

    # Save submission
    output = {
        'COMMON_DATA': common_core,
        'APPLICANT_DATA': data['applicants'],
        'ADDITIONAL_INFO': additional_info,
    }
    Submission.objects.create(
        user=request.user,
        data=output,
        filename=filename
    )

    response = HttpResponse(full_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
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


@login_required
def preview_pdf(request):
    if 'visa_data' not in request.session:
        return redirect('form')
    data = request.session['visa_data']

    # Mapping dictionaries for code → label (same as in visa_filters.py)
    VISA_MAP = {
        '88': 'Business Multiple', '87': 'Business Single', '95': 'Double Transit',
        '96': 'Family Reunion', '94': 'Single Transit', '125': 'Sport & Cultural Single',
        '93': 'Student Single', '86': 'Tourism Multiple', '85': 'Tourism Single',
        '90': 'Treatment Multiple', '89': 'Treatment Single', '92': 'Work Permit Multiple',
        '91': 'Work Permit Single',
    }
    NATIONALITY_MAP = {
        '31': 'Algérie', '1': 'États-Unis d\'Amérique', '77': 'Royaume-Uni',
        '35': 'Chine', '71': 'Inde', '84': 'Italie', '91': 'Canada', '9': 'Australie',
        '3': 'Allemagne', '55': 'France', '80': 'Espagne', '191': 'Turquie',
    }
    GENDER_MAP = {'M': 'Male', 'F': 'Female'}
    MARITAL_STATUS_MAP = {'0': 'Single', '1': 'Married'}
    OCCUPATION_MAP = {
        'Agriculture': 'Agriculture', 'Armed/Security Force': 'Armed/Security Force',
        'Artist/Performer': 'Artist/Performer', 'Business': 'Business',
        'Caregiver/Babysitter': 'Caregiver/Babysitter', 'Construction': 'Construction',
        'Culinary/Cookery': 'Culinary/Cookery', 'Driver/Lorry': 'Driver/Lorry',
        'Education/Training': 'Education/Training', 'Engineer': 'Engineer',
        'Finance/Banking': 'Finance/Banking', 'Government': 'Government',
        'Health/Medical': 'Health/Medical', 'Information Technologies': 'Information Technologies',
        'Legal Professional': 'Legal Professional', 'Other': 'Other',
        'Press/Media': 'Press/Media', 'Professional Sportsperson': 'Professional Sportsperson',
        'Religious Functionary': 'Religious Functionary', 'Researcher/Scientist': 'Researcher/Scientist',
        'Retired': 'Retired', 'Seafarer': 'Seafarer', 'Self-Employed': 'Self-Employed',
        'Service Sector': 'Service Sector', 'Student/Trainee': 'Student/Trainee',
        'Tourism': 'Tourism', 'Unemployed': 'Unemployed',
    }
    TRAVEL_DOCUMENT_MAP = {
        '10': 'Passeport Ordinaire', '3': 'Passeport Diplomatique',
        '2': 'Carte d\'Identité', '9': 'Autres', '11': 'Document de Voyage pour Réfugiés',
    }
    RELATION_MAP = {
        'Wife': 'Wife', 'Husband': 'Husband', 'Father': 'Father',
        'Mother': 'Mother', 'Child': 'Child', 'Other': 'Other',
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading2']
    style_title = styles['Title']

    story = []

    # Title
    story.append(Paragraph(_("Visa Application Summary"), style_title))
    story.append(Spacer(1, 0.5*cm))

    # Common Information (sans relation)
    story.append(Paragraph(_("Common Information"), style_heading))
    story.append(Spacer(1, 0.3*cm))

    common = data['common']
    common_data = [
        [_("Min Desired Date"), common.get('start_date', '')],
        [_("Max Allowed Date"), common.get('max_date', '')],
        [_("Email"), common.get('email', '')],
        [_("Phone"), common.get('phone_local', '')],
        [_("Visa Type"), VISA_MAP.get(common.get('visa'), common.get('visa'))],
        [_("Nationality"), NATIONALITY_MAP.get(common.get('nationality'), common.get('nationality'))],
        [_("Address"), common.get('contact_address', '')],
        [_("City"), common.get('contact_city', '')],
        [_("Postal Code"), common.get('contact_postcode', '')],
        [_("Departure"), common.get('departure_date', '')],
        [_("Return"), common.get('return_date', '')],
    ]

    common_table = Table(common_data, colWidths=[5*cm, 10*cm])
    common_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(common_table)
    story.append(Spacer(1, 0.5*cm))

    # Applicants
    for idx, applicant in enumerate(data['applicants'], start=1):
        applicant_block = []
        applicant_block.append(Paragraph(_("Applicant {}").format(idx), style_heading))
        applicant_block.append(Spacer(1, 0.3*cm))

        app_data = [
            [_("First Name"), applicant.get('name', '')],
            [_("Last Name"), applicant.get('surname', '')],
            [_("Gender"), GENDER_MAP.get(applicant.get('gender'), applicant.get('gender'))],
            [_("Marital Status"), MARITAL_STATUS_MAP.get(applicant.get('marital_status'), applicant.get('marital_status'))],
            [_("Date of Birth"), applicant.get('birthday', '')],
            [_("Place of Birth"), applicant.get('birth_place', '')],
            [_("Passport Number"), applicant.get('passport_number', '')],
            [_("Occupation"), OCCUPATION_MAP.get(applicant.get('occupation'), applicant.get('occupation'))],
            [_("Relation"), RELATION_MAP.get(applicant.get('relation'), applicant.get('relation', ''))],
            [_("Father's Name"), applicant.get('father_name', '')],
            [_("Mother's Name"), applicant.get('mother_name', '')],
            [_("Travel Document"), TRAVEL_DOCUMENT_MAP.get(applicant.get('travel_document'), applicant.get('travel_document'))],
            [_("Issued By"), applicant.get('passport_issued_by', '')],
            [_("Issue Date"), applicant.get('passport_issue_date', '')],
            [_("Expiry Date"), applicant.get('passport_expiry', '')],
        ]

        app_table = Table(app_data, colWidths=[5*cm, 10*cm])
        app_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))

        applicant_block.append(app_table)
        applicant_block.append(Spacer(1, 0.5*cm))
        story.append(KeepTogether(applicant_block))

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    # Generate filename
    if data['applicants']:
        first = data['applicants'][0]
        first_name = first.get('name', 'applicant').replace(' ', '_')
        last_name = first.get('surname', 'unknown').replace(' ', '_')
        filename = f"{first_name}_{last_name}.pdf"
    else:
        filename = "visa_summary.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response