from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    """AbstractUser's default manager expects a `username` positional arg.
    This model has none (email is USERNAME_FIELD), so createsuperuser and
    any direct create_user()/create_superuser() call needs this instead."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


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

    objects = UserManager()

class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="artist")
    stage_name = models.CharField(max_length=100, blank=True)
    social_link = models.URLField(blank=True)
    audio = models.FileField(upload_to="artist_audio/", blank=True, null=True)


class OrganiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organiserprofile")
    social_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

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
