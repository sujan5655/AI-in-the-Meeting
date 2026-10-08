import json
import uuid

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from meetings.ai.meeting_agent import meeting_agent
from meetings.ai.memory import (
    get_or_create_meeting,
    get_or_create_topic,
    get_meeting_notes,
    load_meeting_memory,
    save_meeting_turn,
)
from meetings.ai.transcription import transcribe_audio


class MeetingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.meeting_id = str(uuid.uuid4())
        self.previous_topic = ""

        await self.accept()

        print(
            "WebSocket connected:",
            self.meeting_id,
        )

        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection",
                    "message": "Connected to AI Meeting Assistant",
                    "meeting_id": self.meeting_id,
                }
            )
        )

    async def disconnect(self, close_code):
        print(
            "WebSocket disconnected:",
            close_code,
            "meeting:",
            getattr(
                self,
                "meeting_id",
                None,
            ),
        )

    async def receive(
        self,
        text_data=None,
        bytes_data=None,
    ):

        # ==========================================================
        # AUDIO DATA
        # ==========================================================

        if bytes_data is not None:

            print(
                "Received complete audio:",
                len(bytes_data),
                "bytes",
            )

            try:

                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "transcribing",
                            "message": "Transcribing audio...",
                        }
                    )
                )

                # Whisper/Groq runs outside the event loop
                transcript = await sync_to_async(
                    transcribe_audio,
                    thread_sensitive=False,
                )(
                    audio_bytes=bytes_data,
                    filename="meeting_audio.webm",
                )

                print(
                    "Whisper transcription:",
                    transcript,
                )

                if transcript:

                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "transcript",
                                "text": transcript,
                            }
                        )
                    )

                    await self.process_transcript(
                        transcript
                    )

                else:

                    print(
                        "Whisper returned empty transcription."
                    )

            except Exception as e:

                print(
                    "Whisper error:",
                    repr(e),
                )

                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": (
                                "Whisper transcription failed: "
                                + str(e)
                            ),
                        }
                    )
                )

            return

        # ==========================================================
        # TEXT DATA
        # ==========================================================

        if text_data is None:
            return

        try:

            data = json.loads(text_data)

            message = data.get(
                "message",
                "",
            ).strip()

            if not message:
                return

            await self.process_transcript(
                message
            )

        except Exception as e:

            print(
                "WebSocket processing error:",
                repr(e),
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": str(e),
                    }
                )
            )

    # ==============================================================
    # PROCESS TRANSCRIPT
    # ==============================================================

    async def process_transcript(
        self,
        message,
    ):

        print(
            "Processing transcript:",
            message,
        )

        await self.send(
            text_data=json.dumps(
                {
                    "type": "processing",
                    "message": "Analyzing meeting discussion...",
                }
            )
        )

        # ----------------------------------------------------------
        # 1. Get or create meeting
        # ----------------------------------------------------------

        meeting = await database_sync_to_async(
            get_or_create_meeting
        )(
            meeting_id=self.meeting_id,
            title="AI Meeting",
        )

        print(
            "Meeting:",
            meeting.id,
        )

        # ----------------------------------------------------------
        # 2. Load previous meeting memory
        # ----------------------------------------------------------

        meeting_memory = await database_sync_to_async(
            load_meeting_memory
        )(meeting)

        print(
            "Previous meeting memory:",
            meeting_memory,
        )

        # ----------------------------------------------------------
        # 3. Run AI meeting agent
        # ----------------------------------------------------------

        result = await sync_to_async(
            meeting_agent.invoke,
            thread_sensitive=False,
        )(
            {
                "meeting_id": self.meeting_id,
                "recent_transcript": message,
                "previous_topic": self.previous_topic,
                "current_topic": "",
                "topic_changed": False,
                "summary": "",
                "should_respond": False,
                "user_question": "",
                "ai_response": "",
                "meeting_memory": meeting_memory,
            }
        )

        print(
            "Meeting agent result:",
            result,
        )

        # ----------------------------------------------------------
        # 4. Get AI result
        # ----------------------------------------------------------

        current_topic = result.get(
            "current_topic",
            "",
        )

        if current_topic:
            current_topic = current_topic.strip()

        summary = result.get(
            "summary",
            "",
        )

        if summary:
            summary = summary.strip()

        ai_response = result.get(
            "ai_response",
            "",
        )

        if ai_response:
            ai_response = ai_response.strip()

        self.previous_topic = current_topic

        # ----------------------------------------------------------
        # 5. Create/get topic
        # ----------------------------------------------------------

        if current_topic:

            topic = await database_sync_to_async(
                get_or_create_topic
            )(
                meeting=meeting,
                topic_name=current_topic,
            )

        else:

            topic = await database_sync_to_async(
                get_or_create_topic
            )(
                meeting=meeting,
                topic_name="General Discussion",
            )

        print(
            "Topic:",
            topic.name,
        )

        # ----------------------------------------------------------
        # 6. SAVE TO DATABASE
        # ----------------------------------------------------------

        await database_sync_to_async(
    save_meeting_turn
)(
    meeting=meeting,
    topic=topic,
    transcript=message,
    summary=summary,
    ai_response=ai_response,
)

        print(
            "Meeting turn saved to database."
        )

        # ----------------------------------------------------------
        # 7. Reload saved notes
        # ----------------------------------------------------------

        notes = await database_sync_to_async(
            get_meeting_notes
        )(meeting)

        # ----------------------------------------------------------
        # 8. Send result to frontend
        # ----------------------------------------------------------

        await self.send(
            text_data=json.dumps(
                {
                    "type": "meeting_result",
                    "meeting_id": self.meeting_id,
                    "transcript": message,
                    "topic": current_topic,
                    "topic_changed": result.get(
                        "topic_changed",
                        False,
                    ),
                    "summary": summary,
                    "should_respond": result.get(
                        "should_respond",
                        False,
                    ),
                    "user_question": result.get(
                        "user_question",
                        "",
                    ),
                    "ai_response": ai_response,
                    "notes": notes,
                }
            )
        )

        print(
            "Meeting result sent to frontend."
        )