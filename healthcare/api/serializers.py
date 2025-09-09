# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, Doctor, PatientDoctorMapping
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

# USER REGISTER serializer
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("name", "username", "email", "password")
        extra_kwargs = {
            "username": {"required": True},
        }

    def create(self, validated_data):
        name = validated_data.pop("name")
        username = validated_data["username"]
        user = User.objects.create_user(**validated_data)
        # split name into first/last
        parts = name.split(" ", 1)
        user.first_name = parts[0]
        if len(parts) > 1:
            user.last_name = parts[1]
        user.save()
        return user


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class PatientSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # shows username

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("id", "owner", "created_at")


class MappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    assigned_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = "__all__"
        read_only_fields = ("id", "assigned_by", "assigned_at")

    def validate(self, data):
        # Ensure that patient exists and belongs to someone? We only ensure patient exists.
        # You can add more business rules here.
        if data["patient"].owner is None:
            raise serializers.ValidationError("Patient owner not found.")
        return data
