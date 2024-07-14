from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from datetime import date, datetime

# Create your models here.
#
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin_student', 'Admin Student'),
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    profile_picture = models.ImageField(upload_to='static/images/profile_pictures/', default='background.jpg',null=True)
    
    def is_student(self):
        return self.user_type =='student'
    
    def is_admin(self):
        return self.user_type  =='admin_student'
    
    def is_supervisor(self):
        return self.user_type =='supervisor'
    
    
    

class Departement(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Option(models.Model):
    name = models.CharField(max_length=100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return f"{self.departement.name} - {self.name}"
        

class Session(models.Model):
    name= models.CharField(max_length=100)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='sessions')

    def __str__(self):
        return f"{self.option.departement.name} - {self.option.name} - {self.name}"

class Intake(models.Model):
    name= models.CharField(max_length=100)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='intakes')

    def __str__(self):
        return f"{self.session.option.departement.name} - {self.session.option.name} - {self.session.name} - {self.name}"
    
    
class Level(models.Model):
    name = models.CharField(max_length=100)
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, related_name='levels')

    def __str__(self):
        return f"{self.intake.session.option.departement.name} - {self.intake.session.option.name} - {self.intake.session.name} - {self.name}"
       
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    #photo profile
    student_name=models.CharField(max_length=100)
    roll_number = models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    year_aca=models.CharField(max_length=100,default=2023-2024)
    phone=models.IntegerField(null=True)
    amount_paid=models.IntegerField(null=True, default=0)
    has_access_one=models.BooleanField(default=False)
    cardId=models.CharField(max_length=100,default=00000000)
    ENTRY_PERIOD_CHOICES = [
        ('normal', 'Normal'),
        ('type_b', 'Type B'),
        ('type_c', 'Type C'),
        ('type_d', 'Type D'),
    ]
    entry_period = models.CharField(max_length=10, choices=ENTRY_PERIOD_CHOICES, null=True, default='normal')
    derogation_deadline = models.DateField(null=True, blank=True)
    
    def __str__(self):
            return f"{self.student_name}-{self.roll_number} - {self.level} - {self.year_aca} - {self.phone} - {self.amount_paid} - {self.has_access_one}"

    def update_access(self):
        reference_amount = ReferenceAmount.objects.first()
        if isinstance(self.amount_paid, str):
            self.amount_paid = Decimal(self.amount_paid)
        
        if self.derogation_deadline:
            # Convertir self.derogation_deadline en un objet date si ce n'est pas déjà le cas
            if isinstance(self.derogation_deadline, str):
                self.derogation_deadline = datetime.strptime(self.derogation_deadline, '%Y-%m-%d').date()
            
            # Vérifier si la date limite de dérogation est encore valide
            if date.today() <= self.derogation_deadline:
                self.has_access_one = True
            else:
                self.has_access_one = self.amount_paid >= reference_amount.amount
        else:
            self.has_access_one = self.amount_paid >= reference_amount.amount
        
        self.save()


class AdminStudent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_phone=models.IntegerField(null=True)

    def __str__(self):
        return self.user.username
    

class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    super_phone=models.IntegerField(null=True)

    def __str__(self):
        return self.user.username

class ReferenceAmount(models.Model):
    entry_period = models.CharField(max_length=100,default='normal',null=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.entry_period} - {self.amount}"
    


class Message(models.Model):
    CATEGORY_CHOICES = [
        ('category1', 'Not authorised while i have paid'),
        ('category2', 'Derogation: Not ready financially'),
        ('category3', 'Exam done but status failed'),
        ('category4', 'Other'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receivers = models.ManyToManyField(User, related_name='received_messages')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True)
    subject = models.CharField(max_length=100,null=True)
    body = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

    
