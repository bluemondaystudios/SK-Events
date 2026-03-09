from django.urls import path
from . import views
from .views import profile_router

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    path("events/", views.public_events, name="public-events"),


    # Profiles
    path('profile/artist/', views.artist_profile, name='artist-profile'),
    path('profile/organiser/', views.organiser_profile, name='organiser-profile'),

    # Events
    path('events/create/', views.create_event, name='event-create'),
    

    # Booking decision (organiser only)
    path("bookings/<int:booking_id>/handle/", views.handle_booking, name="handle-booking"),


    path("profile/artist/home/", views.artist_home, name="artist-home"),
    path("profile/artist/events/", views.artist_events, name="artist-events"),


    path("profile/organiser/home/", views.organiser_home, name="organiser-home"),
    path("profile/organiser/events/", views.organiser_events, name="organiser-events"),


    



    # core/urls.py
    path("events/", views.public_events, name="public-events"),
    path("events/<int:event_id>/book/", views.book_event, name="book-event"),


    path("profile/", profile_router, name="profile"),

    path('artist/<int:artist_id>/review/', views.artist_review, name='artist-review'),



]
