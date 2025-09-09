
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (RegisterSerializer, DoctorSerializer,
                          PatientSerializer, MappingSerializer)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound, PermissionDenied

# Register view (returns tokens + user data)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            "user": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


# Patients: ONLY owner can modify their patients
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_queryset(self):
        # Return only patients created by authenticated user
        return Patient.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        # owner-only access
        if obj.owner != request.user:
            raise PermissionDenied("You do not have permission to access this patient.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied("You do not have permission to update this patient.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied("You do not have permission to delete this patient.")
        return super().destroy(request, *args, **kwargs)


# Doctors: list is public; but create/update/delete require auth
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by("-created_at")
    serializer_class = DoctorSerializer

    def get_permissions(self):
        # GET list and retrieve -> allow any
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        # create/update/delete require auth
        return [IsAuthenticated()]


# Mappings: Assign a doctor to patient, list mappings, get by patient id, delete mapping
from rest_framework.decorators import api_view, permission_classes

@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def mapping_list_create(request):
    # POST: create mapping (authenticated)
    if request.method == "POST":
        serializer = MappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Ensure the patient belongs to the current user (only owner can assign)
        patient = serializer.validated_data["patient"]
        if patient.owner != request.user:
            return Response({"detail":"You can only assign doctors to patients you created."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save(assigned_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET: list all mappings for this user (mappings where patient.owner == user)
    mappings = PatientDoctorMapping.objects.filter(patient__owner=request.user).select_related("patient","doctor")
    serializer = MappingSerializer(mappings, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mappings_by_patient(request, patient_id):
    # Return all doctors assigned to a specific patient (only if owner)
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        raise NotFound("Patient not found.")
    if patient.owner != request.user:
        raise PermissionDenied("You do not have permission to view mappings for this patient.")
    mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor")
    serializer = MappingSerializer(mappings, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def mapping_delete(request, id):
    try:
        m = PatientDoctorMapping.objects.get(id=id)
    except PatientDoctorMapping.DoesNotExist:
        raise NotFound("Mapping not found.")
    # allow deletion only if assigned_by == request.user or patient.owner == request.user
    if m.assigned_by != request.user and m.patient.owner != request.user:
        raise PermissionDenied("You do not have permission to delete this mapping.")
    m.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
