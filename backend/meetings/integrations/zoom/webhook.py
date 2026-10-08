import asyncio
import hashlib
import hmac
import json
import os
import threading

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from meetings.integrations.zoom.rtms_client import connect_to_signaling


@csrf_exempt
def zoom_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    # ---------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------

    try:
        body = json.loads(request.body.decode("utf-8"))

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400,
        )

    print("=" * 60)
    print("RAW ZOOM REQUEST")
    print(json.dumps(body, indent=2))
    print("=" * 60)

    event = body.get("event")
    payload = body.get("payload", {})

    # ---------------------------------------------------------
    # ZOOM URL VALIDATION
    # ---------------------------------------------------------

    if event == "endpoint.url_validation":

        print("ZOOM URL VALIDATION REQUEST")

        plain_token = payload.get("plainToken")

        if not plain_token:
            print("Missing plainToken")

            return JsonResponse(
                {"error": "Missing plainToken"},
                status=400,
            )

        webhook_secret = os.getenv(
            "ZOOM_WEBHOOK_SECRET_TOKEN"
        )

        if not webhook_secret:
            print(
                "ZOOM_WEBHOOK_SECRET_TOKEN is not configured."
            )

            return JsonResponse(
                {
                    "error": "ZOOM_WEBHOOK_SECRET_TOKEN is not configured."
                },
                status=500,
            )

        encrypted_token = hmac.new(
            webhook_secret.encode("utf-8"),
            plain_token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        print("Zoom URL validation successful.")

        return JsonResponse(
            {
                "plainToken": plain_token,
                "encryptedToken": encrypted_token,
            },
            status=200,
        )

    # ---------------------------------------------------------
    # NORMAL ZOOM WEBHOOK
    # ---------------------------------------------------------

    print("=" * 60)
    print("ZOOM WEBHOOK RECEIVED")
    print("Event:", event)
    print(
        "Payload:",
        json.dumps(payload, indent=2),
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # RTMS STARTED
    # ---------------------------------------------------------

    if event == "meeting.rtms_started":

        meeting_uuid = payload.get(
            "meeting_uuid"
        )

        rtms_stream_id = payload.get(
            "rtms_stream_id"
        )

        server_urls = payload.get(
            "server_urls"
        )

        print("RTMS STARTED")
        print(
            "Meeting UUID:",
            meeting_uuid,
        )

        print(
            "RTMS Stream ID:",
            rtms_stream_id,
        )

        print(
            "Server URLs:",
            server_urls,
        )

        if (
            meeting_uuid
            and rtms_stream_id
            and server_urls
        ):

            print(
                "Starting RTMS signaling connection in background..."
            )

            def run_connection():

                try:
                    asyncio.run(
                        connect_to_signaling(
                            meeting_uuid=meeting_uuid,
                            rtms_stream_id=rtms_stream_id,
                            server_url=server_urls,
                        )
                    )

                except Exception as e:
                    print(
                        "RTMS connection error:",
                        e,
                    )

            threading.Thread(
                target=run_connection,
                daemon=True,
            ).start()

        else:

            print(
                "Missing RTMS connection information."
            )

    # ---------------------------------------------------------
    # RTMS STOPPED
    # ---------------------------------------------------------

    elif event == "meeting.rtms_stopped":

        meeting_uuid = payload.get(
            "meeting_uuid"
        )

        print(
            "RTMS STOPPED"
        )

        print(
            "Meeting UUID:",
            meeting_uuid,
        )

    # ---------------------------------------------------------
    # OTHER EVENTS
    # ---------------------------------------------------------

    else:

        print(
            "Unhandled Zoom event:",
            event,
        )

    return JsonResponse(
        {"status": "ok"},
        status=200,
    )