import os
import json
import hmac
import hashlib
import asyncio

import websockets


def generate_signature(
    meeting_uuid,
    rtms_stream_id,
):
    client_id = os.getenv(
        "ZOOM_CLIENT_ID"
    )

    client_secret = os.getenv(
        "ZOOM_CLIENT_SECRET"
    )

    if not client_id:
        raise ValueError(
            "ZOOM_CLIENT_ID is not configured"
        )

    if not client_secret:
        raise ValueError(
            "ZOOM_CLIENT_SECRET is not configured"
        )

    message = (
        f"{client_id},"
        f"{meeting_uuid},"
        f"{rtms_stream_id}"
    )

    signature = hmac.new(
        client_secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    return signature


async def connect_to_signaling(
    meeting_uuid,
    rtms_stream_id,
    server_url,
):
    print(
        "Connecting to Zoom RTMS signaling..."
    )

    print(
        "Meeting UUID:",
        meeting_uuid,
    )

    print(
        "RTMS Stream ID:",
        rtms_stream_id,
    )

    print(
        "Server URL:",
        server_url,
    )

    signature = generate_signature(
        meeting_uuid,
        rtms_stream_id,
    )

    handshake = {
        "msg_type": 1,
        "protocol_version": 1,
        "sequence": 1,
        "meeting_uuid": meeting_uuid,
        "rtms_stream_id": rtms_stream_id,
        "signature": signature,
        "buffer_data": False,
    }

    async with websockets.connect(
        server_url
    ) as websocket:

        print(
            "RTMS signaling WebSocket connected."
        )

        print(
            "Sending RTMS handshake..."
        )

        await websocket.send(
            json.dumps(handshake)
        )

        async for message in websocket:

            print(
                "RTMS signaling message:",
                message,
            )

            data = json.loads(
                message
            )

            msg_type = data.get(
                "msg_type"
            )

            # =====================================
            # SIGNALING HANDSHAKE RESPONSE
            # =====================================

            if msg_type == 2:

                status_code = data.get(
                    "status_code"
                )

                if status_code == 0:

                    print(
                        "RTMS signaling handshake successful!"
                    )

                    media_server = data.get(
                        "media_server",
                        {},
                    )

                    server_urls = (
                        media_server.get(
                            "server_urls",
                            {},
                        )
                    )

                    print(
                        "Available media servers:",
                        server_urls,
                    )

                else:

                    print(
                        "RTMS handshake failed."
                    )

                    print(
                        "Status:",
                        status_code,
                    )

                    print(
                        "Reason:",
                        data.get("reason"),
                    )

            # =====================================
            # KEEP ALIVE
            # =====================================

            elif msg_type == 12:

                timestamp = data.get(
                    "timestamp"
                )

                print(
                    "RTMS keep-alive received."
                )

                await websocket.send(
                    json.dumps({
                        "msg_type": 13,
                        "timestamp": timestamp,
                    })
                )

                print(
                    "RTMS keep-alive response sent."
                )