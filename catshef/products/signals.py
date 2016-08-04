from django.db.models.signals import pre_save
from django.dispatch import receiver
import django.core.exceptions as exceptions

from products.models import ProductNutrition

@receiver(pre_save, sender=ProductNutrition)
def validate_prod_nutr_fields(sender, instance, *args, **kwargs):
    if instance.protein < 0:
        raise exceptions.ValidationError('"{}" is an invalid ammount '
        'for field \'protein\', ''since it cannot be '
        'negative.'.format(instance.protein))

    if instance.carbs < 0:
        raise exceptions.ValidationError('"{}" is an invalid ammount '
            'for field \'carbs\', ''since it cannot be '
            'negative.'.format(instance.carbs))

    if instance.fat < 0:
        raise exceptions.ValidationError('"{}" is an invalid ammount '
            'for field \'fat\', ''since it cannot be '
            'negative.'.format(instance.fat))

    if instance.calories is not None:
        if instance.calories < 0:
            raise exceptions.ValidationError('"{}" is an invalid ammount '
            'for field \'calories\', ''since it cannot be '
            'negative.'.format(instance.calories))