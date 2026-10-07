import json
import uuid

from channels.generic.websocket import WebsocketConsumer

from meetings.ai.meeting_agent import meeting_agent
from meetings.ai.memory import (
    get_or_create_meeting,
    get_meeting_notes,
)

class MeetingConsumer(WebsocketConsumer):

    def connect(self):
        self.meeting_id = str(uuid.uuid4())

        self.previous_topic = ""

        self.accept()

        self.send(text_data=json.dumps({
            "type": "connection",
            "message": "Connected to AI Meeting Assistant",
            "meeting_id": self.meeting_id,
        }))

    def disconnect(self, close_code):
        print(
            "WebSocket disconnected:",
            close_code,
        )

    def receive(self, text_data):

        try:
            data = json.loads(text_data)

            message = data.get(
                "message",
                "",
            ).strip()

            if not message:
                return

            self.send(text_data=json.dumps({
                "type": "processing",
                "message": "Analyzing meeting discussion...",
            }))

            result = meeting_agent.invoke({
                "meeting_id": self.meeting_id,
                "recent_transcript": message,
                "previous_topic": self.previous_topic,
                "current_topic": "",
                "topic_changed": False,
                "summary": "",
                "should_respond": False,
                "user_question": "",
                "ai_response": "",
                "meeting_memory": [],
            })
            meeting = get_or_create_meeting(
    meeting_id=self.meeting_id,
    title="AI Meeting",
)

            notes = get_meeting_notes(
    meeting
)

            self.previous_topic = result[
                "current_topic"
            ]

            self.send(text_data=json.dumps({
                "type": "meeting_result",
                "meeting_id": self.meeting_id,
                "transcript": message,
                "topic": result["current_topic"],
                "topic_changed": result["topic_changed"],
                "summary": result["summary"],
                "should_respond": result["should_respond"],
                "user_question": result["user_question"],
                "ai_response": result["ai_response"],
                 "notes": notes,
            }))

        except Exception as e:

            print(
                "WebSocket processing error:",
                repr(e),
            )

            self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e),
            }))