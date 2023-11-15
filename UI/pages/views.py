from django.views.generic import TemplateView
from django.shortcuts import redirect, render


#import doctor and patient forms
from accounts.forms import DoctorCreationForm, PatientCreationForm
from django.views.generic import TemplateView
from django.shortcuts import render

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DoctorCreationForm()
    return render(request, 'doctor_signup.html', {'form': form})


def patient_signup(request):
    form = PatientCreationForm()
    return render(request, 'create_patient.html', {'form': form})

def doctor(request):
    return render(request, 'doctor.html')

def patient(request):
    return render(request, 'patient.html')