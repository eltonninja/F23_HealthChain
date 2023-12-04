from django.views.generic import TemplateView
from django.shortcuts import redirect, render

#handle account
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from django.contrib.auth import login


#import DoctorCreationForm and PatientCreationForm from forms.py
from accounts.forms import UserDetailsForm, UserEditForm, fhirForm

from django.views.generic import TemplateView
from django.shortcuts import render

from accounts.models import NewUser
import requests
import json

def HomePageView(request):
    context = {'user': getUser(request)}
    return render(request, 'pages/home.html', context)


def AboutPageView(request):
    context = {'user': getUser(request)}
    return render(request, 'pages/about.html', context)


def doctor(request):
    return render(request, 'doctor.html')

def patient(request):
    return render(request, 'patient.html')

def send_post_to_flask(data):
    # URL of the Flask app
    url = 'http://localhost:5000/fhir_predict'
    headers = {'Content-Type': 'application/json'}

    json_data = json.dumps(data)

    # Send the POST request
    response = requests.post(url, data=json_data, headers=headers)

    # Handle the response
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Request failed with status code {}'.format(response.status_code)}    

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

    context = {'user': getUser(request), 'form': form}
    return render(request, 'ai.html', context)  

from django.contrib.auth import get_user_model

def providers(request):
    context = {'user': getUser(request), 'users': NewUser.objects.all()}
    return render(request, 'providers.html', context)

# def metamask_signin(request):
#     return render(request, 'pages/metamask_signin.html')

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
    request.session['ethereum_account'] = ethereum_account  # Store in session

    # Check if user details are already filled out
    try:
        user = NewUser.objects.get(username=ethereum_account)
        if user and user.has_filled_details():  # Assuming `has_filled_details` method checks if details are filled
            print('-address in database || user has filled details')
            return redirect('/')  # All set! : Redirect to user dashboard or home page, all set
        else:
            print('-address in database || user has NOT filled all details')
    except NewUser.DoesNotExist:
        print('-address NOT in database || user has NOT filled all details')
        # Create a new user with the Ethereum account as the username
        new_user = NewUser(username=ethereum_account)
        new_user.save()
        print('New user created with username=', ethereum_account)
    
    # IF here, profile need to be updated, redirect to patient-details to do so
    return redirect('patient-details')  # Redirect to fill details form
    

def patient_details(request):
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            ethereum_account = request.session.get('ethereum_account')
            print("retrieved address: " + ethereum_account)
            # Fetch the existing user
            try:
                patient = NewUser.objects.get(username=ethereum_account)
                # Update user details
                for field, value in form.cleaned_data.items():
                    setattr(patient, field, value)
                patient.save()
                backend = NewUser.objects.get(id=patient.id)
                user = backend
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/')
        
            except NewUser.DoesNotExist:
                # Handle case where user does not exist
                pass  # Implement appropriate logic
    else:
        form = UserDetailsForm()
    return render(request, 'patient_details.html', {'form': form})

def fhir_upload(request):
    if request.method == 'POST':
        form = fhirForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = fhirForm()

    context = {'user': getUser(request), 'form': form}
    return render(request, 'fhir_upload.html', context)

def profile(request):
    #get user
    user = getUser(request)

    #if user not exist, return to login, no reason should be in profile
    if user is None:
        return redirect('login')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Redirect to some page after saving the form, e.g., back to the profile page
            return redirect('profile')
    else:
        form = UserEditForm(instance=user)

    context = {'user': user, 'form': form}
    return render(request, 'pages/profile.html', context)

#Return User if exists in database
def getUser(request):
    ethereum_account = request.session.get('ethereum_account')

    if ethereum_account is None:
        return None

    user = NewUser.objects.get(username=ethereum_account)

    return user