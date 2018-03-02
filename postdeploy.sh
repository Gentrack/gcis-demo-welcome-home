#!/bin/sh
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@localhost', 'integrations-are-fun!')" | python manage.py shell
LIST_ID=`python mailchimp-setup.py "$MAILCHIMP_LIST_NAME"`
