from django.urls import path

from meetings.views import (
    MeetingHistoryAPIView,
    MeetingDetailAPIView,
)
from meetings.integrations.zoom.webhook import zoom_webhook


urlpatterns = [
    path(
        "",
        MeetingHistoryAPIView.as_view(),
        name="meeting-history",
    ),

    path(
        "<uuid:id>/",
        MeetingDetailAPIView.as_view(),
        name="meeting-detail",
    ),

    path(
        "zoom/webhook/",
        zoom_webhook,
        name="zoom-webhook",
    ),
]