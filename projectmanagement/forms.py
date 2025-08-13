from django import forms

from authentication.models import Employee, Manager
from .models import TrainingProgram, TrainingParticipation,Certification

class TrainingProgramForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Import models within the function to avoid circular import during initialization
        from .models import Manager, TrainingProgram
        super().__init__(*args, **kwargs)
        self.fields['training_incharge'].queryset = Manager.objects.all()

    class Meta:
        model = TrainingProgram
        fields = ['name', 'description', 'start_date', 'end_date', 'for_managers', 'for_employees','training_incharge']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = TrainingParticipation
        fields = ['program', 'employee', 'manager', 'completion_status','completion_date']

        widgets = {
            'completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ParticipationForm, self).__init__(*args, **kwargs)
        
        # Adding 'None' option for employee field
        self.fields['employee'].queryset = Employee.objects.all()
        self.fields['employee'].empty_label = "None"

        # Adding 'None' option for manager field
        self.fields['manager'].queryset = Manager.objects.all()
        self.fields['manager'].empty_label = "None"



class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['participation', 'certification_name', 'certification_file', 'certification_date']
        widgets = {
            'certification_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }