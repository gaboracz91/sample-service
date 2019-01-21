from rest_framework.routers import DefaultRouter

from service.views import ConsumerViewSet, MeasurementTypeViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'consumers', ConsumerViewSet, base_name='consumer')
router.register(r'measurement-types', MeasurementTypeViewSet, base_name='measurement-type')
router.register(r'tasks', TaskViewSet, base_name='task')

urlpatterns = router.urls
