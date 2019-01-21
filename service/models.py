import uuid
from datetime import timedelta

from django.db import models
from django.utils.timezone import now


class Consumer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona_id = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    pno = models.CharField(max_length=255, null=True)


class MeasurementType(models.Model):
    name = models.CharField(max_length=255)


class Task(models.Model):
    name = models.CharField(max_length=255)
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.PROTECT)


class Healthcheck(models.Model):
    service_name = models.CharField(max_length=255)
    pid = models.IntegerField()
    last_ping = models.DateTimeField(default=now)

    def is_stale(self):
        return now() - timedelta(seconds=30) > self.last_ping
