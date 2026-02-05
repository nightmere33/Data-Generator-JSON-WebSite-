from django.db import models

class VisaApplication(models.Model):
    # Common Data
    slot = models.CharField(max_length=10, blank=True, help_text="Leave empty for random selection")
    VISA_TYPES = [
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
    ]
    visa = models.CharField(max_length=2, choices=VISA_TYPES, default='1')
    
    NATIONALITIES = [
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
    ]
    nationality = models.CharField(max_length=3, choices=NATIONALITIES, default='31')
    
    contact_address = models.TextField()
    contact_city = models.CharField(max_length=100)
    contact_postcode = models.CharField(max_length=10)
    departure_date = models.DateField()
    return_date = models.DateField()
    
    # Settings
    auto_click_next = models.BooleanField(default=False)
    auto_click_delay = models.IntegerField(default=2000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"Application {self.reference_id}"

class Applicant(models.Model):
    visa_application = models.ForeignKey(VisaApplication, on_delete=models.CASCADE, related_name='applicants')
    
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    MARITAL_STATUS_CHOICES = [('0', 'Single'), ('1', 'Married')]
    
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField()
    birth_place = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    
    OCCUPATION_CHOICES = [
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
    ]
    occupation = models.CharField(max_length=50, choices=OCCUPATION_CHOICES)
    
    passport_issued_by = models.CharField(max_length=100)
    passport_issue_date = models.DateField()
    passport_expiry = models.DateField()
    
    TRAVEL_DOCUMENT_CHOICES = [
        ('3', 'Passeport Diplomatique'),
        ('2', 'Carte d\'Identité'),
        ('10', 'Passeport Ordinaire'),
        ('9', 'Autres'),
        ('11', 'Document de Voyage pour Réfugiés'),
    ]
    travel_document = models.CharField(max_length=2, choices=TRAVEL_DOCUMENT_CHOICES, default='10')
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} {self.surname}"