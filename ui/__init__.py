"""UI package for SasthoSetu desktop interface."""

from ui.app import SasthoSetuApp
from ui.auth_view import AuthSuccessView, LoginView, RegisterView
from ui.dashboard_view import ClinicianDashboardView, PatientDetailDialog
from ui.patient_home_view import PatientHomeView
from ui.patient_info_view import PatientInfoView, SymptomPlaceholderView
from ui.role_view import (
    ClinicianPlaceholderView,
    PatientPlaceholderView,
    RoleSelectionView,
)
from ui.symptom_intake_view import SymptomIntakeView, TriagePlaceholderView
from ui.triage_result_view import TriageResultView

__all__ = [
    "SasthoSetuApp",
    "LoginView",
    "RegisterView",
    "AuthSuccessView",
    "RoleSelectionView",
    "PatientPlaceholderView",
    "PatientHomeView",
    "PatientInfoView",
    "SymptomPlaceholderView",
    "SymptomIntakeView",
    "TriagePlaceholderView",
    "TriageResultView",
    "ClinicianPlaceholderView",
    "ClinicianDashboardView",
    "PatientDetailDialog",
]
