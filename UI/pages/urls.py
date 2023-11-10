from django.urls import path

from .views import HomePageView, AboutPageView, doctor_signup, patient_signup

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path('doctor_signup/', doctor_signup, name='doctor_signup'),
    path('patient_signup/', patient_signup, name='patient_signup'),

]
