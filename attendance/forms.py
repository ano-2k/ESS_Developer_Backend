from django import forms
from .models import DepartmentActiveJob, Event
class DepartmentActiveJobForm(forms.ModelForm):
    class Meta:
        model = DepartmentActiveJob
        fields = ['role', 'experience_level', 'location', 'job_type', 'openings']
        
        
        #calendar
        

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
        

from django import forms
from .models import Offer  # Import the Offer model

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer  # Associate the form with the Offer model
        fields = ['role', 'email', 'status','name','date']  # Include the fields you want in the for
        
