Cabot Dingtalk Plugin
=====

Based on: https://github.com/cabotapp/cabot-check-skeleton

This is an alert plugin for the cabot service monitoring tool. 
It allows you to send alert notifications to dingtalk.

## Installation

Enter the cabot virtual environment.

```
    $ pip install git+https://github.com/bdguodong/cabot-alert-dingtalk.git
```

Edit `conf/*.env`.

```
CABOT_PLUGINS_ENABLED=cabot_alert_dingtalk
...
DINGTALK_WEBHOOK_URL=url_of_your_webhook_integration_from_dingtalk
```

Add cabot_alert_dingtalk to the installed apps in settings.py
```
    $ python manage.py syncdb
```
