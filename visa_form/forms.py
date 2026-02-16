from django import forms
from django.contrib.auth.models import User
from datetime import date, timedelta
from .models import AgencyProfile

class VisaApplicationForm(forms.Form):
    # Common fields
    # slot = forms.ChoiceField(
    #     choices=[('', 'Random / Aléatoire')] + 
    #             [(f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}") 
     #             for h in range(8, 16) for m in [0, 20, 40] 
     #             if not (h == 15 and m > 20)],
    #     required=False,
     #    widget=forms.Select(attrs={'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    # )
    
    visa = forms.ChoiceField(
        choices=[
            ('1', 'Tourisme Simple'),
            ('2', 'Tourisme Multiple'),
            ('3', 'Affaires Simple'),
            ('4', 'Affaires Multiple'),
            ('5', 'Traitement Simple'),
            ('6', 'Traitement Multiple'),
            ('32', 'Étudiant Simple'),
            ('34', 'Accompagnement Simple'),
            ('35', 'Accompagnement Multiple'),
            ('38', 'Permis de Travail Simple'),
            ('39', 'Permis de Travail Multiple'),
            ('40', 'Transit Double'),
            ('77', 'Transit Simple'),
        ],
        initial='1',
        widget=forms.Select(attrs={'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    
    nationality = forms.ChoiceField(
        choices=[
            ('31', 'Algérie'),
            ('1', 'États-Unis d\'Amérique'),
            ('77', 'Royaume-Uni'),
            ('35', 'Chine'),
            ('71', 'Inde'),
            ('84', 'Italie'),
            ('91', 'Canada'),
            ('9', 'Australie'),
            ('3', 'Allemagne'),
            ('55', 'France'),
            ('80', 'Espagne'),
            ('191', 'Turquie'),
        ],
        initial='31',
        widget=forms.Select(attrs={'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    
    contact_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'rows': 3,
            'placeholder': '123 Main Street, City, Country'
        })
    )
    
    contact_city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'City'
        })
    )
    
    contact_postcode = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Postal Code'
        })
    )
    
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        }),
        initial=date.today() + timedelta(days=30)
    )
    
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        }),
        initial=date.today() + timedelta(days=45)
    )

     # New fields
    start_date = forms.DateField(
        label="Minimum desired date",
        widget=forms.DateInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'type': 'date'}),
        initial=date.today() + timedelta(days=30)
    )
    max_date = forms.DateField(
        label="Maximum allowed date",
        widget=forms.DateInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'type': 'date'}),
        initial=date.today() + timedelta(days=45)
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    phone_local = forms.CharField(
        label="Phone",
        widget=forms.TextInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'})
    )
    passports = forms.CharField(
        label="Passport numbers (one per line)",
        widget=forms.Textarea(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'rows': 3, 'placeholder': '314690857\n187204660\n...'}),
        required=False,
        help_text="Enter each passport number on a new line"
    )
    relations = forms.CharField(
        label="Relations (comma separated)",
        widget=forms.TextInput(attrs={'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full', 'placeholder': 'Wife, Father, Mother, Child'}),
        required=False,
        help_text="e.g., Wife, Father, Mother, Child"
    )


class ApplicantForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'First Name'
        })
    )
    
    surname = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Last Name'
        })
    )
    
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    birth_place = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Place of Birth'
        })
    )
    
    marital_status = forms.ChoiceField(
        choices=[('0', 'Single'), ('1', 'Married')],
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    father_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Father\'s Full Name'
        })
    )
    
    mother_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Mother\'s Full Name'
        })
    )
    
    occupation = forms.ChoiceField(
        choices=[
            ('Agriculture', 'Agriculture'),
            ('Armed/Security Force', 'Armed/Security Force'),
            ('Artist/Performer', 'Artist/Performer'),
            ('Business', 'Business'),
            ('Caregiver/Babysitter', 'Caregiver/Babysitter'),
            ('Construction', 'Construction'),
            ('Culinary/Cookery', 'Culinary/Cookery'),
            ('Driver/Lorry', 'Driver/Lorry'),
            ('Education/Training', 'Education/Training'),
            ('Engineer', 'Engineer'),
            ('Finance/Banking', 'Finance/Banking'),
            ('Government', 'Government'),
            ('Health/Medical', 'Health/Medical'),
            ('Information Technologies', 'Information Technologies'),
            ('Legal Professional', 'Legal Professional'),
            ('Other', 'Other'),
            ('Press/Media', 'Press/Media'),
            ('Professional Sportsperson', 'Professional Sportsperson'),
            ('Religious Functionary', 'Religious Functionary'),
            ('Researcher/Scientist', 'Researcher/Scientist'),
            ('Retired', 'Retired'),
            ('Seafarer', 'Seafarer'),
            ('Self-Employed', 'Self-Employed'),
            ('Service Sector', 'Service Sector'),
            ('Student/Trainee', 'Student/Trainee'),
            ('Tourism', 'Tourism'),
            ('Unemployed', 'Unemployed'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )
    
    passport_issued_by = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'placeholder': 'Passport Authority'
        })
    )
    
    passport_issue_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    passport_expiry = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full',
            'type': 'date'
        })
    )
    
    travel_document = forms.ChoiceField(
        choices=[
            ('10', 'Passeport Ordinaire'),
            ('3', 'Passeport Diplomatique'),
            ('2', 'Carte d\'Identité'),
            ('9', 'Autres'),
            ('11', 'Document de Voyage pour Réfugiés'),
        ],
        initial='10',
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 w-full'
        })
    )

    
class AgencyRegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input rounded-lg w-full'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input rounded-lg w-full'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input rounded-lg w-full'}))
    agency_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-input rounded-lg w-full'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input rounded-lg w-full'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return cleaned_data