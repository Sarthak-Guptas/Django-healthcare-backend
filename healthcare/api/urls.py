
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, DoctorViewSet, RegisterView, mapping_list_create, mappings_by_patient, mapping_delete
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"doctors", DoctorViewSet, basename="doctors")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("", include(router.urls)),

    # mappings
    path("mappings/", mapping_list_create, name="mappings_list_create"),
    path("mappings/<int:patient_id>/", mappings_by_patient, name="mappings_by_patient"),
    path("mappings/delete/<int:id>/", mapping_delete, name="mappings_delete"),
]
