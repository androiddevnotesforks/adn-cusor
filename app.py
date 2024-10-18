import streamlit as st
import requests
import json
import os
import base64
from openai import OpenAI

# Move API setup to a function
def setup_api():
    st.sidebar.header("API Settings")
    api_url = st.sidebar.text_input("API Base URL", "https://api.x.ai/v1/chat/completions")
    api_key = st.sidebar.text_input("API Key", "xai-no4Zu9rW2jgq5BrdTVC1Im7kKNGGaOA71MS40gT8QdqATaWkFp0fA1JgggDhmyjJEnMdySFFpLnmEiiB", type="password")
    return api_url, api_key

# Update generate_response function
def generate_response_stream(prompt, api_url, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "stream": True
    }

    with requests.post(api_url, headers=headers, json=data, stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line.strip() == '[DONE]':
                            break
                        try:
                            json_object = json.loads(line)
                            content = json_object['choices'][0]['delta'].get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        else:
            yield f"Error: {response.status_code}, {response.text}"

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

def generate_vision_response(image, prompt, api_url, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url=api_url.rsplit('/', 1)[0],  # Remove '/chat/completions' from the end
    )

    base64_image = encode_image(image)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        },
    ]

    stream = client.chat.completions.create(
        model="grok-2v-mini",
        messages=messages,
        stream=True,
        temperature=0.01,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

# Streamlit UI
st.title("X.AI Grok-beta Chat API Demo (Streaming)")

# Setup API in sidebar
api_url, api_key = setup_api()

# Add a radio button to choose between text and image input
input_type = st.radio("Choose input type:", ("Text", "Image"))

if input_type == "Text":
    user_input = st.text_area("Enter your message:", height=100)

    if st.button("Send"):
        if user_input and api_url and api_key:
            response_container = st.empty()
            full_response = ""
            for chunk in generate_response_stream(user_input, api_url, api_key):
                full_response += chunk
                response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)
        elif not user_input:
            st.warning("Please enter a message.")
        else:
            st.warning("Please provide both API URL and API Key in the sidebar.")

else:  # Image input
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image.", use_column_width=True)
        user_input = st.text_area("Ask a question about the image:", height=100)

        if st.button("Analyze"):
            if user_input and api_url and api_key:
                response_container = st.empty()
                full_response = ""
                for chunk in generate_vision_response(uploaded_file, user_input, api_url, api_key):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
            elif not user_input:
                st.warning("Please ask a question about the image.")
            else:
                st.warning("Please provide both API URL and API Key in the sidebar.")

# Add a sidebar with some information
st.sidebar.header("About")
st.sidebar.info("This is a demo of the X.AI Grok-beta Chat API using Streamlit with streaming responses and vision capabilities.")
