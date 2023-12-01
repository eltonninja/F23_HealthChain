from django.views.generic import TemplateView
from django.shortcuts import redirect, render

#handle account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from django.contrib.auth import login


#import DoctorCreationForm and PatientCreationForm from forms.py
from accounts.forms import UserDetailsForm

from django.views.generic import TemplateView
from django.shortcuts import render


#import doctor and patient models
from accounts.models import NewUser

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


def doctor(request):
    return render(request, 'doctor.html')

def patient(request):
    return render(request, 'patient.html')

def ai(request):
    return render(request, 'ai.html')

def providers(request):
    #render 

    return render(request, 'providers.html')

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
    else:
        print("metamask_signin | account: " + ethereum_account)

    # Check if user details are already filled out
    try:
        user = NewUser.objects.get(ethereum_account=ethereum_account)
        if user and user.has_filled_details():  # Assuming `has_filled_details` method checks if details are filled
            print('-address in database || user has filled details')
            return redirect('/')  # Redirect to user dashboard or home page
        else:
            print('-address in database || user has NOT filled all details')
            return redirect('patient-details')  # Redirect to fill details form
    except NewUser.DoesNotExist:
        print('-address NOT in database || user has NOT filled all details')
        # Create New User Here::
        
        # return redirect('patient-details') # Redirect to fill details form
        pass  # Implement appropriate logic, then remove this line

    print('5')
    return render(request, 'pages/metamask_signin.html')

def patient_details(request):
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            ethereum_account = request.session.get('ethereum_account')
            # Fetch the existing user
            try:
                patient = NewUser.objects.get(ethereum_account=ethereum_account)
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

