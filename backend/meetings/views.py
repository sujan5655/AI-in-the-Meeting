from django.shortcuts import render

# Create your views here.

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from meetings.models import Meeting
from meetings.serializers import MeetingSerializer


class MeetingHistoryAPIView(
    ListAPIView
):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return (
            Meeting.objects
            .prefetch_related(
                "topics__transcripts",
                "topics__notes",
            )
            .order_by("-created_at")
        )


class MeetingDetailAPIView(
    RetrieveAPIView
):
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def get_queryset(self):
        return (
            Meeting.objects
            .prefetch_related(
                "topics__transcripts",
                "topics__notes",
            )
        )