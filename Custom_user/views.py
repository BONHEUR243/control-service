from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query_utils import Q
from .models import User,Departement, Option, Session, Intake, Level, Student, AdminStudent,Supervisor,Message,ReferenceAmount


User = get_user_model()

def user_is_student(user):
    return user.is_student()

def user_is_supervisor(user):
    return user.is_admin()



def activate(request,uidb64,token):
    
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except:
        user=None
        
        
    if user is not None and account_activation_token.check_token (user,token)  :
        user.is_active=True
        user.save()
        messages.success(request,f"Thanks @{user.first_name}, Now, LOGIN")
        return redirect('loginUser')
    else:
        messages.error(request,"An error occured during confirmation process, try again")
        return redirect('loginUser') 
        
   
@login_required(login_url='loginUser')
def register(request):
    page='register'
    if request.method=='POST':
            user_type = request.POST.get('user_type')
            first_name=request.POST.get('fname')
            last_name=request.POST.get('lname')
            email=request.POST.get('email')
            password=request.POST.get('pass1')
            pass2=request.POST.get('pass2')

            if password != pass2:
                messages.error(request,'verify your entered passwords,they must correspond!!!')
                return redirect ('register')
            elif len(password) < 6:
                messages.error(request,'The minimum characters are 6 for password')
                return redirect ('register')
            elif User.objects.filter(username=email):
                messages.error(request,'Email already registered !')
                return redirect ('register')
                       
            user = User.objects.create_user(
                username=email,  
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,

                is_active=False,                 
            )
            user.user_type=user_type                
            user.save()   

            if user_type == 'admin_student':
                    admin_phone = request.POST.get('admin_phone')
                    AdminStudent.objects.create(user=user, admin_phone=admin_phone)
                    

            elif user_type == 'student':
                    student_name= request.POST.get('student_name')
                    roll_number = request.POST.get('roll_number')
                    level_id = request.POST.get('level')
                    year_aca = request.POST.get('year_aca')
                    phone = request.POST.get('phone')
                    cardId = request.POST.get('cardId')
                    entry_period = request.POST.get('entry_period')
                    #option_id = request.POST.get('option')
                    # session_id = request.POST.get('session')
                    #intake_id = request.POST.get('intake')
                    #level_id = request.POST.get('level')

                    if not level_id:
                        messages.error(request, 'Level is required for students!')
                        user.delete() 
                        return redirect('register')
                    
                        
                    elif not student_name or not roll_number or not year_aca or not phone or not cardId:
                        messages.error(request,"Please fill out all the fields !")
                        user.delete()
                        return redirect('register')
                    
                    elif Student.objects.filter(roll_number=roll_number):
                        messages.error(request,"The roll number entered is already assigned to someone else")
                        user.delete()
                        return redirect('register')

                    elif Student.objects.filter(cardId=cardId):
                        messages.error(request,"The card's ID is unique and specific for each user. This means that the ID you entered is registered already")
                        user.delete()
                        return redirect('register')
                    
                    level_instance = Level.objects.get(pk=level_id)
                    Student.objects.create(user=user, roll_number=roll_number, student_name=student_name, level=level_instance,year_aca=year_aca,phone=phone,cardId =cardId,entry_period=entry_period )
                    

    
           
            
            elif user_type == 'supervisor':
                    super_phone = request.POST.get('super_phone')
                    Supervisor.objects.create(user=user, super_phone=super_phone)
            
            #Générer le token de vérification
            #token_generator=PasswordResetTokenGenerator()
            #token=token_generator.make_token(user)
            token=account_activation_token.make_token(user)

            # Generer l'uidb64
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construire URL d'activation
            activation_link = f"{request.scheme}://{request.get_host()}/activate/{uid}/{token}/"

            # Envoyer l'email d'activation
            mail_subject="Activate your user account !  "
            message = render_to_string('Custom_user/activation.html', {
                'user': user,
                'activation_link': activation_link,
            })

            lemail=EmailMessage(mail_subject,message,to=[user.email])
            if lemail.send():
                messages.success(request,f"Dear {user.first_name.capitalize()}, please go to your email '{user.email}' and  \
                                click on the activation link.In case you don't find a mail, Check the span Folder ")
                return redirect('loginUser')
            else:
                messages.error(request, f"Unfortunately the message couldn't be sent to '{user.email}', please check the spelling!!! ")
                user.delete()
              #____________________________________________________________________________________
                      
    departements = Departement.objects.all()      
    context={'page':page, 'departements': departements}
    return render(request,'Custom_user/login-register.html',context) 


def loginUser(request):
    page='loginUser'
    user=User.objects.all
    if request.user.is_authenticated :
        #return redirect('home')
        ''' if user.user_type == 'admin_student':
            return render(request,'admin_home.html')
        elif user.user_type == 'supervisor':
            return render(request,'supervisor_home.html')
        elif  user.user_type == 'student':
            return render(request,'home.html')'''
    
    
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('pass1')
        
        user = authenticate(request,username=email,password=password)
        
        if user is not None:
            login(request,user)
            if user.user_type == 'admin_student':
                return redirect('home')
            elif user.user_type == 'supervisor':
                return redirect('home')

            elif  user.user_type == 'student':
                return redirect('home')
            
        else:
            messages.error(request,"Invalid login credentials")
            return redirect('loginUser')
         
    context={'page':page}    
    return render(request,'Custom_user/login-register.html',context)
  
  
def logoutUser(request):
    
    logout(request)
    return redirect ('loginUser')


@login_required
def modify(request):
    user=User.objects.all      
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        
        try:
            user=User.objects.get(email=email)
        
        except:
            messages.error(request,'You entered an email different from yours registered')
            return redirect ('modify')        
        
            
        if password != pass2:
                messages.error(request,"The two password's fiels must match")
                return redirect ('modify')
        if len(password) < 6:
                messages.error(request,'Minimum 6 characters')
                return redirect ('modify')
        
        
                  
        user.set_password(password)          
        user.save()
        
        return redirect('loginUser')
        
        
    context={'user':user}
    return render(request,'modify.html',context)

def reset(request):
    if request.method=='POST':
        email=request.POST.get("email")
        user=User.objects.filter(Q(email=email)).first()
        if user:            
            mail_subject="Reset Passord Request!"
            message=render_to_string("Custom_user/template-reset.html",{
                'user': user.first_name,
                'domain':get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            }
            )
            lemail=EmailMessage(mail_subject,message,to=[user.email])
            lemail.content_subtype = 'html'
            
            if lemail.send():
                messages.success(request,f"Dear {user.first_name.capitalize()},We have emailed you on «{user.email}»  .  \
                                So, please go and follow the instructions. You may need to check the span Folder ")
                return redirect('reset')
            else:
                messages.error(request, f"Unfortunately the reset email message couldn't be sent to «{user.email}», check the spelling!!! ")
                return redirect('loginUser')
            
        else:
            messages.error(request,'Please enter your correct registered email !')
            return redirect('reset')    
    context={}
    return render (request,'Custom_user/reset.html',context)

def resetConfirm(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except:
        user=None
        
        
    if user is not None and account_activation_token.check_token (user,token)  :
        if request.method=='POST':
            
            password=request.POST.get('pass1')
            pass2=request.POST.get('pass2')
            
            if password != pass2:
                messages.error(request,'The passwords do no match !!!')
                return redirect ('resetConfirm')
            elif len(password) < 6:
                messages.error(request,'Password too short, Retry !')
                return redirect ('resetConfirm')
            
            user.set_password(password)  
            user.save()                  
                    
            messages.success(request,f"Dear {user.first_name}, Your password has been changed successfully ")
            return redirect('loginUser')
        
    else:
        messages.error(request,"Sorry, Invalid or expired Activation link ")
        return redirect('reset')
    return render(request,'Custom_user/reset-confirm.html',{})


@login_required(login_url='loginUser')
def home(request):
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
    return render(request,'home.html',context) 
    
    
def get_options(request, departement_id):
    options = Option.objects.filter(departement_id=departement_id)
    options_list = [{"id": option.id, "name": option.name} for option in options]
    return JsonResponse({"options": options_list})

def get_sessions(request, option_id):
    sessions = Session.objects.filter(option_id=option_id)
    sessions_list = [{"id": session.id, "name": session.name} for session in sessions]
    return JsonResponse({"sessions": sessions_list})

def get_intakes(request, session_id):
    intakes = Intake.objects.filter(session_id=session_id)
    intakes_list = [{"id": intake.id, "name": intake.name} for intake in intakes]
    return JsonResponse({"intakes": intakes_list})

def get_levels(request, intake_id):
    levels = Level.objects.filter(intake_id=intake_id)
    levels_list = [{"id": level.id, "name": level.name} for level in levels]
    return JsonResponse({"levels": levels_list})
     
    
    
    
    