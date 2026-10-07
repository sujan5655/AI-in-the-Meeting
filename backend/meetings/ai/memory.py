from meetings.models import (
    Meeting,
    Topic,
    TranscriptSegment,
    MeetingNote,
)
from django.db.models.functions import Lower


def get_or_create_meeting(
    meeting_id,
    title="AI Meeting",
):
    meeting, created = Meeting.objects.get_or_create(
        id=meeting_id,
        defaults={
            "title": title,
        },
    )

    return meeting


def get_or_create_topic(
    meeting,
    topic_name,
):
    topic = Topic.objects.filter(
        meeting=meeting
    ).annotate(
        name_lower=Lower("name")
    ).filter(
        name_lower=topic_name.lower()
    ).first()

    if topic:
        return topic

    topic = Topic.objects.create(
        meeting=meeting,
        name=topic_name,
        is_current=True,
    )

    return topic


def save_transcript(
    meeting,
    topic,
    speaker,
    text,
):
    transcript = TranscriptSegment.objects.create(
        meeting=meeting,
        topic=topic,
        speaker=speaker,
        text=text,
    )

    return transcript


def save_summary(
    meeting,
    topic,
    summary,
):
    if not summary:
        return None

    note = MeetingNote.objects.create(
        meeting=meeting,
        topic=topic,
        note_type="summary",
        content=summary,
    )

    return note



def load_meeting_memory(meeting):
    memory = []

    topics = Topic.objects.filter(
    meeting=meeting
).order_by(
    "started_at"
).prefetch_related(
    "transcripts",
    "notes",
)

    for topic in topics:
        transcripts = topic.transcripts.all()
        notes = topic.notes.all()

        transcript_text = ""

        for transcript in transcripts:
            transcript_text += (
                f"{transcript.speaker}: "
                f"{transcript.text}\n"
            )

        summaries = []

        for note in notes:
            if note.note_type == "summary":
                summaries.append(note.content)

        memory.append({
            "topic": topic.name,
            "transcript": transcript_text,
            "summaries": summaries,
        })

    return memory


def get_current_topic(meeting):
    return Topic.objects.filter(
        meeting=meeting,
        is_current=True,
    ).first()


def save_meeting_turn(
    meeting,
    topic,
    transcript,
    summary,
):
    """
    Save the current meeting turn to PostgreSQL.
    """

    save_transcript(
        meeting=meeting,
        topic=topic,
        speaker="Meeting",
        text=transcript,
    )

    save_summary(
        meeting=meeting,
        topic=topic,
        summary=summary,
    )



def get_meeting_notes(meeting):
    notes = MeetingNote.objects.filter(
        meeting=meeting
    ).select_related(
        "topic"
    ).order_by(
        "created_at"
    )

    result = []

    for note in notes:
        result.append({
            "type": note.note_type,
            "content": note.content,
            "topic": (
                note.topic.name
                if note.topic
                else None
            ),
            "created_at": note.created_at.isoformat(),
        })

    return result