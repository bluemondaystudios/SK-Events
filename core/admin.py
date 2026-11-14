from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, ArtistProfile, OrganiserProfile, Event, BookingRequest, Article


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Custom User has no username field, so the built-in UserAdmin's
    fieldsets (which reference 'username') can't be reused as-is."""

    ordering = ["email"]
    list_display = ["email", "role", "is_staff", "is_active", "date_joined"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role", {"fields": ("role",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "author", "artist", "published_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "body", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["artist"]
    date_hierarchy = "published_at"

    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "status")}),
        ("Content", {"fields": ("excerpt", "body", "featured_image")}),
        ("Attribution", {"fields": ("author", "artist")}),
        ("Publishing", {"fields": ("published_at",)}),
    )

    def get_changeform_initial_data(self, request):
        return {"author": request.user.pk}


# ---------------------------------------------------------------------------
# Legacy booking platform (retired in favour of the news/journalism site
# above). Kept registered so existing data stays browsable/exportable here,
# but nothing in the live site links to any of it any more.
# ---------------------------------------------------------------------------


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ["stage_name", "user", "social_link", "has_audio"]
    search_fields = ["stage_name", "user__email"]

    @admin.display(boolean=True, description="Audio uploaded")
    def has_audio(self, obj):
        return bool(obj.audio)


@admin.register(OrganiserProfile)
class OrganiserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "social_link"]
    search_fields = ["user__email"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "organiser", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["title", "organiser__user__email"]
    autocomplete_fields = ["organiser"]


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ["artist", "event", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["artist__stage_name", "artist__user__email", "event__title"]
    autocomplete_fields = ["artist", "event"]
