import asyncio
import io
import json
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from flask import Blueprint, jsonify, request, send_file
from google.adk.events import Event

from agentd import AgentD

from .utils import error_response

api = Blueprint("api", __name__)

from datetime import datetime, timezone
from typing import Dict

SESSIONS: Dict[str, Dict] = {}

AGENTD_INSTANCE = AgentD()


def timestamp():
    return datetime.utcnow().isoformat()
    # return (
    #     datetime.now(timezone.utc)
    #     .isoformat(timespec="milliseconds")
    #     .replace("+00:00", "Z")
    # )


def validate_run_request(data):
    topic = data.get("topic")
    if not topic or not isinstance(topic, str) or not topic.strip():
        return False, "Field 'topic' must be a non-empty string."
    return True, ""


async def real_pipeline_worker(request_id, topic):
    # 1. create user and session
    # 2. run

    user_id = AGENTD_INSTANCE.generate_user_id()
    new_session = await AGENTD_INSTANCE.new_sesion(user_id)

    SESSIONS[request_id].update(
        {
            "pipeline_status": "running",
            "status": "In Progress",
            "update_timestamp": timestamp(),
            "update": "Pipeline started.",
            "_session_id": new_session.id,
            "_user_id": user_id,
            "progress": 0,
        }
    )

    def update_session_status(**kwargs):
        kwargs.setdefault("update_timestamp", timestamp())
        append_agent_update = kwargs.pop("apppend_agent_update", None)
        if append_agent_update:
            agent_prev_updates = SESSIONS[request_id].get("agent_updates", [])
            agent_prev_updates.append(append_agent_update)
            SESSIONS[request_id]["agent_updates"] = agent_prev_updates
        SESSIONS[request_id].update(**kwargs)

    def callback(event: Event, eventType: AgentD.EventType):
        if eventType == AgentD.EventType.TEXT_MESSAGE:
            message = "\n".join(event)
            update_session_status(
                status="Generating response",
                update=message,
                apppend_agent_update=message,
            )

        elif eventType == AgentD.EventType.TOOL_CALL_REQUEST:
            tool_calls = AGENTD_INSTANCE.parse_tool_call_event(event)
            message = "Agent is executing tools:\n" "\n".join(
                f"- {tool_call['name']}"  #: {tool_call['args']}"
                for tool_call in tool_calls
            )
            update_session_status(
                status="Executing tools",
                update=message,
                apppend_agent_update=message,
            )

        elif eventType == AgentD.EventType.TOOL_RESULT:
            tool_results = AGENTD_INSTANCE.parse_tool_result_event(event)
            message = ""
            for tool_result in tool_results:
                message += f"Tool `{tool_result['name']}` execution completed\n"

            update_session_status(
                status="Processing tool results",
                update=message,
                apppend_agent_update=message,
            )

        elif eventType == AgentD.EventType.CONTROL_SIGNAL:
            # something went wrong
            update_session_status(
                status="Failed",
                pipeline_status="failed",
                error="An error occurred during processing.",
                update="An error occurred during processing.",
                end_timestamp=timestamp(),
            )

        elif eventType == AgentD.EventType.FILE_URL:
            file_url = event.get("url")
            description = event.get("description", "")
            name = event.get("name", "file")
            filetype = event.get("filetype", "txt")

            update_session_status(
                status="New file created",
                update=f"File `{name}` ({filetype}) created: {file_url}",
                apppend_agent_update=f"File created:\n[Download {name}]({file_url}) : {description}",
            )

        elif eventType == AgentD.EventType.PROGRESS_UPDATE:
            progress: int = int(event)
            print(f"======> Progress update: {progress}%")
            update_session_status(
                progress=progress,
            )

        elif eventType == AgentD.EventType.USER_INPUT_REQUEST:
            user_input_specs: dict = event
            message = (
                # f"Agent '{user_input_specs.get('agent_name', 'Unknown')}' is requesting your input:\n"
                f"{user_input_specs.get('description', '')}\n"
            )
            update_session_status(
                pipeline_status="waiting_for_input",
                status="Waiting for input",
                update=message,
                user_input_specs=user_input_specs,
            )

    try:

        async def loop(message: str):
            await AGENTD_INSTANCE.continue_session(
                message=message,
                session=new_session,
                callback=callback,
            )

            while SESSIONS[request_id]["pipeline_status"] == "waiting_for_input":
                if SESSIONS[request_id].get("user_input"):
                    SESSIONS[request_id]["pipeline_status"] = "running"
                    SESSIONS[request_id]["status"] = "In Progress"
                    SESSIONS[request_id]["update"] = "Processing your answer"
                    SESSIONS[request_id]["progress"] = 72
                    user_input = SESSIONS[request_id]["user_input"]
                    SESSIONS[request_id]["user_input"] = None
                    await loop(user_input)
                    break
                continue

        await loop(f"{topic}")

        if not SESSIONS[request_id]["pipeline_status"] == "failed":
            update_session_status(
                pipeline_status="completed",
                status="Completed",
                end_timestamp=timestamp(),
            )
    except Exception as e:
        SESSIONS[request_id].update(
            {
                "pipeline_status": "failed",
                "error": str(e),
                "update": "An error occurred during processing.",
                "end_timestamp": timestamp(),
            }
        )
        return


def thread_worker(request_id, topic):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(real_pipeline_worker(request_id, topic))
    loop.close()


@api.route("/run", methods=["POST"])
def run_pipeline():
    data = request.get_json()
    if not data:
        return error_response("Invalid or missing JSON body.", 400)

    valid, message = validate_run_request(data)
    if not valid:
        return error_response(message, 400)

    topic = data["topic"]

    request_id = str(uuid.uuid4())

    SESSIONS[request_id] = {
        "topic": topic,
        "pipeline_status": "queued",
        "status": "In Progress",
        "start_timestamp": timestamp(),
        "end_timestamp": None,
        "update_timestamp": timestamp(),
        "update": None,
        "agent_updates": [],
        "error": None,
        "progress": 0,
    }

    threading.Thread(target=thread_worker, args=(request_id, topic)).start()

    response = {
        "status": "success",
        "message": f"Pipeline started.",
        "request_id": request_id,
    }
    return jsonify(response), 202


@api.route("/answer/<request_id>", methods=["POST"])
def provide_solution_choice(request_id):
    session = SESSIONS.get(request_id)
    if not session:
        return error_response("Session not found.", 404)

    if session["pipeline_status"] != "waiting_for_input":
        return error_response("This session is not expecting input at the moment.", 400)

    data = request.get_json()
    answer = data.get("answer")

    SESSIONS[request_id]["user_input"] = answer

    return (
        jsonify(
            {
                "status": "success",
                "message": "Answer is being processed.",
            }
        ),
        200,
    )


@api.route("/status/<request_id>", methods=["GET"])
def get_request_status(request_id):
    session = SESSIONS.get(request_id)
    if not session:
        return error_response("Session not found.", 404)

    return (
        jsonify(
            {
                "status": "success",
                "request_id": request_id,
                "pipeline_status": session["pipeline_status"],
                "updated_at": session["update_timestamp"],
                "progress": session["progress"],
                "update": session["update"],
                "agent_updates": session.get("agent_updates", []),
                "error": session.get("error"),
                "started_at": session["start_timestamp"],
                "ended_at": session["end_timestamp"],
            }
        ),
        200,
    )


@api.route("/api-status", methods=["GET"])
def get_status():
    piplines_status = {
        "queued_pipelines": [],
        "running_pipelines": [],
        "completed_pipelines": [],
        "failed_pipelines": [],
        "waiting_for_input_pipelines": [],
    }

    if not SESSIONS:
        return (
            jsonify(
                {
                    "status": "success",
                    "data": piplines_status,
                }
            ),
            200,
        )

    for request_id, session in SESSIONS.items():
        if session["pipeline_status"] == "queued":
            piplines_status["queued_pipelines"].append(request_id)
        if session["pipeline_status"] == "running":
            piplines_status["running_pipelines"].append(request_id)
        elif session["pipeline_status"] == "completed":
            piplines_status["completed_pipelines"].append(request_id)
        elif session["pipeline_status"] == "failed":
            piplines_status["failed_pipelines"].append(request_id)
        elif session["pipeline_status"] == "waiting_for_input":
            piplines_status["waiting_for_input_pipelines"].append(request_id)

    response = {
        "status": "success",
        "data": piplines_status,
    }
    return jsonify(response), 200


@api.route("/health", methods=["GET"])
@api.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200
