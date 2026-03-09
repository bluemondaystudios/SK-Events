from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ArtistProfile, OrganiserProfile, Event

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('ARTIST', 'Artist'),
        ('ORGANISER', 'Organiser'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="I am an")

    class Meta:
        model = User
        fields = ('email', 'role', 'password1', 'password2')

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ["stage_name", "social_link", "audio"]


class OrganiserProfileForm(forms.ModelForm):
    class Meta:
        model = OrganiserProfile
        fields = ('social_link', 'image')

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "image"]
