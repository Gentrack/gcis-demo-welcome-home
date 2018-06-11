# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA

from mailchimp3 import MailChimp

from integrationapp.models import Customer

import base64, json, requests, time, os
import random

@require_POST
@csrf_exempt
def webhook(request):
    verify_signature(request)
    json_req = json.loads(request.body)
    send_to_mailchimp(json_req)
    return HttpResponse(status=200)


def verify_signature(request):
    # x-payload-signature format:
    # t=timestampvalue,v=tokenvalue
    payload_signature = request.META.get('HTTP_X_PAYLOAD_SIGNATURE')
    t, v = payload_signature.split(',')

    # extract then validate timestamp
    timestamp = t.split('t=')[1]
    now = time.time()
    diff_minutes = (now - int(timestamp)) / 60
    # at this point you can decide to reject the request if it is too old

    # get the application's public key which was provided from the developer portal
    app_public_key = os.environ['APP_PUB_KEY']
    public_key = RSA.import_key(app_public_key)

    payload = b'{}.{}'.format(timestamp, request.body)
    sha = SHA512.new(payload)
    verifier = PKCS1_v1_5.new(public_key)

    # extract the base64 encoded signature
    signature = v[2:]
    if not verifier.verify(sha, base64.b64decode(signature)):
        raise ValueError('Payload signature is invalid!')
    print 'Payload is signed and verified.'


def setup_mailchimp_client():
    user_name = 'anystring'
    api_key = os.environ['MAILCHIMP_API_KEY']
    headers = requests.utils.default_headers()
    client = MailChimp(user_name, api_key, request_headers=headers)
    print 'MailChimp client created'
    return client


def send_to_mailchimp(json_req):
    # Get customer record from the mock CRM dataset
    account_id = json_req['data']['accountId']
    customer = query_crm(account_id)

    merge_fields = map_to_merge_fields(customer, json_req)

    client = setup_mailchimp_client()

    try:
        list_id = os.environ['MAILCHIMP_LIST_ID']
    except KeyError:
        list_name = os.environ['MAILCHIMP_LIST_NAME']
        list_id = get_id_from_name(client, list_name)

    client.lists.members.create(list_id, {
        'email_address': customer.email_address,
        'status': 'subscribed',
        'merge_fields': merge_fields,
    })
    print 'Customer added to MailChimp list: %s' % customer.email_address


def map_to_merge_fields(customer, json_req):
    merge_fields = {}

    # from Customer model
    merge_fields['FNAME'] = customer.first_name
    merge_fields['LNAME'] = customer.last_name
    merge_fields['ACCTNO'] = customer.account_id
    print 'Customer model fields populated'

    # from core event payload
    merge_fields['ACCTNAME'] = json_req['data']['accountName']
    merge_fields['PAYMENT'] = json_req['data']['paymentMethod']
    currency = json_req['data']['currency']
    if currency == 'GBP':
        curr_symbol = u'\u00A3'
        rate_symbol = 'p'
    else:
        curr_symbol = '$'
        rate_symbol = 'c'
    print 'Event core fields populated'
    
    # get merge fields for services
    services = json_req['data']['services']
    t1 = False
    t2 = False
    for service in services:
        pre = ''
        if not t1 and not t2:
            t1 = True
            pre = 'T1_'
        elif t1 and not t2:
            t2 = True
            pre = 'T2_'
        else:
            return

        merge_fields[pre + 'SERVICE'] = service['serviceType']
        merge_fields[pre + 'NAME'] = service['tariff']['name']
        merge_fields[pre + 'TYPE'] = service['tariff']['type']

        rates = service['tariff']['rates']
        rate1 = ''
        rate2 = ''
        for rate in rates:
            s_rate = str(rate['rate'])
            if rate['name'] == 'Daily':
                merge_fields[pre + 'DAILY'] = '{} {}/{}'.format(s_rate, rate_symbol, rate['per'])
            else:
                if not rate1:
                    rate1 = '{} {}/{}'.format(s_rate, rate_symbol, rate['per'])
                else:
                    rate2 = '{} {}/{}'.format(s_rate, rate_symbol, rate['per'])
        merge_fields[pre + 'RATE1'] = rate1
        merge_fields[pre + 'RATE2'] = rate2

        merge_fields[pre + 'ENDS'] = service['tariff']['tariffEnds']
        merge_fields[pre + 'UNTIL'] = service['tariff']['fixedUntil']
        exitFees = service['tariff']['exitFees']
        merge_fields[pre + 'EXIT'] = ', '.join(exitFees)

        discounts = service['tariff']['discounts']
        additional_charges = service['tariff']['additionalCharges']
        disc_and_additional = discounts + additional_charges
        merge_fields[pre + 'DISC'] = ', '.join(disc_and_additional)

        addons = service['tariff']['addons']
        merge_fields[pre + 'ADD'] = ', '.join(addons)

        merge_fields[pre + 'EAC'] = '{} kWh'.format(service['tariff']['annualEstimate']['usage'])

    print 'Merge fields constructed'
    return merge_fields


def get_id_from_name(client, list_name):
    response = client.lists.all(get_all=True)
    list_id = ''
    for list in response['lists']:
        if list_name == list['name']:
            list_id = list['id']

    return list_id


def query_crm(account_id):
    try:
        customer = Customer.objects.get(account_id=account_id)
        print 'Customer found in database: %s' % customer.email_address 
    except Customer.DoesNotExist:
        # Create a fake customer if the demo setup missed creating a customer record
        first_name = random.choice(['John', 'Paul', 'George', 'Ringo', 'William', 'Steven'])
        last_name = random.choice(['Doe', 'Smith', 'Jobs', 'Campbell', 'Gates', 'Sanders'])
        email_address = 'test{}@change-this-address.local'.format(random.randint(10, 500))
        customer = Customer.objects.create(
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
            email_address=email_address
        )
        print 'Customer does not exist, generated fake record'

    return customer
