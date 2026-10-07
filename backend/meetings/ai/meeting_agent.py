import json
import os
from typing import TypedDict
from dotenv import load_dotenv
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()
from meetings.models import Meeting
from meetings.ai.memory import (
    get_or_create_meeting,
    get_or_create_topic,
    save_meeting_turn,
)
from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
load_dotenv()

class MeetingState(TypedDict):
  meeting_id:str
  # Current conversation
  recent_transcript:str
  # Topic information
  previous_topic:str
  current_topic:str
  topic_changed:bool
  # Current discussion summary
  summary:str
   # AI interaction
  should_respond:bool
  user_question:str
  ai_response:str

  # Meeting memory
  meeting_memory: list


llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
  )

def update_meeting_memory(state: MeetingState):
    meeting = get_or_create_meeting(
        meeting_id=state["meeting_id"],
        title="AI Meeting",
    )

    topic = get_or_create_topic(
        meeting=meeting,
        topic_name=state["current_topic"],
    )

    save_meeting_turn(
        meeting=meeting,
        topic=topic,
        transcript=state["recent_transcript"],
        summary=state["summary"],
    )

    return {
        "meeting_memory": [],
    }
def detect_topic(state:MeetingState):
  prompt=f"""

You are analyzing a live meeting.
Previous topic:
{state['previous_topic']}
Recent Conversation:
{state['recent_transcript']}
Determine the current topic.
Return ONLY valid JSON:
{{
"topic_changed":true,
"topic":"short topic name",
"summary":"short summary of the discussion"
}}
If the topic has not changed, set topic_changed to false.

"""
  response=llm.invoke(prompt)
  content=response.content
  try:
    result=json.loads(content)
  except json.JSONDecodeError:
    result={
      "topic_changed":False,
      "topic":state["previous_topic"],
      "summary":"",
    }
  return {
    "topic_changed":result["topic_changed"],
    "current_topic":result["topic"],
    "summary":result["summary"]

  }


def detect_ai_question(state:MeetingState):
  prompt=f"""
You are detecting whether the AI assistant was directly asked a question during a meeting.
Conversation:
{state["recent_transcript"]}
Return ONLY valid JSON:
{{
"should_respond":true,
"question":"the question asked to the AI"
}}
If nobody asked the AI anything:
{{
"should_respond":false,
"question":""
}}
"""
  response = llm.invoke(prompt)

  try:
        result = json.loads(response.content)
  except json.JSONDecodeError:
        result = {
            "should_respond": False,
            "question": "",
        }

  return {
        "should_respond": result["should_respond"],
        "user_question": result["question"],
    }


def generate_ai_response(state: MeetingState):
    if not state["should_respond"]:
        return {
            "ai_response": ""
        }

    prompt = f"""
You are an AI participant in a professional meeting.

Current topic:
{state["current_topic"]}

Meeting context:
{state["recent_transcript"]}

The participants asked:
{state["user_question"]}

Give your own useful professional opinion.

Rules:

1. Base your answer on the meeting discussion.
2. Do not pretend to know facts that were not discussed.
3. Clearly explain your reasoning.
4. If there is not enough information, say what information is missing.
5. Keep the answer concise enough to speak during a meeting.
"""

    response = llm.invoke(prompt)

    return {
        "ai_response": response.content
    }


graph = StateGraph(MeetingState)

graph.add_node(
    "detect_topic",
    detect_topic,
)

graph.add_node(
    "update_meeting_memory",
    update_meeting_memory,
)

graph.add_node(
    "detect_ai_question",
    detect_ai_question,
)

graph.add_node(
    "generate_ai_response",
    generate_ai_response,
)


graph.add_edge(
    START,
    "detect_topic",
)

graph.add_edge(
    "detect_topic",
    "update_meeting_memory",
)

graph.add_edge(
    "update_meeting_memory",
    "detect_ai_question",
)

graph.add_edge(
    "detect_ai_question",
    "generate_ai_response",
)

graph.add_edge(
    "generate_ai_response",
    END,
)

meeting_agent = graph.compile()


if __name__ == "__main__":
    initial_state: MeetingState = {
        "meeting_id": "test-001",
        "recent_transcript": """
        We are discussing whether our AI meeting assistant should support
        automatic meeting summaries. John thinks summaries should be generated
        after every meeting. Sarah thinks users should be able to request them.
        What do you think, AI?
        """,
        "previous_topic": "AI meeting assistant",
        "current_topic": "",
        "topic_changed": False,
        "summary": "",
        "should_respond": False,
        "user_question": "",
        "ai_response": "",
    }

    result = meeting_agent.invoke(initial_state)

    print("\nCURRENT TOPIC:")
    print(result["current_topic"])

    print("\nTOPIC CHANGED:")
    print(result["topic_changed"])

    print("\nAI SHOULD RESPOND:")
    print(result["should_respond"])

    print("\nQUESTION:")
    print(result["user_question"])

    print("\nAI RESPONSE:")
    print(result["ai_response"])

