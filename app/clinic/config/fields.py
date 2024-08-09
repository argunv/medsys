FIELD_USER_LEVEL = 'user_level'
FIELD_IS_ACTIVE = 'is_active'
FIELD_LAST_LOGIN = 'last_login'
FIELD_DATE_JOINED = 'date_joined'

START_END_ATTRS = {'type': 'time', 'step': 900, 'min': '00:00', 'max': '23:45'}
DATE_ATTRS = {'type': 'date'}

VISIT_FIELDS = ('doctor', 'patient', 'date', 'start', 'end', 'status', 'description')
SCHEDULE_FIELDS = ('doctor', 'day_of_week', 'start', 'end')
DIAGNOSIS_FIELDS = ('doctor', 'patient', 'description', 'is_active')

MAX_EMAIL_LENGTH = 64
MAX_USERNAME_LENGTH = 15

SERIALIZER_FIELDS = {
    'User': ('id', 'username', 'first_name', 'last_name', 'phone', 'email', 'user_level'),
    'Visit': ('id', 'doctor', 'patient', 'date', 'start', 'end', 'status', 'description'),
    'Schedule': ('id', 'doctor', 'start', 'end', 'day_of_week'),
    'Diagnosis': ('id', 'description', 'patient', 'doctor', 'is_active', 'created_at'),
    'DoctorSpecialization': ('doctor', 'specialization')
}