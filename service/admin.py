from django.contrib import admin

from service.models import Consumer, MeasurementType, Task

admin.site.register(Consumer)
admin.site.register(MeasurementType)
admin.site.register(Task)
