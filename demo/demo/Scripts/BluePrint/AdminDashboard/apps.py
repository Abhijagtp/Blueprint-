from django.apps import AppConfig
from django.conf import settings

class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AdminDashboard'

    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            from apscheduler.schedulers.background import BackgroundScheduler
            from django_apscheduler.jobstores import DjangoJobStore
            from .task import reactivate_suspended_users

            scheduler = BackgroundScheduler()
            #scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                reactivate_suspended_users,
                trigger='interval',
                id='reactivate_users',
                days=1,
                replace_existing=True,
            )

            scheduler.start()

