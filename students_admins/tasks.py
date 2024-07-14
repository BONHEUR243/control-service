from celery import shared_task
from datetime import date
from Custom_user.models import Student

@shared_task
def check_deadlines():
    today = date.today()
    students = Student.objects.filter(derogation_deadline__lte=today, derogation_deadline__isnull=False)
    for student in students:
        student.update_access()
