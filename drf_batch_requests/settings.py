from django.conf import settings

# Consumer backend
REQUESTS_CONSUMER_BACKEND = getattr(
    settings, "DRF_BATCH_REQUESTS_CONSUMER_BACKEND", 'drf_batch_requests.backends.sync.SyncRequestsConsumeBackend'
)
