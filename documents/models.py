from django.db import models

class Document(models.Model):
    user_id = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, blank=True, null=True)  # New field for email
    aadhar_card = models.FileField(upload_to='documents/aadhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='documents/pan/', blank=True, null=True)
    bank_details = models.FileField(upload_to='documents/bank/', blank=True, null=True)
    previous_payslip = models.FileField(upload_to='documents/payslip/', blank=True, null=True)
    experience_certificate = models.FileField(upload_to='documents/experience/', blank=True, null=True)
    degree_certificate = models.FileField(upload_to='documents/degree/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class ManagerDocument(models.Model):
    user_id = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, blank=True, null=True)  # New field for email
    aadhar_card = models.FileField(upload_to='documents/aadhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='documents/pan/', blank=True, null=True)
    bank_details = models.FileField(upload_to='documents/bank/', blank=True, null=True)
    previous_payslip = models.FileField(upload_to='documents/payslip/', blank=True, null=True)
    experience_certificate = models.FileField(upload_to='documents/experience/', blank=True, null=True)
    degree_certificate = models.FileField(upload_to='documents/degree/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    

class SupervisorDocument(models.Model):
    user_id = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, blank=True, null=True)  # New field for email
    aadhar_card = models.FileField(upload_to='documents/aadhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='documents/pan/', blank=True, null=True)
    bank_details = models.FileField(upload_to='documents/bank/', blank=True, null=True)
    previous_payslip = models.FileField(upload_to='documents/payslip/', blank=True, null=True)
    experience_certificate = models.FileField(upload_to='documents/experience/', blank=True, null=True)
    degree_certificate = models.FileField(upload_to='documents/degree/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"