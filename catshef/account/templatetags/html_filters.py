from django import template

register = template.Library()

def _add_attr_to_boundfield(bound_field, attr_name, attr_value,
    override=False, separator=' '):
    """
    Generic method for adding attributes to bound fields.

    Args:
        bound_fild (BoundField): BoundField instance to add the attr to
        attr_name (str): name of new attribute to be added
        attr_value (str): value of the new attribute
        override (bool): indicates wether attr_name should be overriden(i.e.
            replaced), if it's already in the Fields widget attributes
        separator (str): string used to append the attr_value if attr_name is 
            already in the Field widget attributes (only has effect if  
            override=False)
    """
    field = bound_field.field  # related Form field instance
    field_attrs = field.widget.attrs  # attrs of current widget

    if override:
        field.widget.attrs = {**field_attrs, **{attr_name: attr_value}}
        return bound_field
    # Don't override, append the content if the attr_name being added is already
    # present    
    if attr_name in field_attrs:
        # if an attribute that's being added is already present, then append
        # the contents of the new attribute to it
        field_attrs[attr_name] += separator + attr_value
    else:
        # if the attribute being added is a new one, then simply merge both of
        # of the dicts
        field.widget.attrs = {**field_attrs, **{attr_name: attr_value}}
    return bound_field

@register.filter(name='add_class')
def add_class(value, arg):
    return _add_attr_to_boundfield(value, 'class', arg)

@register.filter(name='add_placeholder')
def add_placeholder(value, arg):
    return _add_attr_to_boundfield(value, 'placeholder', arg, override=True)
