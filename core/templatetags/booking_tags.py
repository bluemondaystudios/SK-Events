from django import template

register = template.Library()

@register.filter
def dictkey(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def artist_facing_status(status):
    """A declined request still reads as PENDING to the artist who sent it.

    Business rule: an artist only gets one real shot at "Book Me" per event
    (re-requesting is already blocked at the booking model level), so there's
    no upside to telling them "no" outright -- it just discourages them from
    using the platform. Organisers still see the true DECLINED status
    everywhere they manage bookings; this filter is for artist-facing
    screens only.
    """
    if status == "DECLINED":
        return "PENDING"
    return status
