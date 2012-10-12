# Django Analytics client

django-analytics-client is a Django app used to send server side analytics to the Funkbit analytics backend using Celery.

This is an early draft and work in progress.


## Installation

Install `django-analytics-client` (available on PyPi):

    pip install django-analytics-client

## Configuration

The following settings needs to be defined in your `settings.py`:

- ANALYTICS_USERNAME (Analytics service username.)
- ANALYTICS_PASSWORD (Analytics service password.)
- ANALYTICS_SITE_ID (The analytics site id we collect data for.)
- ANALYTICS_HOST (The hostname for the analytics service.)
- ANALYTICS_PORT (The port number for the analytics service.)
- ANALYTICS_ENABLED (Disable or enable analytics reporting.)

## Usage

Some examples:

- Middleware example in `middleware.py`
- Generic example in `sample.py`
- Celery tasks in `tasks.py`