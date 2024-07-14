from django.db import models
from Custom_user.models import User,Departement, Option, Session, Intake, Level, Student, AdminStudent,Supervisor

# Create your models here.

class Exam(models.Model):
    course=models.CharField(max_length=100)
    EXAM_TYPE_CHOICES = (
        ('CAT2', 'CAT2'),
        ('FAT', 'FAT'),
        ('SPECIAL', 'SPECIAL'),
        ('ToBeDetermined', 'To be determined'),
    )
    type_exam=models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    date=models.DateTimeField()
    venue=models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.course}- {self.type_exam}-{self.level.name}"
    


class ExamStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='-')
    
    def __str__(self):
        return f"{self.student.student_name} - {self.exam.course} - {self.status}"

