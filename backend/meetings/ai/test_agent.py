from .meeting_agent import meeting_agent


def run_discussion(transcript, previous_topic, meeting_memory):
    state = {
        "meeting_id": "test",

        "recent_transcript": transcript,

        "previous_topic": previous_topic,

        "current_topic": "",

        "topic_changed": False,

        "meeting_memory": meeting_memory,

        "summary": "",

        "should_respond": False,

        "user_question": "",

        "ai_response": "",
    }

    return meeting_agent.invoke(state)


# ==========================================================
# DISCUSSION 1
# ==========================================================

meeting_memory = []

result = run_discussion(
    """
    John: We need to decide between PostgreSQL and MongoDB.

    Sarah: I prefer MongoDB because it is flexible.

    Mike: But our application has many relationships.

    John: AI, what is your view?
    """,
    "",
    meeting_memory,
)

meeting_memory = result["meeting_memory"]

print("=" * 60)
print("DISCUSSION 1")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nAI SHOULD RESPOND:")
print(result["should_respond"])

print("\nQUESTION:")
print(result["user_question"])

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
    meeting_memory,
)

meeting_memory = result["meeting_memory"]

print("\n")
print("=" * 60)
print("DISCUSSION 2")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nTOPIC CHANGED:")
print(result["topic_changed"])

print("\nAI SHOULD RESPOND:")
print(result["should_respond"])

print("\nQUESTION:")
print(result["user_question"])

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
    meeting_memory,
)

meeting_memory = result["meeting_memory"]

print("\n")
print("=" * 60)
print("DISCUSSION 3")
print("=" * 60)

print("\nTOPIC:")
print(result["current_topic"])

print("\nTOPIC CHANGED:")
print(result["topic_changed"])

print("\nAI SHOULD RESPOND:")
print(result["should_respond"])

print("\nQUESTION:")
print(result["user_question"])

print("\nAI RESPONSE:")
print(result["ai_response"])


# ==========================================================
# SHOW MEMORY
# ==========================================================

print("\n")
print("=" * 60)
print("MEETING MEMORY")
print("=" * 60)

for index, memory in enumerate(
    meeting_memory,
    start=1,
):
    print(f"\nTOPIC {index}:")
    print(memory["topic"])
    print("\nSUMMARIES:")

    for summary in memory["summaries"]:
       print("-", summary)

    print("\nTRANSCRIPT:")
    print(memory["transcript"])