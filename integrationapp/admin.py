# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from integrationapp.models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'last_name', 'first_name', 'email_address')