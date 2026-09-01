from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout
from .models import Event, BookingRequest
from .forms import ArtistProfileForm, EventForm
from django.db.models import Q
from django.contrib import messages
from .models import BookingRequest as Booking



def home(request):
    if request.user.is_authenticated:
        if request.user.role == "ARTIST":
            return redirect("artist-home")
        elif request.user.role == "ORGANISER":
            return redirect("organiser-home")

    return render(request, "index.html")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']

            # Create the appropriate profile
            if role == 'ARTIST':
                ArtistProfile.objects.create(user=user)
            elif role == 'ORGANISER':
                OrganiserProfile.objects.create(user=user)

            login(request, user)
            if role == 'ARTIST':
                return redirect('artist-home')
            else:
                return redirect('organiser-home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'ARTIST':
                return redirect('artist-home')
            else:
                return redirect('organiser-home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')



@login_required
def profile_router(request):
    user = request.user

    if user.role == "ARTIST":
        return redirect("artist-profile")

    elif user.role == "ORGANISER":
        return redirect("organiser-profile")

    return redirect("home")


@login_required
def artist_profile(request):
    profile = ArtistProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = ArtistProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.refresh_from_db()
    else:
        form = ArtistProfileForm(instance=profile)

    # "Complete" per the ID-card spec: stage name, social link and a best
    # song all filled in. Drives the completeness indicator on the card.
    is_complete = bool(profile.stage_name and profile.social_link and profile.audio)

    return render(request, "artist_profile.html", {
        "profile": profile,
        "form": form,
        "is_complete": is_complete,
    })


@login_required
def organiser_profile(request):
    organiser = OrganiserProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = OrganiserProfileForm(request.POST, request.FILES, instance=organiser)
        if form.is_valid():
            form.save()
    else:
        form = OrganiserProfileForm(instance=organiser)

    return render(request, "organiser_profile.html", {
        "organiser": organiser,
        "form": form,
        "event_count": Event.objects.filter(organiser=organiser).count(),
    })


@login_required
def handle_booking(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id)

    if booking.event.organiser.user != request.user:
        messages.error(request, "Not authorised.")
        return redirect("organiser-events")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            booking.status = "ACCEPTED"
        elif action == "decline":
            booking.status = "DECLINED"

        booking.save()

    return redirect("organiser-events")



@login_required
def create_event(request):
    organiser = OrganiserProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organiser = organiser
            event.save()
            return redirect("organiser-profile")
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})


@login_required
def book_event(request, event_id):
    if request.user.role != "ARTIST":
        messages.error(request, "Only artists can book events.")
        return redirect("events")

    event = get_object_or_404(Event, id=event_id)
    artist = get_object_or_404(ArtistProfile, user=request.user)

    booking, created = BookingRequest.objects.get_or_create(
        event=event,
        artist=artist,
        defaults={"status": "PENDING"}
    )

    if not created:
        messages.info(request, "You already requested this event.")
    else:
        messages.success(request, "Booking request sent.")

    return redirect("artist-events")

@login_required
def booking_action(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id)
    if booking.event.organiser.user != request.user:
        return redirect('home')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['ACCEPTED', 'DECLINED']:
            booking.status = action
            booking.save()
    return redirect('organiser-profile')



def public_events(request):
    events = Event.objects.all()
    return render(request, "events.html", {"events": events})


@login_required
def artist_home(request):
    if request.user.role != "ARTIST":
        return redirect("home")

    artist = request.user.artist

    bookings = BookingRequest.objects.filter(artist=artist).select_related("event")

    stats = {
        # DECLINED folds into "pending" here -- see artist_facing_status:
        # artists get one shot at "Book Me" per event either way, and a
        # declined request is never shown to them as a hard no.
        "pending": bookings.filter(status__in=["PENDING", "DECLINED"]).count(),
        "accepted": bookings.filter(status="ACCEPTED").count(),
    }

    recent_activity = bookings.order_by("-created_at")[:5]

    return render(request, "artist_home.html", {
        "requested": bookings.count(),
        "artist": artist,
        "stats": stats,
        "recent_activity": recent_activity,
    })

@login_required
def organiser_home(request):
    if request.user.role != "ORGANISER":
        return redirect("home")

    organiser = request.user.organiserprofile

    events = Event.objects.filter(organiser=organiser)

    pending_requests = BookingRequest.objects.filter(
        event__organiser=organiser,
        status="PENDING"
    ).select_related("artist", "event")

    stats = {
        "events": events.count(),
        "pending_requests": pending_requests.count(),
    }

    return render(request, "organiser_home.html", {
        "organiser": organiser,
        "stats": stats,
        "pending_requests": pending_requests,
    })

@login_required
def organiser_events(request):
    user = request.user

    events = Event.objects.filter(organiser=user.organiserprofile)

    bookings = BookingRequest.objects.filter(
        event__in=events
    ).select_related("artist", "event")

    return render(
        request,
        "profile/organiser/events.html",
        {
            "events": events,
            "bookings": bookings,
        },
    )


@login_required
def artist_events(request):
    artist = get_object_or_404(ArtistProfile, user=request.user)
    events = Event.objects.all()

    bookings = BookingRequest.objects.filter(artist=artist)
    booking_status = {b.event.id: b.status for b in bookings}

    return render(request, "profile/artist/events.html", {
        "events": events,
        "booking_status": booking_status,
    })



@login_required
def artist_review(request, artist_id):
    if request.user.role != "ORGANISER":
        return redirect("home")

    organiser = request.user.organiserprofile
    artist = get_object_or_404(ArtistProfile, id=artist_id)

    # Only allow review if organiser has a booking with this artist
    has_relationship = BookingRequest.objects.filter(
        event__organiser=organiser,
        artist=artist
    ).exists()

    if not has_relationship:
        messages.error(request, "You are not authorised to view this artist.")
        return redirect("organiser-home")

    bookings = BookingRequest.objects.filter(
        artist=artist,
        event__organiser=organiser
    ).select_related("event")

    accepted_events = BookingRequest.objects.filter(
        artist=artist,
        status="ACCEPTED"
    ).select_related("event")

    return render(request, "profile/organiser/artist_review.html", {
        "artist": artist,
        "bookings": bookings,
        "accepted_events": accepted_events,
    })


@login_required
def organiser_decisions(request):
    organiser = request.user.organiser

    booking = (
        BookingRequest.objects
        .filter(
            event__organiser=organiser,
            status="PENDING"
        )
        .select_related("artist", "event")
        .order_by("created_at")
        .first()
    )

    return render(
        request,
        "profile/organiser/decision_card.html",
        {"booking": booking}
    )

