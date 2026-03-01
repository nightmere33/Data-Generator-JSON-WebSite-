from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import AgencyProfile

class VisaApplicationForm(forms.Form):
    visa = forms.ChoiceField(
        choices=[('', _('Select visa type'))] + [
            ('88', _('Business Multiple')),
            ('87', _('Business Single')),
            ('95', _('Double Transit')),
            ('96', _('Family Reunion')),
            ('94', _('Single Transit')),
            ('125', _('Sport & Cultural Single')),
            ('93', _('Student Single')),
            ('86', _('Tourism Multiple')),
            ('85', _('Tourism Single')),
            ('90', _('Treatment Multiple')),
            ('89', _('Treatment Single')),
            ('92', _('Work Permit Multiple')),
            ('91', _('Work Permit Single')),
        ],
        initial='',
        label=_('Visa Type'),
        widget=forms.Select(attrs={'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    
    nationality = forms.ChoiceField(
        choices=[('', _('Select nationality'))] + [
            ('31', _('Algérie')),
            ('1', _('États-Unis d\'Amérique')),
            ('77', _('Royaume-Uni')),
            ('35', _('Chine')),
            ('71', _('Inde')),
            ('84', _('Italie')),
            ('91', _('Canada')),
            ('9', _('Australie')),
            ('3', _('Allemagne')),
            ('55', _('France')),
            ('80', _('Espagne')),
            ('191', _('Turquie')),
        ],
        initial='',
        label=_('Nationality'),
        widget=forms.Select(attrs={'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    
    contact_address = forms.CharField(
        label=_('Contact Address'),
        widget=forms.Textarea(attrs={
            'class': 'form-textarea rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'rows': 3,
            'placeholder': _('123 Main Street, City, Country')
        })
    )
    
    contact_city = forms.CharField(
        label=_('City'),
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('City')
        })
    )
    
    contact_postcode = forms.CharField(
        label=_('Postal Code'),
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('Postal Code')
        })
    )
    
    departure_date = forms.DateField(
        label=_('Departure Date'),
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        }),
    )
    
    return_date = forms.DateField(
        label=_('Return Date'),
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        }),
    )

    start_date = forms.DateField(
        label=_("Minimum desired date"),
        widget=forms.DateInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'type': 'date'}),
    )
    max_date = forms.DateField(
        label=_("Maximum allowed date"),
        widget=forms.DateInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'type': 'date'}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    phone_local = forms.CharField(
        label=_("Phone"),
        widget=forms.TextInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )

    RELATION_CHOICES = [
        ('', _('Select relation')),
        ('Wife', _('Wife')),
        ('Husband', _('Husband')),
        ('Father', _('Father')),
        ('Mother', _('Mother')),
        ('Child', _('Child')),
        ('Other', _('Other')),
    ]

    relations = forms.ChoiceField(
        label=_('Relation'),
        choices=RELATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        today = date.today()

        start_date = cleaned_data.get('start_date')
        max_date = cleaned_data.get('max_date')
        departure = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')

        if start_date:
            if start_date < today:
                self.add_error('start_date', _("Minimum desired date cannot be in the past."))
            if max_date and start_date > max_date:
                self.add_error('start_date', _("Minimum desired date must not be after maximum allowed date."))
        
        if max_date and max_date < today:
            self.add_error('max_date', _("Maximum allowed date cannot be in the past."))

        if departure:
            if departure < today:
                self.add_error('departure_date', _("Departure date cannot be in the past."))
            if return_date and departure >= return_date:
                self.add_error('return_date', _("Return date must be after departure date."))

        if return_date and return_date < today:
            self.add_error('return_date', _("Return date cannot be in the past."))

        return cleaned_data


class ApplicantForm(forms.Form):
    name = forms.CharField(
        label=_('First Name'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('First Name')
        })
    )
    
    surname = forms.CharField(
        label=_('Last Name'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('Last Name')
        })
    )
    
    gender = forms.ChoiceField(
        label=_('Gender'),
        choices=[('', _('Select gender')), ('M', _('Male')), ('F', _('Female'))],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    birthday = forms.DateField(
        label=_('Date of Birth'),
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    birth_place = forms.CharField(
        label=_('Place of Birth'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('Place of Birth')
        })
    )
    
    marital_status = forms.ChoiceField(
        label=_('Marital Status'),
        choices=[('', _('Select marital status')), ('0', _('Single')), ('1', _('Married'))],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    father_name = forms.CharField(
        label=_("Father's Full Name"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _("Father's Full Name")
        })
    )
    
    mother_name = forms.CharField(
        label=_("Mother's Full Name"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _("Mother's Full Name")
        })
    )
    
    passport_number = forms.CharField(
        label=_('Passport Number'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('Passport Number')
        })
    )
    
    occupation = forms.ChoiceField(
        label=_('Occupation'),
        required=True,
        choices=[('', _('Select occupation'))] + [
            ('Agriculture', _('Agriculture')),
            ('Armed/Security Force', _('Armed/Security Force')),
            ('Artist/Performer', _('Artist/Performer')),
            ('Business', _('Business')),
            ('Caregiver/Babysitter', _('Caregiver/Babysitter')),
            ('Construction', _('Construction')),
            ('Culinary/Cookery', _('Culinary/Cookery')),
            ('Driver/Lorry', _('Driver/Lorry')),
            ('Education/Training', _('Education/Training')),
            ('Engineer', _('Engineer')),
            ('Finance/Banking', _('Finance/Banking')),
            ('Government', _('Government')),
            ('Health/Medical', _('Health/Medical')),
            ('Information Technologies', _('Information Technologies')),
            ('Legal Professional', _('Legal Professional')),
            ('Other', _('Other')),
            ('Press/Media', _('Press/Media')),
            ('Professional Sportsperson', _('Professional Sportsperson')),
            ('Religious Functionary', _('Religious Functionary')),
            ('Researcher/Scientist', _('Researcher/Scientist')),
            ('Retired', _('Retired')),
            ('Seafarer', _('Seafarer')),
            ('Self-Employed', _('Self-Employed')),
            ('Service Sector', _('Service Sector')),
            ('Student/Trainee', _('Student/Trainee')),
            ('Tourism', _('Tourism')),
            ('Unemployed', _('Unemployed')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    passport_issued_by = forms.CharField(
        label=_('Passport Issued By'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': _('Passport Authority')
        })
    )
    
    passport_issue_date = forms.DateField(
        label=_('Issue Date'),
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    passport_expiry = forms.DateField(
        label=_('Expiry Date'),
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    travel_document = forms.ChoiceField(
        label=_('Travel Document Type'),
        choices=[('', _('Select document type'))] + [
            ('10', _('Passeport Ordinaire')),
            ('3', _('Passeport Diplomatique')),
            ('2', _('Carte d\'Identité')),
            ('9', _('Autres')),
            ('11', _('Document de Voyage pour Réfugiés')),
        ],
        initial='',
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )


class AgencyRegistrationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-input rounded-lg w-full'})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-input rounded-lg w-full'})
    )
    confirm_password = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-input rounded-lg w-full'})
    )
    agency_name = forms.CharField(
        label=_('Agency Name'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input rounded-lg w-full'})
    )
    phone = forms.CharField(
        label=_('Phone'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input rounded-lg w-full'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError(_("Passwords do not match"))
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email already registered"))
        return cleaned_data