# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    # Basic doctor profile
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    specialty = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialty})"


class Patient(models.Model):
    # Owner is the user who created the patient entry
    owner = models.ForeignKey(User, related_name="patients", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(Patient, related_name="mappings", on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name="mappings", on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "doctor")  # prevent duplicate mapping

    def __str__(self):
        return f"{self.patient} -> {self.doctor}"
