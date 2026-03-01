from django import template
from django.utils.translation import gettext as _

register = template.Library()

# Mapping dictionaries (keys are the stored values, values are translated labels)

VISA_MAP = {
    '88': _('Business Multiple'),
    '87': _('Business Single'),
    '95': _('Double Transit'),
    '96': _('Family Reunion'),
    '94': _('Single Transit'),
    '125': _('Sport & Cultural Single'),
    '93': _('Student Single'),
    '86': _('Tourism Multiple'),
    '85': _('Tourism Single'),
    '90': _('Treatment Multiple'),
    '89': _('Treatment Single'),
    '92': _('Work Permit Multiple'),
    '91': _('Work Permit Single'),
}

NATIONALITY_MAP = {
    '31': _('Algérie'),
    '1': _('États-Unis d\'Amérique'),
    '77': _('Royaume-Uni'),
    '35': _('Chine'),
    '71': _('Inde'),
    '84': _('Italie'),
    '91': _('Canada'),
    '9': _('Australie'),
    '3': _('Allemagne'),
    '55': _('France'),
    '80': _('Espagne'),
    '191': _('Turquie'),
}

MARITAL_STATUS_MAP = {
    '0': _('Single'),
    '1': _('Married'),
}

GENDER_MAP = {
    'M': _('Male'),
    'F': _('Female'),
}

TRAVEL_DOCUMENT_MAP = {
    '3': _('Passeport Diplomatique'),
    '2': _('Carte d\'Identité'),
    '10': _('Passeport Ordinaire'),
    '9': _('Autres'),
    '11': _('Document de Voyage pour Réfugiés'),
}

OCCUPATION_MAP = {
    'Agriculture': _('Agriculture'),
    'Armed/Security Force': _('Armed/Security Force'),
    'Artist/Performer': _('Artist/Performer'),
    'Business': _('Business'),
    'Caregiver/Babysitter': _('Caregiver/Babysitter'),
    'Construction': _('Construction'),
    'Culinary/Cookery': _('Culinary/Cookery'),
    'Driver/Lorry': _('Driver/Lorry'),
    'Education/Training': _('Education/Training'),
    'Engineer': _('Engineer'),
    'Finance/Banking': _('Finance/Banking'),
    'Government': _('Government'),
    'Health/Medical': _('Health/Medical'),
    'Information Technologies': _('Information Technologies'),
    'Legal Professional': _('Legal Professional'),
    'Other': _('Other'),
    'Press/Media': _('Press/Media'),
    'Professional Sportsperson': _('Professional Sportsperson'),
    'Religious Functionary': _('Religious Functionary'),
    'Researcher/Scientist': _('Researcher/Scientist'),
    'Retired': _('Retired'),
    'Seafarer': _('Seafarer'),
    'Self-Employed': _('Self-Employed'),
    'Service Sector': _('Service Sector'),
    'Student/Trainee': _('Student/Trainee'),
    'Tourism': _('Tourism'),
    'Unemployed': _('Unemployed'),
}

RELATION_MAP = {
    'Wife': _('Wife'),
    'Husband': _('Husband'),
    'Father': _('Father'),
    'Mother': _('Mother'),
    'Child': _('Child'),
    'Other': _('Other'),
}

@register.filter
def visa_label(value):
    return VISA_MAP.get(value, value)

@register.filter
def nationality_label(value):
    return NATIONALITY_MAP.get(value, value)

@register.filter
def marital_status_label(value):
    return MARITAL_STATUS_MAP.get(value, value)

@register.filter
def gender_label(value):
    return GENDER_MAP.get(value, value)

@register.filter
def travel_document_label(value):
    return TRAVEL_DOCUMENT_MAP.get(value, value)

@register.filter
def occupation_label(value):
    return OCCUPATION_MAP.get(value, value)

@register.filter
def relation_label(value):
    return RELATION_MAP.get(value, value)