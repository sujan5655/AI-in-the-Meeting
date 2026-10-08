from rest_framework import serializers

from meetings.models import (
    Meeting,
    Topic,
    TranscriptSegment,
    MeetingNote,
)


class TranscriptSegmentSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = TranscriptSegment
        fields = [
            "id",
            "speaker",
            "text",
            "timestamp",
            "topic",
        ]


class MeetingNoteSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = MeetingNote
        fields = [
            "id",
            "note_type",
            "content",
            "created_at",
            "topic",
        ]


class TopicSerializer(
    serializers.ModelSerializer
):
    transcripts = TranscriptSegmentSerializer(
        many=True,
        read_only=True,
    )

    notes = MeetingNoteSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Topic
        fields = [
            "id",
            "name",
            "summary",
            "started_at",
            "ended_at",
            "is_current",
            "transcripts",
            "notes",
        ]


class MeetingSerializer(
    serializers.ModelSerializer
):
    topics = TopicSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "created_at",
            "is_active",
            "topics",
        ]