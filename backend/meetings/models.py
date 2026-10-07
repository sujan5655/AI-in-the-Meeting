from django.db import models

# Create your models here.
import uuid

from django.db import models


class Meeting(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    name = models.CharField(max_length=255)

    summary = models.TextField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_current = models.BooleanField(default=False)
    class Meta:
      constraints = [
        models.UniqueConstraint(
            fields=["meeting", "name"],
            name="unique_topic_per_meeting",
        )
    ]

    def __str__(self):
        return f"{self.meeting.title} - {self.name}"
    


class TranscriptSegment(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="transcripts",
    )

    speaker = models.CharField(
        max_length=255,
        default="Unknown",
    )

    text = models.TextField()

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transcripts",
    )

    def __str__(self):
        return self.text[:50]


class MeetingNote(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    note_type = models.CharField(
        max_length=50,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes",
    )

    def __str__(self):
        return f"{self.note_type}: {self.content[:50]}"