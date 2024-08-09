"""Views for the clinic app."""
import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import (HttpRequest, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView,
                                  View)
from rest_framework import viewsets

from .config.levels import ROLES, UserLevel
from .config.models import VisitStatus
from .config.strings import (STR_EMAIL, STR_FIRST_NAME, STR_FORM, STR_ID,
                             STR_LAST_NAME, STR_LOGIN, STR_NO_ACCESS,
                             STR_PROFILE, STR_SCHEDULES, STR_SPECIALIZATION)
from .forms import (DiagnosisAddForm, DiagnosisStatusForm, DoctorSearchForm,
                    RegisterUserForm, ScheduleViewForm, VisitCreationForm,
                    VisitUpdateForm)
from .models import (CustomUser, Diagnosis, DoctorSpecialization, Schedule,
                     Visit)
from .permissions import IsAdminUser
from .serializers import (CustomUserSerializer, DiagnosisSerializer,
                          ScheduleSerializer, VisitSerializer)


class MainPageView(View):
    """Main page view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get method for the main page view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        return render(request, 'base_generic.html')


class RegisterChooseView(View):
    """Register choose view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get method for the register choose view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        return render(request, 'register/index.html')


class RegisterView(View):
    """Register view."""

    def get(self, request: HttpRequest, role: str = None) -> HttpResponse:
        """Get method for the register view.

        Args:
            request (HttpRequest): The request object.
            role (str): The role of the user.

        Returns:
            HttpResponse: The response object.
        """
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if not role:
            return render(request, 'register/index.html')
        try:
            user_level = ROLES[role.lower()]
        except KeyError:
            return HttpResponseForbidden('Invalid role.')
        if user_level == UserLevel.ADMIN.value:
            return HttpResponseForbidden('Only superusers can register admins.')
        form = RegisterUserForm()
        return render(request, f'register/{role}/index.html', {STR_FORM: form})

    def post(self, request: HttpRequest, role: str = None) -> HttpResponse:
        """Post method for the register view.

        Args:
            request (HttpRequest): The request object.
            role (str): The role of the user.

        Returns:
            HttpResponse: The response object.
        """
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        try:
            user_level = ROLES[role.lower()]
        except KeyError:
            return HttpResponseForbidden('Invalid role.')
        if user_level == UserLevel.ADMIN.value:
            return HttpResponseForbidden('Only superusers can register admins.')
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_level = user_level
            if user_level == UserLevel.DOCTOR.value:
                user.is_active = False
            user.save()
            return redirect(STR_LOGIN)
        return render(request, f'register/{role}/index.html', {STR_FORM: form})


class LoginView(View):
    """Login view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get method for the login view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        if request.user.is_authenticated:
            return redirect(f'/{request.user.username}/')
        form = AuthenticationForm(request=request)
        return render(request, 'login/index.html', {STR_FORM: form})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Post method for the login view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        if request.user.is_authenticated:
            return redirect(f'/{request.user.username}/')
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect(f'/{user.username}/')
        return render(request, 'login/index.html', {STR_FORM: form})


class LogoutView(View):
    """Logout view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get method for the logout view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        logout(request)
        return redirect(STR_LOGIN)


class ProfileView(LoginRequiredMixin, View):
    """Profile view."""

    login_url = STR_LOGIN

    def get(self, request: HttpRequest, username: str = None) -> HttpResponse:
        """Get method for the profile view.

        Args:
            request (HttpRequest): The request object.
            username (str): The username of the profile.

        Returns:
            HttpResponse: The response object.
        """
        user = request.user
        if user.is_staff:
            return redirect('/admin/')
        if not username or username == user.username:
            return self.render_own_profile(request, user)
        return self.render_other_profile(request, user, username)

    def post(self, request: HttpRequest, username: str = None) -> HttpResponse:
        """Post method for the profile view.

        Args:
            request (HttpRequest): The request object.
            username (str): The username of the profile.

        Returns:
            HttpResponse: The response object.
        """
        user = request.user
        if not username or username == user.username:
            return HttpResponseForbidden('You cannot book an appointment with yourself.')
        profile_user = get_object_or_404(CustomUser, username=username)
        if user.user_level == UserLevel.PATIENT.value:
            return self.handle_patient_post(request, profile_user)
        return HttpResponseForbidden(STR_NO_ACCESS)

    def handle_patient_post(self, request: HttpRequest, doctor_user: CustomUser) -> HttpResponse:
        """Handle the POST request for a patient booking an appointment.

        Args:
            request (HttpRequest): The request object.
            doctor_user (CustomUser): The doctor user object.

        Returns:
            HttpResponse: The response object.
        """
        if doctor_user.user_level != UserLevel.DOCTOR.value:
            return HttpResponseForbidden('You can only book appointments with doctors.')

        form = VisitCreationForm(request.POST, doctor=doctor_user, patient=request.user)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = request.user
            visit.doctor = doctor_user
            visit.save()
            return redirect(STR_PROFILE, username=request.user.username)

        schedules = Schedule.objects.filter(doctor=doctor_user)
        context = {
            'doctor': doctor_user,
            STR_SCHEDULES: schedules,
            STR_FORM: form,
        }
        return render(request, 'profile/doctor_profile_for_patient.html', context)

    def render_other_profile(self, request: HttpRequest, user: CustomUser, username: str) -> HttpResponse:
        """Render the profile of another user.

        Args:
            request (HttpRequest): The request object.
            user (CustomUser): The user.
            username (str): The username of the profile.

        Returns:
            HttpResponse: The response object.
        """
        profile_user = get_object_or_404(CustomUser, username=username)
        if user.user_level == UserLevel.DOCTOR.value:
            return self.render_for_doctor(request, profile_user)
        elif user.user_level == UserLevel.PATIENT.value:
            return self.render_for_patient(request, profile_user)
        return HttpResponseForbidden(STR_NO_ACCESS)

    def render_for_doctor(self, request: HttpRequest, profile_user: CustomUser) -> HttpResponse:
        """Render the profile of a doctor.

        Args:
            request (HttpRequest): The request object.
            profile_user (CustomUser): The profile user.

        Returns:
            HttpResponse: The response object.
        """
        if profile_user.user_level == UserLevel.PATIENT.value:
            return self.render_patient_profile_for_doctor(request, profile_user)
        elif profile_user.user_level == UserLevel.DOCTOR.value:
            return self.render_doctor_profile_for_doctor(request, profile_user)
        return HttpResponseForbidden(STR_NO_ACCESS)

    def render_for_patient(self, request: HttpRequest, profile_user: CustomUser) -> HttpResponse:
        """Render the profile of a patient.

        Args:
            request (HttpRequest): The request object.
            profile_user (CustomUser): The profile user.

        Returns:
            HttpResponse: The response object.
        """
        if profile_user.user_level == UserLevel.DOCTOR.value:
            return self.render_doctor_profile_for_patient(request, profile_user)
        elif profile_user.user_level == UserLevel.PATIENT.value:
            return HttpResponseForbidden(STR_NO_ACCESS)
        return HttpResponseForbidden(STR_NO_ACCESS)

    def render_own_profile(self, request: HttpRequest, profile_user: CustomUser) -> HttpResponse:
        """Render the profile of the user.

        Args:
            request (HttpRequest): The request object.
            profile_user (CustomUser): The profile user.

        Returns:
            HttpResponse: The response object.
        """
        if profile_user.user_level == UserLevel.PATIENT.value:
            diagnoses = Diagnosis.objects.filter(patient=profile_user)
            visits = Visit.objects.filter(patient=profile_user).select_related('doctor')
            visits_info = [{
                'doctor': visit.doctor,
                'date': visit.date.strftime('%Y-%m-%d'),
                'start': f'{visit.start.hour:02d}:{visit.start.minute:02d}',
                'end': f'{visit.end.hour:02d}:{visit.end.minute:02d}',
                'status': visit.status,
                'editable': visit.status == VisitStatus.ACTIVE,
                STR_ID: visit.id,
            } for visit in visits]
            context = {
                'diagnoses': diagnoses,
                'visits_info': visits_info,
                'user': profile_user,
            }
            return render(request, 'profile/patient_profile.html', context)
        elif profile_user.user_level == UserLevel.DOCTOR.value:
            patients = Visit.objects.filter(
                doctor=profile_user, status=VisitStatus.ACTIVE,
            ).select_related('patient')
            schedules = Schedule.objects.filter(doctor=profile_user)
            schedule_info = [{
                STR_ID: schedule.id,
                'doctor': schedule.doctor,
                'start': schedule.start,  # Converts to HH:MM format
                'end': schedule.end,       # Converts to HH:MM format
                'day_of_week': calendar.day_name[int(schedule.day_of_week)],
            } for schedule in schedules]
            visits_info = [{
                'patient': visit.patient,
                'date': visit.date.strftime('%Y-%m-%d'),
                'start': f'{visit.start.hour:02d}:{visit.start.minute:02d}',
                'end': f'{visit.end.hour:02d}:{visit.end.minute:02d}',
                'status': visit.status,
                'editable': visit.status in {VisitStatus.ACTIVE, VisitStatus.SCHEDULED},
                'add_diagnosis': visit.status == VisitStatus.VISITED,
                STR_ID: visit.id,
            } for visit in Visit.objects.filter(doctor=profile_user, date__gt=date.today())]
            specialization = DoctorSpecialization.objects.filter(doctor=profile_user).first()
            if not specialization:
                specialization = '-'
            context = {
                'patients': patients,
                STR_SCHEDULES: schedule_info,
                'visits': visits_info,
                STR_SPECIALIZATION: specialization,
            }
            return render(request, 'profile/doctor_profile.html', context)

    def render_patient_profile_for_doctor(self, request: HttpRequest, patient_user: CustomUser) -> HttpResponse:
        """Render the profile of a patient for a doctor.

        Args:
            request (HttpRequest): The request object.
            patient_user (CustomUser): The patient user.

        Returns:
            HttpResponse: The response object.
        """
        diagnoses = Diagnosis.objects.filter(patient=patient_user)
        context = {
            'patient': patient_user,
            'diagnoses': diagnoses,
        }
        return render(request, 'profile/patient_profile_for_doctor.html', context)

    def render_doctor_profile_for_doctor(self, request: HttpRequest, doctor_user: CustomUser) -> HttpResponse:
        """Render the profile of a doctor for a doctor.

        Args:
            request (HttpRequest): The request object.
            doctor_user (CustomUser): The doctor user.

        Returns:
            HttpResponse: The response object.
        """
        schedules = Schedule.objects.filter(doctor=doctor_user)
        context = {
            'doctor': doctor_user,
            STR_SCHEDULES: schedules,
        }
        return render(request, 'profile/doctor_profile_for_doctor.html', context)

    def render_doctor_profile_for_patient(self, request: HttpRequest, doctor_user: CustomUser) -> HttpResponse:
        """Render the profile of a doctor for a patient.

        Args:
            request (HttpRequest): The request object.
            doctor_user (CustomUser): The doctor user.

        Returns:
            HttpResponse: The response object.
        """
        schedules = Schedule.objects.filter(doctor=doctor_user)
        if request.method == 'POST':
            form = VisitCreationForm(request.POST, doctor=doctor_user, patient=request.user)
            if form.is_valid():
                visit = form.save(commit=False)
                visit.patient = request.user
                visit.doctor = doctor_user
                visit.save()
                return redirect(STR_PROFILE, username=request.user.username)
        else:
            form = VisitCreationForm(doctor=doctor_user, patient=request.user)

        context = {
            'doctor': doctor_user,
            STR_SCHEDULES: schedules,
            STR_FORM: form,
        }
        return render(request, 'profile/doctor_profile_for_patient.html', context)


class VisitUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Visit update view."""

    model = Visit
    template_name = 'profile/visit_update.html'
    login_url = STR_LOGIN
    form_class = VisitUpdateForm

    def test_func(self):
        """Check if the user is the doctor or the patient of the visit.

        Returns:
            bool: True if the user is the doctor or the patient of the visit.
        """
        visit = self.get_object()
        return (
                (self.request.user in {visit.doctor, visit.patient})
            ) and (
                visit.status in {VisitStatus.ACTIVE, VisitStatus.SCHEDULED}
            )

    def get_success_url(self):
        """Get the success URL.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})

    def get_form_kwargs(self):
        """Pass the form_kwargs with doctor and patient.

        Returns:
            dict: The form kwargs.
        """
        kwargs = super().get_form_kwargs()
        visit = self.get_object()
        kwargs['doctor'] = visit.doctor
        kwargs['patient'] = visit.patient
        return kwargs


class AddDiagnosisView(LoginRequiredMixin, CreateView):
    """Add diagnosis view."""

    model = Diagnosis
    form_class = DiagnosisAddForm
    template_name = 'diagnosis/diagnosis_form.html'

    def get_success_url(self):
        """Return the success URL after a successful form submission.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        """Form validation method for adding a diagnosis.

        Args:
            form (DiagnosisAddForm): The form object.

        Returns:
            HttpResponse: The response object.

        Exceptions:
            ValidationError: If the doctor has not had a visit with the patient.
        """
        diagnosis = form.save(commit=False)
        diagnosis.doctor = self.request.user
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(CustomUser, id=patient_id)
        diagnosis.patient = patient
        if Visit.objects.filter(doctor=self.request.user, patient=patient).exists():
            diagnosis.save()
            messages.success(self.request, 'Диагноз успешно добавлен.')
            return super().form_valid(form)
        messages.error(self.request, 'Вы не можете добавить диагноз этому пациенту.')
        return self.form_invalid(form)


class ChangeDiagnosisStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Change diagnosis status view."""

    model = Diagnosis
    form_class = DiagnosisStatusForm
    template_name = 'diagnosis/diagnosis_update_form.html'

    def get_success_url(self):
        """Return the success URL after a successful form submission.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})

    def test_func(self):
        """Check if the user is the doctor of the diagnosis.

        Returns:
            bool: True if the user is the doctor of the diagnosis.
        """
        diagnosis = self.get_object()
        return self.request.user == diagnosis.doctor

    def handle_no_permission(self):
        """Handle the case when the user does not have permission to change the diagnosis status.

        Returns:
            HttpResponse: The response object.
        """
        messages.error(self.request, 'Вы не можете изменить статус этого диагноза.')
        return redirect(STR_LOGIN)  # Замените на ваш URL списка диагнозов


class UpdateScheduleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update schedule view."""

    model = Schedule
    form_class = ScheduleViewForm
    template_name = 'profile/update_schedule.html'
    login_url = STR_LOGIN

    def test_func(self) -> bool:
        """Check if the user is the doctor of the schedule.

        Returns:
            bool: True if the user is the doctor of the schedule.
        """
        schedule = self.get_object()
        return self.request.user == schedule.doctor

    def get_form_kwargs(self) -> dict:
        """Get the form kwargs.

        Returns:
            dict: The form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = self.request.user
        return kwargs

    def get_success_url(self) -> str:
        """Get the success URL.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})


class CreateScheduleView(LoginRequiredMixin, CreateView):
    """Create schedule view."""

    model = Schedule
    form_class = ScheduleViewForm
    template_name = 'profile/doctor_schedule_create.html'
    login_url = STR_LOGIN

    def get_success_url(self) -> str:
        """Get the success URL.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})

    def get_form_kwargs(self) -> dict:
        """Get the form kwargs.

        Returns:
            dict: The form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = self.request.user
        return kwargs

    def form_valid(self, form: ScheduleViewForm) -> HttpResponse:
        """Form validation method.

        Args:
            form (ScheduleViewForm): The form object.

        Returns:
            HttpResponse: The response object.
        """
        form.instance.doctor = self.request.user
        return super().form_valid(form)


class DeleteScheduleView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete schedule view."""

    model = Schedule
    template_name = 'profile/doctor_schedule_confirm_delete.html'
    success_url = STR_LOGIN

    def test_func(self):
        """Check if the user is the doctor of the schedule.

        Returns:
            bool: True if the user is the doctor of the schedule.
        """
        schedule = self.get_object()
        return self.request.user == schedule.doctor


class VisitViewSet(viewsets.ModelViewSet):
    """Visit view set."""

    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [IsAdminUser]


class ScheduleViewSet(viewsets.ModelViewSet):
    """Schedule view set."""

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminUser]


class DiagnosisViewSet(viewsets.ModelViewSet):
    """Diagnosis view set."""

    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAdminUser]


class CustomUserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]


class DoctorSearchView(LoginRequiredMixin, ListView):
    """Doctor search view."""

    model = CustomUser
    template_name = 'search_doctors.html'
    login_url = STR_LOGIN

    def get_queryset(self) -> CustomUser:
        """Get the queryset.

        Returns:
            CustomUser: The queryset.
        """
        queryset = CustomUser.objects.filter(user_level=UserLevel.DOCTOR.value)
        form = DoctorSearchForm(self.request.GET)

        if form.is_valid():
            cleaned_data = self.get_cleaned_data(form)
            queryset = self.apply_filters(queryset, cleaned_data)
        else:
            queryset = CustomUser.objects.none()

        return queryset.distinct()

    def get_cleaned_data(self, form):
        """Get cleaned data from the form.

        Args:
            form (DoctorSearchForm): The search form.

        Returns:
            dict: The cleaned data.
        """
        return {
            STR_FIRST_NAME: form.cleaned_data.get(STR_FIRST_NAME, '').strip(),
            STR_LAST_NAME: form.cleaned_data.get(STR_LAST_NAME, '').strip(),
            STR_SPECIALIZATION: form.cleaned_data.get(STR_SPECIALIZATION, '').strip(),
            'username': form.cleaned_data.get('username', '').strip(),
            STR_EMAIL: form.cleaned_data.get(STR_EMAIL, '').strip(),
            'phone': form.cleaned_data.get('phone', '').strip(),
        }

    def apply_filters(self, queryset, cleaned_data):
        """Apply filters to the queryset based on cleaned data.

        Args:
            queryset (QuerySet): The initial queryset.
            cleaned_data (dict): The cleaned data.

        Returns:
            QuerySet: The filtered queryset.
        """
        if cleaned_data[STR_FIRST_NAME]:
            queryset = queryset.filter(first_name__icontains=cleaned_data[STR_FIRST_NAME])
        if cleaned_data[STR_LAST_NAME]:
            queryset = queryset.filter(last_name__icontains=cleaned_data[STR_LAST_NAME])
        if cleaned_data[STR_SPECIALIZATION]:
            queryset = queryset.filter(
                doctor_specializations__specialization__icontains=cleaned_data[STR_SPECIALIZATION])
        if cleaned_data['username']:
            queryset = queryset.filter(username__icontains=cleaned_data['username'])
        if cleaned_data[STR_EMAIL]:
            queryset = queryset.filter(email__icontains=cleaned_data[STR_EMAIL])
        if cleaned_data['phone']:
            queryset = queryset.filter(phone=cleaned_data['phone'])
        return queryset

    def get_context_data(self, **kwargs):
        """Get the context data.

        Args:
            kwargs: The keyword arguments.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        context[STR_FORM] = DoctorSearchForm(self.request.GET or None)
        context['specializations'] = DoctorSpecialization.objects.filter(
            doctor__id__in=self.get_queryset().values_list(STR_ID, flat=True),
        ).distinct()
        return context


class DoctorSpecializationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Doctor specialization update view."""

    model = DoctorSpecialization
    fields = [STR_SPECIALIZATION]
    template_name = 'profile/doctor_specialization_update.html'
    login_url = STR_LOGIN

    def test_func(self):
        """Check if the user is the doctor of the specialization.

        Returns:
            bool: True if the user is the doctor of the specialization.
        """
        specialization = self.get_object()
        return self.request.user == specialization.doctor

    def get_success_url(self):
        """Get the success URL.

        Returns:
            str: The success URL.
        """
        return reverse(STR_PROFILE, kwargs={'username': self.request.user.username})
