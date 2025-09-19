from django import template

register = template.Library()

@register.filter(name='non_negative')
def non_negative(value):
    try:
        return max(float(value), 0)  # Ensure the value is non-negative
    except (ValueError, TypeError):
        return 0  # If there's a value error or type error (like None), return 0
