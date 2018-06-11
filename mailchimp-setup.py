# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from mailchimp3 import MailChimp
import argparse, json, os, requests


def list_exists(client, list_name):
    response = client.lists.all(get_all=True)
    # get existing lists
    existing_list = {}
    for list in response['lists']:
        existing_list[list['name']] = list['id']

    if list_name in existing_list:
        return (True, existing_list)

    return (False, existing_list)


def create_mailing_list(client, list_name):
    list_id = None
    try:
        response = client.lists.create({
            'name': list_name,
            'contact': {
                'company': 'Energise',
                'address1': '123 Main St',
                'address2': 'St Marys Ocean',
                'city': 'Auckland',
                'state': 'Auckland',
                'zip': '1011',
                'country': 'New Zealand',
            },
            'permission_reminder': 'You are receiving this email because you signed up for our service via our website.',
            'campaign_defaults': {
                'from_name': 'John Doe',
                'from_email': 'jdoe@energise.example',
                'subject': 'Welcome to Energise!',
                'language': 'English',
            },
            'email_type_option': False
        })
        list_id = response['id']
    except Exception as e:
        print('Failed to create mailing list because of error {}'.format(str(e)))
        exit(1)

    return list_id


def get_merge_fields():
    merge_dict = OrderedDict()
    # key: tag, values: name, type, default
    merge_dict['ACCTNO'] = ('Account Number', 'text', '')
    merge_dict['ACCTNAME'] = ('Account Name', 'text', '')
    merge_dict['PAYMENT'] = ('Payment Method', 'dropdown', 'Direct Debit')
    merge_dict['T1_SERVICE'] = ('Tariff 1 - Service', 'text', 'Electricity')
    merge_dict['T1_NAME'] = ('Tariff 1 - Name', 'text', 'Economy 7')
    merge_dict['T1_TYPE'] = ('Tariff 1 - Type', 'text', 'Fixed Rate')
    merge_dict['T1_RATE1'] = ('Tariff 1 - Unit Rate 1', 'text', '20.49 p/kWh')
    merge_dict['T1_RATE2'] = ('Tariff 1 - Unit Rate 2', 'text', '8.22 p/kWh')
    merge_dict['T1_DAILY'] = ('Tariff 1 - Daily Rate', 'text', '16.23 p/day (5,923.95/year)')
    merge_dict['T1_ENDS'] = ('Tariff 1 - Ends', 'date', '')
    merge_dict['T1_UNTIL'] = ('Tariff 1 - Price Fixed', 'date', '')
    merge_dict['T1_EXIT'] = ('Tariff 1 - Exit Fees', 'text', '')
    merge_dict['T1_DISC'] = ('Tariff 1 - Discounts', 'text', '')
    merge_dict['T1_ADD'] = ('Tariff 1 - Additional', 'text', '')
    merge_dict['T2_SERVICE'] = ('Tariff 2 - Service', 'text', 'Gas')
    merge_dict['T2_NAME'] = ('Tariff 2 - Name', 'text', 'Gas Home')
    merge_dict['T2_TYPE'] = ('Tariff 2 - Type', 'text', 'Fixed Rate')
    merge_dict['T2_RATE1'] = ('Tariff 2 - Unit Rate 1', 'text', '12.01 p/kWh')
    merge_dict['T2_RATE2'] = ('Tariff 2 - Unit Rate 2', 'text', '')
    merge_dict['T2_DAILY'] = ('Tariff 2 - Daily Rate', 'text', '12.33 p/day (4,500.45/year)')
    merge_dict['T2_ENDS'] = ('Tariff 2 - Ends', 'date', '')
    merge_dict['T2_UNTIL'] = ('Tariff 2 - Price Fixed', 'date', '')
    merge_dict['T2_EXIT'] = ('Tariff 2 - Exit Fees', 'text', '')
    merge_dict['T2_DISC'] = ('Tariff 2 - Discounts', 'text', '')
    merge_dict['T2_ADD'] = ('Tariff 2 - Additional', 'text', '')

    return merge_dict


def create_merge_fields(client, list_id):
    try:
        # remove 3 and 4 (ADDRESS and PHONE)
        client.lists.merge_fields.delete(list_id=list_id, merge_id='3')
        client.lists.merge_fields.delete(list_id=list_id, merge_id='4')

        merge_dict = get_merge_fields()
        for tag, (field_name, field_type, field_default) in merge_dict.iteritems():
            merge_data = {
                'tag': tag,
                'name': field_name,
                'type': field_type,
                'default_value': field_default
            }
            if field_type == 'date':
                merge_data['options'] = {'date_format': 'DD/MM/YYYY'}
            if tag == 'PAYMENT':
                merge_data['options'] = {'choices': ['Direct Debit', 'Other']}

            client.lists.merge_fields.create(list_id=list_id, data=merge_data)
    except Exception as e:
        print('Failed to create merge fields with error {}'.format(str(e)))
        exit(1)


def setup_mailchimp_client():
    headers = requests.utils.default_headers()
    # mailchimp credentials
    user_name = 'anystring' # not required by API
    api_key = os.environ['MAILCHIMP_API_KEY']

    # login to mailchimp
    client = MailChimp(user_name, api_key, request_headers=headers)
    return client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up a MailChimp mailing list for welcome pack events")
    parser.add_argument('list_name', metavar='L', type=str, nargs=1, help='Name of the list that will be created')

    args = parser.parse_args()

    client = setup_mailchimp_client()
    list_name = args.list_name[0]
    exists, list_dict = list_exists(client, list_name)
    if not exists:
        list_id = create_mailing_list(client, list_name)
        create_merge_fields(client, list_id)
        print(list_id)
    else:
        print(list_dict[list_name])
