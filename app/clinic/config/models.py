from django.db.models import TextChoices

STATUS_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('visited', 'Visited'),
    ('missed', 'Missed'),
    ('cancelled', 'Cancelled'),
]
FIRST_NAME_MAX_LENGTH = 30
LAST_NAME_MAX_LENGTH = 30
STATUS_MAX_LENGTH = 30
SPECIALTY_MAX_LENGTH = 30
DAY_OF_WEEK_CHOICES = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

class VisitStatus(TextChoices):
    """VisitStatus enum for defining the status of a visit."""

    VISITED = 'visited', 'Visited'
    MISSED = 'missed', 'Missed'
    CANCELLED = 'cancelled', 'Cancelled'
    ACTIVE = 'active', 'Active'
    SCHEDULED = 'scheduled', 'Scheduled'
