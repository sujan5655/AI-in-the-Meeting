import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()


from meetings.ai.memory import (
    get_or_create_meeting,
    get_or_create_topic,
    save_transcript,
    save_summary,
    load_meeting_memory,
)


# ==========================================
# GET EXISTING MEETING
# ==========================================

meeting = get_or_create_meeting(
    "00000000-0000-0000-0000-000000000001",
    "AI Meeting Test",
)


# ==========================================
# CREATE SECOND TOPIC
# ==========================================

topic = get_or_create_topic(
    meeting,
    "AWS Deployment",
)


# ==========================================
# SAVE SECOND TRANSCRIPT
# ==========================================

save_transcript(
    meeting,
    topic,
    "Sarah",
    "We should deploy the application using AWS.",
)


# ==========================================
# SAVE SECOND SUMMARY
# ==========================================

save_summary(
    meeting,
    topic,
    "The team discussed deploying the application using AWS.",
)


# ==========================================
# LOAD MEMORY FROM DATABASE
# ==========================================

memory = load_meeting_memory(meeting)


print("=" * 60)
print("LOADED MEETING MEMORY")
print("=" * 60)


for index, item in enumerate(
    memory,
    start=1,
):
    print(f"\nTOPIC {index}:")
    print(item["topic"])

    print("\nSUMMARIES:")

    for summary in item["summaries"]:
        print("-", summary)

    print("\nTRANSCRIPT:")
    print(item["transcript"])


print("\n")
print("=" * 60)
print("POSTGRESQL MEMORY LOAD TEST PASSED")
print("=" * 60)