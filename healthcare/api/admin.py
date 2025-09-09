# api/admin.py
from django.contrib import admin
from .models import Doctor, Patient, PatientDoctorMapping

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(PatientDoctorMapping)
