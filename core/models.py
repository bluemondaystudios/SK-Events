from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import Truncator, slugify


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


class Article(models.Model):
    """A news/blog post about Sekhukhune's entertainment scene. Admin/staff
    write these through the Django admin -- no public authoring flow."""

    CATEGORY_CHOICES = (
        ("NEWS", "News"),
        ("INTERVIEW", "Interview"),
        ("EVENT_RECAP", "Event Recap"),
        ("RELEASE", "New Release"),
        ("OPINION", "Opinion"),
    )

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="NEWS")
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        help_text="Shown in article listings. Leave blank to auto-generate from the body.",
    )
    body = models.TextField()
    featured_image = models.ImageField(upload_to="article_images/", blank=True, null=True)

    author = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
        related_name="articles",
    )
    # Optional link to an existing artist profile, e.g. "MC Thunder just
    # shook the ground at Youth Culture Fest" links straight to their page.
    artist = models.ForeignKey(
        ArtistProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="DRAFT")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        if self.status == "PUBLISHED" and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base = slugify(self.title)[:200] or "article"
        slug = base
        n = 1
        while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            n += 1
            slug = f"{base}-{n}"
        return slug

    @property
    def display_excerpt(self):
        return self.excerpt or Truncator(self.body).words(40)
