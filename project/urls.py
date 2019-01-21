"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from rest_framework.documentation import include_docs_urls

from service import views

urlpatterns = [
    path('local_healthcheck', views.local_healthcheck),
    path('monks/healthcheck', views.monks_health_check),
    path('service-metadata', views.monks_service_meta),
    url('', include('django_prometheus.urls'))
]

if settings.DEBUG:
    urlpatterns += [
        path('api/v1/', include('service.urls')),
        path('docs/', include_docs_urls(title='Sample Service API Documentation')),
        path('', RedirectView.as_view(url=reverse_lazy('api-docs:docs-index'), permanent=False)),
    ]
