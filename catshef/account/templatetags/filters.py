from django import template

register = template.Library()

@register.filter(name='add_attrs')
def add_attrs(value, arg):
    return value.as_widget(attrs={'class':arg})
