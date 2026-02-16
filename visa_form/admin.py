from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import AgencyProfile, InviteLink, Submission

class AgencyProfileInline(admin.StackedInline):
    model = AgencyProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [AgencyProfileInline]
    list_display = ('email', 'username', 'is_staff', 'get_agency_name')
    def get_agency_name(self, obj):
        return obj.profile.agency_name if hasattr(obj, 'profile') else ''
    get_agency_name.short_description = 'Agency'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(InviteLink)
class InviteLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'is_used', 'used_by')
    readonly_fields = ('token', 'created_at')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'filename')
    list_filter = ('user',)