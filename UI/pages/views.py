from django.views.generic import TemplateView
from django.shortcuts import render


#import doctor and patient forms
from accounts.forms import DoctorCreationForm, PatientCreationForm
from django.views.generic import TemplateView
from django.shortcuts import render

class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


def create_doctor(request):
    form = DoctorCreationForm()
    return render(request, 'create_doctor.html', {'form': form})

def create_patient(request):
    form = PatientCreationForm()
    return render(request, 'create_patient.html', {'form': form})