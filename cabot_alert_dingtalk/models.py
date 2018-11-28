from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env

from django.conf import settings
# from django.core.urlresolvers import reverse
from django.template import Context, Template

import requests
import json

from logging import getLogger
logger = getLogger(__name__)

dingtalk_template = """\
Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}*is back to normal*{% else %}reporting *{{ service.overall_status }}* status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %} \
{% if alert %}{% for alias in users %} @{{ alias }}{% endfor %}{% endif %}\

{% if service.overall_status != service.PASSING_STATUS %}Checks failing:\
{% for check in service.all_failing_checks %}\
    - {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}\
{% endfor %}\
{% endif %}\
"""


class DingtalkAlert(AlertPlugin):
    name = "Dingtalk"
    author = "bdguodong"

    def send_alert(self, service, users, duty_officers):
        alert = True
        dingtalk_aliases = []
        users = list(users) + list(duty_officers)

        dingtalk_aliases = [u.dingtalk_alias for u in DingtalkAlertUserData.objects.filter(user__user__in=users)]

        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        if service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS, service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        if service.overall_status == service.PASSING_STATUS:
            color = 'good'
            if service.old_overall_status == service.WARNING_STATUS:
                alert = False  # Don't alert for recovery from WARNING status
        else:
            color = 'danger'

        c = Context({
            'service': service,
            'users': dingtalk_aliases,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME,
            'alert': alert,
        })
        message = Template(dingtalk_template).render(c)
        self._send_dingtalk_alert(message, service, color=color, sender='Cabot')

    def _send_dingtalk_alert(self, message, service, color='good', sender='Cabot'):
        url = env.get('DINGTALK_WEBHOOK_URL')
        if not url:
            logger.error('invalid dingtalk webhook url')
        # TODO: handle color
        # text temp
        ding_notification = {
            'msgtype': 'text',
            'text': {
                'content': message,
            }
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        logger.info('ding alert notification = %s' % ding_notification)
        resp = requests.post(url, headers=headers, data=json.dumps(ding_notification))
        logger.info('ding alert resp=%s.' % resp.text)
        logger.info('ding alert resp=%s.' % resp)


class DingtalkAlertUserData(AlertPluginUserData):
    name = "Dingtalk Plugin"
    dingtalk_alias = models.CharField(max_length=50, blank=True)

    def serialize(self):
        return {
            "dingtalk_alias": self.dingtalk_alias
        }
