from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

#import DoctorCreationForm and PatientCreationForm from forms.py
from accounts.forms import UserDetailsForm, UserEditForm, fhirForm

from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from accounts.models import NewUser
import requests
import json

def HomePageView(request):
    return render(request, 'pages/home.html')


def AboutPageView(request):
    return render(request, 'pages/about.html')


def doctor(request):
    return render(request, 'doctor.html')

def patient(request):
    return render(request, 'patient.html')

def send_post_to_flask(data):
    # URL of the Flask app
    url = 'http://localhost:5000/fhir_predict'
    headers = {'Content-Type': 'application/json'}

def ai(request):
    if request.method == 'POST':
        form = fhirForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file
            uploaded_file = request.FILES['fhir_file']
            # Read the content of the file
            file_data = uploaded_file.read()
            # Convert file data to JSON object if it's JSON
            try:
                json_data = json.loads(file_data)
            except json.JSONDecodeError:
                # Handle error if the file is not a valid JSON
                return render(request, 'ai.html', {'error': 'Invalid JSON file'})
            # Now send this data to the Flask app
            response = send_post_to_flask(json_data)
            return render(request, 'ai.html', {'response': response})
    else:
        form = fhirForm()
    context = {'form': form}
    return render(request, 'ai.html', context)  

def providers(request):
    context = {
    'user': NewUser.objects.all(),
    'users': NewUser.objects.exclude(specialty__isnull=True).exclude(specialty='')}
    return render(request, 'providers.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def process_account(request):
    data = json.loads(request.body)
    account = data.get('account')
    print(request.body)
    # Process the account data here

    return JsonResponse({'status': 'success'})

def metamask_signin(request):
    # Retrieve Ethereum account from session or request
    ethereum_account = request.GET.get('account')
    
    if ethereum_account is None:
        print("metamask_signin | account: None")
        return render(request, 'pages/metamask_signin.html') #return to signin, it didnt work
    
    print("metamask_signin | account: " + ethereum_account)
    user = authenticate(request, ethereum_account=ethereum_account)

    if user:
        login(request, user, backend='accounts.auth.EthereumAuthenticationBackend')
        if user.has_filled_details():
            print('-address in database || user has filled details')
            return redirect('/')  # All set! Redirect to the home page
        else:
            print('-address in database || user has NOT filled all details')
    else:
        # Create a new user if not exist
        print('-address NOT in database || user has NOT filled all details')
        new_user = NewUser.objects.create(username=ethereum_account)
        new_user.save()
        login(request, new_user, backend='accounts.auth.EthereumAuthenticationBackend')
        print('New user created with username=', ethereum_account)
    return redirect('patient-details')  # Redirect to fill details form
    

def patient_details(request):
    if request.method == 'POST':
        form = UserDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')  # Redirect to home after saving the form
        
        # Handle invalid form case if necessary
    else:
        form = UserDetailsForm(instance=request.user)
    
    return render(request, 'patient_details.html', {'form': form})

def fhir_upload(request):
    if request.method == 'POST':
        form = fhirForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = fhirForm()

    context = {'form': form}
    return render(request, 'fhir_upload.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect to some page after saving the form, e.g., back to the profile page
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)

    context = {'form': form}
    return render(request, 'pages/profile.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Delete the user
        logout(request)  # Log the user out
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('/')  # Redirect to the home page or a goodbye page

    return render(request, 'delete-account.html')