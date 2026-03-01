from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import AgencyProfile, InviteLink, Submission
import json
import random
import re
import uuid
from django.utils.timezone import now
import zipfile
from io import BytesIO
from datetime import datetime

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
    list_display = ('token_short', 'created_at', 'is_used', 'used_by')
    list_filter = ('is_used', 'created_at')
    search_fields = ('token', 'used_by__email')
    readonly_fields = ('token', 'created_at')

    def token_short(self, obj):
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'filename', 'data_summary', 'download_link')
    list_filter = ('user', 'created_at')
    search_fields = ('filename', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('user', 'filename', 'created_at', 'pretty_json')
    fields = ('user', 'filename', 'created_at', 'pretty_json')
    actions = ['download_selected_submissions']

    def data_summary(self, obj):
        if not obj.data:
            return "-"
        applicants = obj.data.get('APPLICANT_DATA', [])
        common = obj.data.get('COMMON_DATA', {})
        visa = common.get('visa', '?')
        return f"{len(applicants)} applicant(s) | Visa: {visa}"
    data_summary.short_description = 'Summary'

    def pretty_json(self, obj):
        """Return a syntax-highlighted JSON display with a download button."""
        from django.utils.safestring import mark_safe
        data = obj.data
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        formatted = formatted.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Syntax highlighting
        formatted = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*")(\s*:)',
                           r'<span class="json-key">\1</span>\2', formatted)
        formatted = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*")(?!\s*:)',
                           r'<span class="json-string">\1</span>', formatted)
        formatted = re.sub(r'\b(-?\d+(\.\d+)?([eE][+-]?\d+)?)\b',
                           r'<span class="json-number">\1</span>', formatted)
        formatted = re.sub(r'\b(true|false)\b',
                           r'<span class="json-boolean">\1</span>', formatted)
        formatted = re.sub(r'\bnull\b',
                           r'<span class="json-null">null</span>', formatted)

        download_url = f"/admin/visa_form/submission/{obj.id}/download/"

        html = f"""
        <div style="background: #1a1a1a; border-radius: 8px; padding: 1rem; position: relative; margin-top: 1rem;">
            <div style="position: absolute; top: 12px; right: 12px; display: flex; gap: 8px;">
                <a href="{download_url}"
                   style="background: #10b981; color: white; padding: 6px 12px; border-radius: 6px;
                          text-decoration: none; font-size: 13px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">
                    <i class="fas fa-download" style="font-size: 12px;"></i> Download File
                </a>
            </div>
            <pre style="color: #e2e8f0; background: transparent; padding: 0; margin: 0;
                        font-family: 'Courier New', Courier, monospace; font-size: 13px;
                        line-height: 1.5; overflow-x: auto; max-height: 500px;">{formatted}</pre>
        </div>
        <style>
            .json-key {{ color: #63b3ed; }}
            .json-string {{ color: #68d391; }}
            .json-number {{ color: #f6ad55; }}
            .json-boolean {{ color: #f687b3; }}
            .json-null {{ color: #cbd5e0; }}
        </style>
        """
        return mark_safe(html)
    pretty_json.short_description = 'Data (formatted)'

    def download_link(self, obj):
        return format_html('<a class="button" href="{}" target="_blank">Download</a>',
                           f"/admin/visa_form/submission/{obj.id}/download/")
    download_link.short_description = 'Download'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:submission_id>/download/', self.admin_site.admin_view(self.download_single),
                 name='submission-download'),
        ]
        return custom_urls + urls

    def download_single(self, request, submission_id):
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(Submission, pk=submission_id)
        data = obj.data

        if 'COMMON_DATA' in data:
            data['COMMON_DATA']['slot'] = ""

        full_applicants = data.get('APPLICANT_DATA', [])
        applicants_script = []
        for app in full_applicants:
            app_copy = app.copy()
            app_copy.pop('passport_number', None)
            applicants_script.append(app_copy)

        common_core = data.get('COMMON_DATA', {})
        additional = data.get('ADDITIONAL_INFO', {})

        num_applicants = len(full_applicants)
        passports = [app.get('passport_number', '') for app in full_applicants]
        # Pad to 5 with placeholders "2emepersonne", "3emepersonne", ...
        for i in range(len(passports), 5):
            passports.append(f"{i+1}emepersonne")

        email = additional.get('email', '')
        phone = additional.get('phone_local', '')
        relation = additional.get('relations', '')
        relations_array = [relation, "Wife", "Father", "Mother", "Child"]

        start_date = additional.get('start_date', '')
        max_date = additional.get('max_date', '')
        start_date_dmy = format_date_dmy(start_date)
        max_date_dmy = format_date_dmy(max_date)

        # Part 1: Tampermonkey
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

        # Part 2: Second script
        second_script = f"""// ============================================
// SCRIPT 2 CONFIGURATION
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

        response = HttpResponse(full_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{obj.filename}"'
        return response

    def download_selected_submissions(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            return self.download_single(request, obj.id)
        else:
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for obj in queryset:
                    data = obj.data
                    if 'COMMON_DATA' in data:
                        data['COMMON_DATA']['slot'] = ""

                    full_applicants = data.get('APPLICANT_DATA', [])
                    applicants_script = []
                    for app in full_applicants:
                        app_copy = app.copy()
                        app_copy.pop('passport_number', None)
                        applicants_script.append(app_copy)

                    common_core = data.get('COMMON_DATA', {})
                    additional = data.get('ADDITIONAL_INFO', {})

                    num_applicants = len(full_applicants)
                    passports = [app.get('passport_number', '') for app in full_applicants]
                    for i in range(len(passports), 5):
                        passports.append(f"{i+1}emepersonne")

                    email = additional.get('email', '')
                    phone = additional.get('phone_local', '')
                    relation = additional.get('relations', '')
                    relations_array = [relation, "Wife", "Father", "Mother", "Child"]

                    start_date = additional.get('start_date', '')
                    max_date = additional.get('max_date', '')
                    start_date_dmy = format_date_dmy(start_date)
                    max_date_dmy = format_date_dmy(max_date)

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

                    second_script = f"""// ============================================
// SCRIPT 2 CONFIGURATION
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
                    zip_file.writestr(obj.filename, full_content)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="submissions_{now().strftime("%Y%m%d_%H%M%S")}.zip"'
            return response
    download_selected_submissions.short_description = "Download selected submissions"