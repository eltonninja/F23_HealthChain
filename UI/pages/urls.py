from django.urls import path

from .views import HomePageView, AboutPageView, doctor_signup, patient_signup, doctor, patient, ai, providers, process_account, patient_details, metamask_signin


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path('doctor_signup/', doctor_signup, name='doctor_signup'),
    path('patient_signup/', patient_signup, name='patient_signup'),
    path('doctor/', doctor, name='doctor'),
    path('patient/', patient, name='patient'),
    path('ai/', ai, name='ai'),
    path('providers/', providers, name='providers'),

    path('path-to-your-django-view/', process_account, name='process_account'),
    path('patient-details/', patient_details, name='patient-details'),
    path('metamask_signin/', metamask_signin, name='metamask_signin'),
]
