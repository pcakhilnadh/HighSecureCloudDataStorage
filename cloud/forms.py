from django.contrib.auth.models import User 
from django import forms

from cloud.models import UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password','first_name','last_name')

class UserProfileForm(forms.ModelForm):
	
	class Meta:
		model = UserProfile
		#GENDER_CHOICES = (('Male', 'M'),('Female', 'F'))
		#gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect)
		fields = ('picture','phone_number','dob','gender')
