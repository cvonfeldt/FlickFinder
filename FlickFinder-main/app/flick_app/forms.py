# flick_app/forms.py
from django import forms

class UserPreferenceForm(forms.Form):
    user_id = forms.CharField(max_length=255, label="User ID")
    preferences = forms.CharField(widget=forms.Textarea, label="Enter your movie preferences")
