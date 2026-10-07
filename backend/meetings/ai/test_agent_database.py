import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()


from meetings.ai.meeting_agent import meeting_agent
from meetings.ai.memory import load_meeting_memory
from meetings.models import Meeting


MEETING_ID = "11111111-1111-1111-1111-111111111111"


def run_discussion(
    transcript,
    previous_topic,
):
    state = {
        "meeting_id": MEETING_ID,

        "recent_transcript": transcript,

        "previous_topic": previous_topic,

        "current_topic": "",

        "topic_changed": False,

        "meeting_memory": [],

        "summary": "",

        "should_respond": False,

        "user_question": "",

        "ai_response": "",
    }

    return meeting_agent.invoke(state)


# ==========================================================
# DISCUSSION 1
# ==========================================================

result = run_discussion(
    """
    John: We need to decide between PostgreSQL and MongoDB.

    Sarah: I prefer MongoDB because it is flexible.

    Mike: But our application has many relationships.

    John: AI, what is your view?
    """,
    "",
)

print("=" * 60)
print("DISCUSSION 1")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nAI RESPONSE:")
print(result["ai_response"])


# ==========================================================
# DISCUSSION 2
# ==========================================================

result = run_discussion(
    """
    John: Let's move on from the database.

    Sarah: Now we need to discuss deploying the application.

    Mike: I think we should deploy everything using AWS.

    John: We could use EC2 and RDS.

    Sarah: What about the monthly infrastructure cost?

    John: AI, what is your view on AWS deployment?
    """,
    result["current_topic"],
)

print("\n")
print("=" * 60)
print("DISCUSSION 2")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nTOPIC CHANGED:")
print(result["topic_changed"])

print("\nAI RESPONSE:")
print(result["ai_response"])


# ==========================================================
# DISCUSSION 3
# ==========================================================

result = run_discussion(
    """
    Mike: Before we finish deployment, let's discuss security.

    Sarah: We need authentication and role-based permissions.

    John: We should also protect the API from unauthorized access.

    Mike: AI, what is your view on the security approach?
    """,
    result["current_topic"],
)

print("\n")
print("=" * 60)
print("DISCUSSION 3")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nTOPIC CHANGED:")
print(result["topic_changed"])

print("\nAI RESPONSE:")
print(result["ai_response"])


# ==========================================================
# LOAD MEMORY FROM POSTGRESQL
# ==========================================================

meeting = Meeting.objects.get(
    id=MEETING_ID
)

memory = load_meeting_memory(
    meeting
)


print("\n")
print("=" * 60)
print("FINAL POSTGRESQL MEMORY")
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
print("END-TO-END MEMORY TEST PASSED")
print("=" * 60)