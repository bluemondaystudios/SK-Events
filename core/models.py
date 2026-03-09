from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    ROLE_CHOICES = (
        ('ARTIST', 'Artist'),
        ('ORGANISER', 'Organiser'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="artist")
    stage_name = models.CharField(max_length=100, blank=True)
    social_link = models.URLField(blank=True)
    audio = models.FileField(upload_to="artist_audio/", blank=True, null=True)


class OrganiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organiserprofile")
    social_link = models.URLField()
    image = models.ImageField(upload_to='images/')

class Event(models.Model):
    organiser = models.ForeignKey(OrganiserProfile, on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="event_images/")
    created_at = models.DateTimeField(auto_now_add=True)






class BookingRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "artist")  # 🔒 prevents duplicates

    def __str__(self):
        return f"{self.artist} → {self.event} ({self.status})"
