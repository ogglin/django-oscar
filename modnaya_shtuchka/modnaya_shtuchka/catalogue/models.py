from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductAttribute, \
    AbstractProductAttributeValue


class Product(AbstractProduct):
    class Meta:
        ordering = ['-date_created', ]


class ProductAttribute(AbstractProductAttribute):
    ordering = models.IntegerField(null=True, default=1000)

    class Meta:
        ordering = ['ordering', 'code', ]


class ProductAttributeValue(AbstractProductAttributeValue):
    class Meta:
        ordering = ['attribute__ordering', 'attribute__code', ]
        pass


from oscar.apps.catalogue.models import *  # noqa isort:skip
