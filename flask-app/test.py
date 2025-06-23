import time

import requests

BASE_URL = "http://localhost:5000"


def log(message):
    print(f"\n========= LOG =======\n{message}\n=====================\n")


def run_pipeline(topic):
    log(f"Starting pipeline for topic: {topic}")
    response = requests.post(f"{BASE_URL}/api/run", json={"topic": topic})
    if response.status_code != 202:
        log(
            f"Failed to start pipeline. Status: {response.status_code}, Response: {response.text}"
        )
        return None
    data = response.json()
    request_id = data.get("request_id")
    log(f"Pipeline started. Session ID: {request_id}")
    return request_id


def poll_status(request_id):
    status_url = f"{BASE_URL}/api/status/{request_id}"
    while True:
        response = requests.get(status_url)
        if response.status_code != 200:
            log(
                f"Status check failed. Status: {response.status_code}, Response: {response.text}"
            )
            break

        data = response.json()
        pipeline_status = data.get("pipeline_status")
        progress = data.get("progress")
        update = data.get("update")

        log(f"Status: {pipeline_status}, Progress: {progress}%, Update: {update}")

        if pipeline_status == "completed":
            log(f"Pipeline {request_id} completed successfully!")
            break

        elif pipeline_status == "failed":
            log(f"Pipeline {request_id} failed.")
            log(f"Error: {data.get('error')}")
            break

        elif pipeline_status == "waiting_for_input":
            log(f"Pipeline {request_id} is waiting for solution choice.")
            user_prompt = data.get("update")
            log(f"Prompt: {user_prompt}")
            user_input = input("Enter the number of your chosen solution: ").strip()
            answer_url = f"{BASE_URL}/api/answer/{request_id}"
            answer_response = requests.post(answer_url, json={"answer": user_input})
            if answer_response.status_code == 200:
                log(f"Answer submitted successfully.")
            else:
                log(
                    f"Failed to submit solution. Status: {answer_response.status_code}, Response: {answer_response.text}"
                )
                break

        time.sleep(1)  # Poll every 1 second


def main():
    tests = [
        "Hi, what is your name?",
        "Hi",
        "generate an image of a cat with a hat walking on aeroplane wings",
        "generate social media posts for my new open source project called 'AgentD' which is a multi-agent system built using Google ADK",
    ]
    for topic in tests:
        log(f"Running test with topic: {topic}")
        request_id = run_pipeline(topic)
        if request_id:
            poll_status(request_id)
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
