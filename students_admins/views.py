from django.shortcuts import render,redirect, get_object_or_404
from Custom_user.models import User,Departement, Option, Session, Intake, Level, Student, AdminStudent,Supervisor,ReferenceAmount,Message
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Exam,ExamStatus
from django.db.models import Count
from datetime import date, datetime,timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json, datetime


# Create your views here.
User = get_user_model()

def user_is_student(user):
    return user.is_student()

def user_is_supervisor(user):
    return user.is_admin()

@login_required(login_url='loginUser')
def profile(request):
    user=request.user
    user_type=user.user_type
    student=None
    admin_student=None
    supervisor=None
    claims = Message.objects.filter(receivers=request.user).order_by('-timestamp')
    unreplied_count = claims.filter(replied=False).count()
    
    if user_type=='student':
        student= Student.objects.filter(user=user).first()
        
    if user_type=='admin_student':
        admin_student= AdminStudent.objects.filter(user=user).first()
        
    if user_type=='supervisor':
        supervisor= Supervisor.objects.filter(user=user).first()
        
    reference_amount = ReferenceAmount.objects.first().amount if ReferenceAmount.objects.exists() else 0
        
    context={'user':user,'student':student,'user_type':user_type,'admin_student':admin_student,'supervisor':supervisor,'reference_amount':reference_amount,'unreplied_count':unreplied_count}
    return render(request,'profile.html',context)

@login_required
@csrf_exempt
def upload_profile_picture(request):
    if request.method == 'POST':
    
        try:
            profile_picture = request.FILES['profile_picture']
            user = request.user
            user.profile_picture = profile_picture
            user.save()
            messages.success(request, 'Profile picture uploaded successfully.')
            return redirect('profile')
        except KeyError:
            messages.error(request, 'An error occured while uploading the file, Choose a picture then try again...')
            return redirect('profile') 
    return render(request, 'profile.html')


@login_required(login_url='loginUser')
def learnUse(request):
    return render(request, 'students_admins/learn.html')
    


@login_required(login_url='loginUser')
def schedule(request):
    user = request.user
    user_type=user.user_type
    levels = Level.objects.all()
    claims = Message.objects.filter(receivers=request.user).order_by('-timestamp')
    unreplied_count = claims.filter(replied=False).count()
    if user_type=='admin_student':
        search_query=request.GET.get('search')
        if search_query:
            levels=Level.objects.filter(
                Q(name__icontains=search_query)|
                Q(intake__session__option__name__icontains=search_query)|
                Q(intake__session__option__departement__name__icontains=search_query)
            )
        else:
            levels=Level.objects.all()
        examens_groupes_par_niveau = {}
        for level in levels:
             examens_groupes_par_niveau[level] = Exam.objects.filter(level=level)

        return render(request, 'students_admins/schedule_grouped.html', {'examens_groupes_par_niveau': examens_groupes_par_niveau,'unreplied_count':unreplied_count})
    elif user_type=='student':
        student = Student.objects.get(user=user)
        exams = Exam.objects.filter(level=student.level)
    else:
        exams = []
    
    return render(request, 'students_admins/schedule.html', {'exams': exams, 'student':student,'unreplied_count':unreplied_count} )


@login_required(login_url='loginUser')
def add_schedule(request):
    if not request.user.is_admin():
        return redirect('schedule')

    if request.method == 'POST':
        course = request.POST.get('course')
        type_exam = request.POST.get('type_exam')
        date = request.POST.get('date')
        venue = request.POST.get('venue')
        level_id = request.POST.get('level')

        if not (course and type_exam and date and venue and level_id):
            return HttpResponseBadRequest("Please fill all the fields.")

        level = get_object_or_404(Level, id=level_id)
        Exam.objects.create(course=course, type_exam=type_exam, date=date, venue=venue, level=level)
        return redirect('schedule')

    levels = Level.objects.all()
    return render(request, 'students_admins/add_schedule.html', {'levels': levels})

@login_required(login_url='loginUser')
def modify_schedule(request, exam_id):
    if not request.user.is_admin():
        return redirect('schedule')

    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        exam.course = request.POST.get('course')
        exam.type_exam = request.POST.get('type_exam')
        exam.date = request.POST.get('date')
        exam.venue = request.POST.get('venue')
        level_id = request.POST.get('level')

        if not (exam.course and exam.type_exam and exam.date and exam.venue and level_id):
            return HttpResponseBadRequest("Fill all the fields Please!")
        
        exam.level = get_object_or_404(Level, id=level_id)
        exam.save()
        return redirect('schedule')

    levels = Level.objects.all()
    return render(request, 'students_admins/modify_schedule.html', {'exam': exam, 'levels': levels})


@login_required(login_url='loginUser')
def manage_students(request):
    if not request.user.is_admin:
        return redirect('profile')
    
    search_query = request.GET.get('search')
    students = Student.objects.all()
    levels = Level.objects.all()

    if search_query:
        students = students.filter(
            Q(level__name__icontains=search_query) |
            Q(student_name__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(level__intake__session__option__name__icontains=search_query) |
            Q(level__intake__session__option__departement__name__icontains=search_query)
        )
        levels = levels.filter(
            Q(name__icontains=search_query) |
            Q(intake__session__option__name__icontains=search_query) |
            Q(intake__session__option__departement__name__icontains=search_query) |
            Q(student__in=students)
        ).distinct()

    reference_amount = ReferenceAmount.objects.first().amount if ReferenceAmount.objects.exists() else 0
    
    students_grouped_by_level = {}
    
    for level in levels:
        level_students = students.filter(level=level)
        if level_students.exists():
            students_grouped_by_level[level] = level_students

    claims = Message.objects.filter(receivers=request.user).order_by('-timestamp')
    unreplied_count = claims.filter(replied=False).count()

    return render(request, 'students_admins/manage_students.html', {
        'students': students,
        'reference_amount': reference_amount,
        'students_grouped_by_level': students_grouped_by_level,
        'search_query': search_query,
        'unreplied_count': unreplied_count
    })



@login_required(login_url='loginUser')
def manage_reference_amounts(request):
    if request.method == 'POST':
        try:
            # Récupérer les données soumises par le formulaire
            amount_normal = request.POST.get('amount_normal')
            amount_type_b = request.POST.get('amount_type_b')
            amount_type_c = request.POST.get('amount_type_c')
            amount_type_d = request.POST.get('amount_type_d')

            # Mettre à jour ou créer l'objet ReferenceAmount
            reference_amount, created = ReferenceAmount.objects.get_or_create()
            reference_amount.amount_normal = amount_normal
            reference_amount.amount_type_b = amount_type_b
            reference_amount.amount_type_c = amount_type_c
            reference_amount.amount_type_d = amount_type_d
            reference_amount.save()

            # Mettre à jour les montants payés des étudiants en fonction de leur entry_period
            update_students_amounts(reference_amount)

            messages.success(request, 'Reference amounts updated successfully.')
            return redirect('manage_students')
        except:
            messages.error(request, 'Please enter valid amount!')
            return redirect('manage_reference_amounts')

    # Si la méthode HTTP n'est pas POST (affichage du formulaire)
    reference_amount = ReferenceAmount.objects.first()  # Récupérer le premier objet ReferenceAmount
    return render(request, 'students_admins/manage_reference_amounts.html', {'reference_amount': reference_amount})


@login_required(login_url='loginUser')
def update_students_amounts(reference_amount):
    students = Student.objects.all()
    for student in students:
        if student.entry_period == 'normal':
            # Convertir reference_amount.amount_normal en int si ce n'est pas déjà le cas
            amount_normal = int(reference_amount.amount_normal)  # Assurez-vous que amount_normal est un entier
            # Comparaison entre le montant payé et le montant de référence pour 'normal'
            if student.amount_paid >= amount_normal:
                student.has_access_one = True
            else:
                student.has_access_one = False
        elif student.entry_period == 'type_b':
            amount_type_b = int(reference_amount.amount_type_b)  # Assurez-vous que amount_type_b est un entier
            if student.amount_paid >= amount_type_b:
                student.has_access_one = True
            else:
                student.has_access_one = False
        elif student.entry_period == 'type_c':
            amount_type_c = int(reference_amount.amount_type_c)  # Assurez-vous que amount_type_c est un entier
            if student.amount_paid >= amount_type_c:
                student.has_access_one = True
            else:
                student.has_access_one = False
        elif student.entry_period == 'type_d':
            amount_type_d = int(reference_amount.amount_type_d)  # Assurez-vous que amount_type_d est un entier
            if student.amount_paid >= amount_type_d:
                student.has_access_one = True
            else:
                student.has_access_one = False
        student.save()





@login_required(login_url='loginUser')
def manage_student_details(request, student_id):
    if not request.user.is_admin():
        return redirect('profile')
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        amount_paid = request.POST.get('amount_paid')
        has_access_one = request.POST.get('has_access_one') == 'on'
        derogation_deadline = request.POST.get('derogation_deadline')
        
        student.has_access_one = has_access_one
        student.save()
        
        if amount_paid:
            student.amount_paid = int(amount_paid)
        
        
        
        if derogation_deadline:
            student.derogation_deadline = derogation_deadline
        else:
            student.derogation_deadline = None
        
        student.update_access()  # Update access status based on new amount paid and deadline
        
        
       

        messages.success(request, "Student details updated successfully!")
        return redirect('manage_students')
    reference_amount = ReferenceAmount.objects.first().amount if ReferenceAmount.objects.exists() else 0
    
    return render(request, 'students_admins/manage_student_details.html', {'student': student, 'reference_amount': reference_amount})



@login_required(login_url='loginUser')
def claim(request):
    if request.user.user_type == 'student':
        if request.method == 'POST':
            category = request.POST.get('category')
            subject = request.POST.get('subject')
            body = request.POST.get('body')

            if category and subject and body:
                # Create a single message
                message = Message.objects.create(
                    sender=request.user,
                    category=category,
                    subject=subject,
                    body=body
                )
                # Add all admins as receivers
                admins = User.objects.filter(user_type='admin_student')
                message.receivers.set(admins)
                message.save()
                
                messages.success(request, 'Claim sent successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'All fields are required.')

        return render(request, 'students_admins/claim.html')
    else:
        return redirect('profile')





@login_required(login_url='loginUser')
def view_claims(request):
    if request.user.user_type == 'admin_student':
        # Filtrer les réclamations par catégorie
        category = request.GET.get('category', 'all')
        claims = Message.objects.filter(receivers=request.user).order_by('-timestamp')
        if category != 'all':
            claims = claims.filter(category=category)
        
        unreplied_count = claims.filter(replied=False).count()
        return render(request, 'students_admins/aview_claims.html', {'claims': claims, 'unreplied_count': unreplied_count, 'selected_category': category})
    
    elif request.user.user_type == 'student':
        sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
        received_messages = Message.objects.filter(receivers=request.user).order_by('-timestamp')
        return render(request, 'students_admins/view_claims.html', {'sent_messages': sent_messages, 'received_messages': received_messages})
    
    else:
        return redirect('profile')







@login_required(login_url='loginUser')
def reply_claim(request, message_id):
    if request.user.user_type == 'admin_student':
        message = get_object_or_404(Message, id=message_id, receivers=request.user)
        if request.method == 'POST':
            reply_body = request.POST.get('body')
            if reply_body:
                # Create the reply message
                reply_message = Message.objects.create(
                    sender=request.user,
                    category=message.category,
                    subject=f" {message.subject}",
                    body=reply_body,
                    replied=True
                )
                # Set the original sender as the receiver of the reply
                reply_message.receivers.set([message.sender])
                reply_message.save()

                # Mark the original message as replied
                message.replied = True
                message.save()

                messages.success(request, 'Reply sent successfully.')
                return redirect('view_claims')
            else:
                messages.error(request, 'Reply body is required.')
        claims = Message.objects.filter(receivers=request.user).order_by('-timestamp')
        unreplied_count = claims.filter(replied=False).count()
        return render(request, 'students_admins/areply_claim.html', {'message': message,'unreplied_count': unreplied_count})
    else:
        return redirect('profile')



@login_required(login_url='loginUser')
def exam_status_student(request):
    student = get_object_or_404(Student, user=request.user)
    exam_statuses = ExamStatus.objects.filter(student=student).order_by('exam__date')

    status_data = []
    current_time = timezone.now()  # Utiliser la date actuelle sans l'heure

    for exam_status in exam_statuses:
        exam_date = exam_status.exam.date

        
        if exam_status.entry_time and exam_status.exit_time:
                display_status = "Present"
        else:
                display_status = "-"

        status_data.append({
            'exam': exam_status.exam,
            'status': exam_status,
            'display_status': display_status,
            'entry_time': exam_status.entry_time,
            'exit_time': exam_status.exit_time
        })

    return render(request, 'students_admins/exam_status_student.html', {'status_data': status_data})

@login_required(login_url='loginUser')
def exam_status_admin(request):
    search_query = request.GET.get('search')
    data = {}

    if search_query:
        students = Student.objects.filter(
            Q(level__name__icontains=search_query) |
            Q(student_name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
        levels = Level.objects.filter(
            Q(name__icontains=search_query) |
            Q(student__in=students)
        ).distinct()
    else:
        levels = Level.objects.all()
        students = Student.objects.all()

    for level in levels:
        exams = Exam.objects.filter(level=level)
        level_students = students.filter(level=level)

        if level_students.exists() or exams.exists():
            data[level] = {'exams': exams, 'students': []}
            
            for student in level_students:
                student_data = {'student': student, 'exam_statuses': []}
                for exam in exams:
                    exam_status, created = ExamStatus.objects.get_or_create(student=student, exam=exam)
                    current_time = timezone.now()
                    
                    if exam_status.entry_time and exam_status.exit_time:
                        status_text = "Present"
                    else:
                        status_text = "-"
                    
                    student_data['exam_statuses'].append({
                        'exam': exam,
                        'status': status_text,
                        'entry_time': exam_status.entry_time,
                        'exit_time': exam_status.exit_time
                    })
                data[level]['students'].append(student_data)

    return render(request, 'students_admins/exam_status_admin.html', {'data': data, 'search_query': search_query})









@csrf_exempt
def check_rfid(request):
    if request.method == 'POST':
        card_id = request.POST.get('cardId')
        try:
            student = Student.objects.get(cardId=card_id)
            if student.has_access_one:
                response_data = {
                    'status': 'Authorized',
                    'student_name': student.student_name.capitalize,
                    'roll_number': student.roll_number,
                    'message': 'Authorised'
                }
                
                    # Enregistrer l'entrée ou la sortie dans ExamStatus si nécessaire
                current_time = timezone.now()
                exam = Exam.objects.filter(date__date=current_time.date(), level=student.level).first()
                if exam:
                    exam_status, created = ExamStatus.objects.get_or_create(student=student, exam=exam)
                    
                    if created or not exam_status.entry_time:
                        exam_status.entry_time = current_time
                    else:
                        # Vérifier si une demi-heure s'est écoulée depuis entry_time
                        time_difference = current_time - exam_status.entry_time
                        if time_difference < timedelta(hours=0.1):
                            exam_status.entry_time = current_time
                        elif not exam_status.exit_time:
                            exam_status.exit_time = current_time
                            exam_status.status= "Present"
                            
                            # Envoyer un email
                            subject = 'Assessment finished'
                            message = render_to_string('email_exam_completed.html', {
                                'student': student,
                                'exam': exam,
                                'entry_time': exam_status.entry_time,
                                'exit_time': exam_status.exit_time,
                            })
                            lemail = EmailMessage(subject, message, to=[student.user.email])
                            lemail.content_subtype = 'html'
                            lemail.send()
                    

                    exam_status.save()
            else:
                response_data = {
                    'status': 'Not authorized',
                    'student_name': student.student_name.capitalize,
                    'roll_number': student.roll_number,
                    'message': 'Not authorised'
                }
        except Student.DoesNotExist:
            response_data = {
                'status': 'Unrecognized',
                'student_name': 'Not registered',
                'roll_number': 'ERROR/Not registered',
                'message': 'Unrecognised'
            }

        return JsonResponse(response_data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)







