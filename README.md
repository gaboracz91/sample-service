#How to set up a dockerized DRF(django rest framework) project

## Step 1: Creation

- Pycharm > New Project:
    - Give it the name of the service, ie:  
    - Select a python3 interpreter
    - Create


## Step 2: Setup
### Create .gitignore
```
db.sqlite3
.idea/
*.pyc
```

### Installing requirements
- Add requirements.txt to your project with the following packages:
```
Django==2.0.2
djangorestframework
markdown
coreapi
django-cors-headers
gunicorn
```
- Run pip install -r requirements.txt

### Create the django project
```
django-admin startproject project .
```
### Update project/settings.py

- Update the following lines to enable starbug
```
ALLOWED_HOSTS = ['*']
```

- Add the following lines to add SECURE_PROXY_SSL_HEADER to enable https
```
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

- Add drf and corsheader to INSTALLED_APPS and MIDDLEWARE to enable https and gunicorn
```
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'corsheaders',
]
```

```
MIDDLEWARE = [ 
    ...,
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', <-- add only this line, directly between SessionMiddleware and CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]
```

### Create an app
```
python manage.py startapp service
```

- Add service to project/settings.py INSTALLED_APPS
```
INSTALLED_APPS = [
    ...,
    'service'
```

- Create new Model in service/models.py
```
class Contact(models.Model):
    email = models.EmailField(null=True, help_text="The email of the contact detail.")
    phone = models.CharField(null=True, max_length=16, help_text="The phone of the contact detail.")
    address = models.TextField(null=True, help_text="The address of the contact detail.")
```

- Register model in service/admin.py
```
from service.models import Contact

admin.site.register(Contact)
```

- Run makemigrations & migrate
```
python manage.py makemigrations
python manage.py migrate
```

- Create service/serializer.py
```
from rest_framework import serializers

from service.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'email', 'phone', 'address')
```


- Create API views in service/views.py
```
from rest_framework import generics

from service.models import Contact
from service.serializer import ContactSerializer


class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
```

- Add monks_health_check and monks_service_meta service/views.py for starbug 
```
from django.http import JsonResponse


def monks_health_check(request):
    response = {
        "unhealthy": [],
        "healthy": [
            {
                "name": "dockerized-service-ping",
                "healthy": True,
                "type": "SELF",
                "actionable": True
            }
        ]
    }
    return JsonResponse(response)


def monks_service_meta(request):
    response = {
        "service_name": "dockerized-service",
        "service_version": "0.0.1",
        "owner": "Koalas"
    }
    return JsonResponse(response)
```


- Create service/urls.py
```
from django.urls import path

from . import views

app_label = 'dockerized_service'

urlpatterns = [
    path(r'contact_detail/', views.ContactList.as_view()),
    path(r'contact_detail/<int:pk>/', views.ContactDetail.as_view())
]

```

- Add staticfiles to project/settings.py
```
STATICFILES_DIR = [
    os.path.join(BASE_DIR, "static")
]

STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn")
```

- Add urls and staticfiles to project/urls.py
```
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from rest_framework.documentation import include_docs_urls

import service.views as views

urlpatterns = [
    path('api/v1/', include('service.urls')),
    path('monks/healthcheck', views.monks_health_check),
    path('service-metadata', views.monks_service_meta),
    path('docs/', include_docs_urls(title='Dockerized Service API Documentation')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=reverse_lazy('api-docs:docs-index'), permanent=False))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

```


### Create docker-entrypoint.sh
```
#!/bin/sh

python manage.py migrate        # Apply database migrations
python manage.py collectstatic --clear --noinput   # clearstatic files
python manage.py collectstatic --noinput  # collect static files
echo Starting Gunicorn.
exec gunicorn project.wsgi --name dockerized_service --bind :8080 --workers 3 --access-logfile /var/log/gunicorn-access.log --error-logfile /var/log/gunicorn-error.log
```


### Create Dockerfile:
```
FROM python:3-alpine

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8080

ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

### Create run_locally.sh
```
#!/usr/bin/env bash

docker build . -t dockerized_service
docker run -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_SECURITY_TOKEN=${AWS_SECURITY_TOKEN} --rm -p 8080:8080 dockerized_service:latest
```

# Step 3: Run

```
chmod 755 run_locally.sh
run_locally.sh
```

# Step 4: Access docker container
```
docker ps
docker exec -it <CONTAINER ID> sh
```