from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import (AddDiagnosisView, ChangeDiagnosisStatusView,
                    CreateScheduleView, CustomUserViewSet, DeleteScheduleView,
                    DiagnosisViewSet, DoctorSearchView,
                    DoctorSpecializationUpdateView, LoginView, LogoutView,
                    MainPageView, ProfileView, RegisterChooseView,
                    RegisterView, ScheduleViewSet, UpdateScheduleView,
                    VisitUpdate, VisitViewSet)

API_PREFIX = "api/"
REGISTER_URL = "register/<str:role>/"
LOGIN_URL = "login/"
LOGOUT_URL = "logout/"
UPDATE_SCHEDULE_URL = "schedule/<uuid:pk>/update/"
CREATE_SCHEDULE_URL = "schedule/create/"
DELETE_SCHEDULE_URL = "schedule/<uuid:pk>/delete/"
VISIT_UPDATE_URL = "visit/<uuid:pk>/update/"
ADD_DIAGNOSES_URL = "diagnosis/add/<uuid:patient_id>/"
UPDATE_DIAGNOSES_URL = "diagnosis/update/<uuid:pk>/"
MAIN_PAGE_URL = ""
REGISTER_CHOOSE_URL = "register_choose/"
SEARCH_DOCTORS_URL = "search/"
SPECIALIZATION_UPDATE_URL = "specialization/update/<uuid:pk>/"
PROFILE_URL = "<str:username>/"
API_TOKEN_URL = "api-token-auth/"

router = DefaultRouter()
router.register(r"users", CustomUserViewSet)
router.register(r"visits", VisitViewSet)
router.register(r"diagnoses", DiagnosisViewSet)
router.register(r"schedules", ScheduleViewSet)
api_patterns = [
    path("", include(router.urls)),
]

urlpatterns = [
    path(API_PREFIX, include(api_patterns)),
    path(REGISTER_URL, RegisterView.as_view(), name="register"),
    path(LOGIN_URL, LoginView.as_view(), name="login"),
    path(LOGOUT_URL, LogoutView.as_view(), name="logout"),
    path(API_TOKEN_URL, obtain_auth_token, name="obtain_auth_token"),
    path(UPDATE_SCHEDULE_URL, UpdateScheduleView.as_view(), name="update_schedule"),
    path(CREATE_SCHEDULE_URL, CreateScheduleView.as_view(), name="create_schedule"),
    path(DELETE_SCHEDULE_URL, DeleteScheduleView.as_view(), name="delete_schedule"),
    path(ADD_DIAGNOSES_URL, AddDiagnosisView.as_view(), name='add_diagnosis'),
    path(UPDATE_DIAGNOSES_URL, ChangeDiagnosisStatusView.as_view(), name='update_diagnosis'),
    path(VISIT_UPDATE_URL, VisitUpdate.as_view(), name="visit_update"),
    path(MAIN_PAGE_URL, MainPageView.as_view(), name="main"),
    path(REGISTER_CHOOSE_URL, RegisterChooseView.as_view(), name="register_choose"),
    path(SEARCH_DOCTORS_URL, DoctorSearchView.as_view(), name="search_doctors"),
    path(SPECIALIZATION_UPDATE_URL, DoctorSpecializationUpdateView.as_view(), name="specialization_update"),
    path(PROFILE_URL, ProfileView.as_view(), name="profile"),
]
