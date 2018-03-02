# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Customer(models.Model):
    """
    Customer model in our mock CRM, you would typically pull this information from a CRM API instead of storing it in the integration layer
    """
    account_id = models.CharField(max_length=64, verbose_name="Account ID", unique=True)
    first_name = models.CharField(max_length=128, verbose_name="First Name")
    last_name = models.CharField(max_length=128, verbose_name="Last Name")
    email_address = models.EmailField(verbose_name="Email Address")

    def __str__(self):
        return "%s" % self.account_id
