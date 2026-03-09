from django import template

register = template.Library()

@register.filter
def dictkey(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)
