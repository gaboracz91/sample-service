import os
import signal
import subprocess

from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from prometheus_client import Gauge
from rest_framework.viewsets import ModelViewSet

from service.models import Consumer, Healthcheck, MeasurementType, Task
from service.serializer import ConsumerSerializer, MeasurementTypeSerializer, TaskSerializer

healthy_gauge = Gauge('healthy', 'Service health check', ['name', 'actionable', 'dependentOn', 'type'])
healthy_gauge.labels(
    **{'name': 'sample-service', 'actionable': 'true', 'type': 'SELF', 'dependentOn': ''}).set(0)


class ConsumerViewSet(ModelViewSet):
    serializer_class = ConsumerSerializer
    queryset = Consumer.objects.all()


class MeasurementTypeViewSet(ModelViewSet):
    serializer_class = MeasurementTypeSerializer
    queryset = MeasurementType.objects.all()


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filter_fields = ('measurement_type',)


def monks_health_check(request):
    response = {
        "unhealthy": [],
        "healthy": [
            {
                "name": "sample-service-ping",
                "healthy": True,
                "type": "SELF",
                "actionable": True
            }
        ]
    }
    return JsonResponse(response)


def monks_service_meta(request):
    response = {
        "service_name": "sample-service",
        "service_version": "0.0.1",
        "owner": "Team"
    }
    return JsonResponse(response)


def restart_stale_processes():
    for healthcheck in Healthcheck.objects.all():
        if healthcheck.is_stale():
            try:
                os.kill(healthcheck.pid, signal.SIGTERM)
            except ProcessLookupError:
                print('PID {} for {} does not exist'.format(healthcheck.pid, healthcheck.service_name))

            healthcheck.delete()
            subprocess.Popen(['python', 'manage.py', healthcheck.service_name])


@csrf_exempt
def local_healthcheck(request):
    service_name = request.POST['service_name']
    pid = request.POST['pid']
    healthcheck, created = Healthcheck.objects.get_or_create(service_name=service_name, defaults={'pid': pid})
    if not created:
        healthcheck.last_ping = now()
        healthcheck.save()
    return JsonResponse({"success": "true"})
