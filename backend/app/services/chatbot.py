from app.config import *
from app.models.schemas import *
from typing import List
from io import BytesIO

def create_vector_store(conversationsessionsID: str):
    vector_store = client.vector_stores.create(name=f"Session Vector Store for: {conversationsessionsID}")
    
    return vector_store

def create_file(client, file_path):
    if file_path.startswith("http://") or file_path.startswith("https://"):
        # Download the file content from the URL
        response = requests.get(file_path)
        file_content = BytesIO(response.content)
        file_name = file_path.split("/")[-1]
        file_tuple = (file_name, file_content)
        result = client.files.create(
            file=file_tuple,
            purpose="assistants"
        )
    else:
        # Handle local file path
        with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="assistants"
            )
    print(result.id)
    return result.id

def update_vector_store(vector_store_id: str, file_paths: List[str]):
    if not file_paths:
        return
    
    # file_ids = [create_file(client, path) for path in file_paths]
    # print(f"Uploaded file IDs: {file_ids}")
    
    file_streams = [open(path, "rb") for path in file_paths]
    # print(file_streams)

    for file in file_streams:
        client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store_id, file=file
        )

def create_assistant(vector_store_id: str):
    assistant = client.beta.assistants.create(
        name="Articles Analysis Assistant",
        instructions="You are the expert in analyzing the articles. Use your knowledge to answer questions about the articles.",
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
    )

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )

    return assistant

def flow_qa(prompt, assistant_id):
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": prompt}],
    )

    handler = EventHandler()

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=(
            "You are a healthcare support assistant. Your role is to provide accurate, reliable, and well-sourced information "
            "based on the documents provided. Always verify facts before responding. If the information is not present in the documents "
            "or is inconclusive, clearly state that and recommend consulting a qualified healthcare professional."
        ),
        event_handler=handler,
    ) as stream:
        stream.until_done()

    return handler.result