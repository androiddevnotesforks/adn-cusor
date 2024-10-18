import streamlit as st
import requests
import json
import os
import base64
from openai import OpenAI

# Move API setup to a function
def setup_api():
    st.sidebar.header("API Settings")
    api_url = st.sidebar.text_input("API Base URL", "https://api.x.ai/v1")
    api_key = st.sidebar.text_input("API Key", "xai-no4Zu9rW2jgq5BrdTVC1Im7kKNGGaOA71MS40gT8QdqATaWkFp0fA1JgggDhmyjJEnMdySFFpLnmEiiB", type="password")
    return api_url, api_key

# Update generate_response function
def generate_response_stream(prompt, api_url, api_key, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
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

def local_image_vision(image_file, prompt, api_url, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url=api_url,
    )

    base64_image = encode_image(image_file)

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

def web_url_vision(image_url, prompt, api_url, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url=api_url,
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
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

# New functions for REST API features

def get_api_key_info(api_url, api_key):
    url = f"{api_url}/api-key"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else f"Error: {response.status_code}, {response.text}"

def list_models(api_url, api_key):
    url = f"{api_url}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else f"Error: {response.status_code}, {response.text}"

def get_model(api_url, api_key, model_id):
    url = f"{api_url}/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else f"Error: {response.status_code}, {response.text}"

def create_embeddings(api_url, api_key, input_text, model, encoding_format):
    url = f"{api_url}/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "input": input_text,
        "model": model,
        "encoding_format": encoding_format
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json() if response.status_code == 200 else f"Error: {response.status_code}, {response.text}"

# Streamlit UI
st.title("X.AI Grok-beta API Demo")

# Setup API in sidebar
api_url, api_key = setup_api()

# Add a radio button to choose between different features
feature = st.radio("Choose a feature:", ("Text Chat", "Local Image Vision", "Web URL Image Vision", "API Key Info", "List Models", "Get Model", "Create Embeddings"))

if feature == "Text Chat":
    user_input = st.text_area("Enter your message:", height=100)

    # Add parameter controls
    st.sidebar.header("Text Chat Parameters")
    temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.sidebar.number_input("Max Tokens", 1, value=150)
    top_p = st.sidebar.slider("Top P", 0.0, 1.0, 1.0, 0.1)
    frequency_penalty = st.sidebar.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.1)
    presence_penalty = st.sidebar.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.1)

    if st.button("Send"):
        if user_input and api_url and api_key:
            response_container = st.empty()
            full_response = ""
            for chunk in generate_response_stream(user_input, f"{api_url}/chat/completions", api_key, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
                full_response += chunk
                response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)
        elif not user_input:
            st.warning("Please enter a message.")
        else:
            st.warning("Please provide both API URL and API Key in the sidebar.")

elif feature == "Local Image Vision":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image.", use_column_width=True)
        user_input = st.text_area("Ask a question about the image:", height=100)

        if st.button("Analyze"):
            if user_input and api_url and api_key:
                response_container = st.empty()
                full_response = ""
                for chunk in local_image_vision(uploaded_file, user_input, api_url, api_key):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
            elif not user_input:
                st.warning("Please ask a question about the image.")
            else:
                st.warning("Please provide both API URL and API Key in the sidebar.")

elif feature == "Web URL Image Vision":
    image_url = st.text_input("Enter the URL of the image:")
    if image_url:
        st.image(image_url, caption="Image from URL.", use_column_width=True)
        user_input = st.text_area("Ask a question about the image:", height=100)

        if st.button("Analyze"):
            if user_input and api_url and api_key:
                response_container = st.empty()
                full_response = ""
                for chunk in web_url_vision(image_url, user_input, api_url, api_key):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
            elif not user_input:
                st.warning("Please ask a question about the image.")
            else:
                st.warning("Please provide both API URL and API Key in the sidebar.")

elif feature == "API Key Info":
    if st.button("Get API Key Info"):
        if api_url and api_key:
            info = get_api_key_info(api_url, api_key)
            st.json(info)
        else:
            st.warning("Please provide both API URL and API Key in the sidebar.")

elif feature == "List Models":
    if st.button("List Models"):
        if api_url and api_key:
            models = list_models(api_url, api_key)
            st.json(models)
        else:
            st.warning("Please provide both API URL and API Key in the sidebar.")

elif feature == "Get Model":
    model_id = st.text_input("Enter Model ID:")
    if st.button("Get Model Info"):
        if api_url and api_key and model_id:
            model_info = get_model(api_url, api_key, model_id)
            st.json(model_info)
        else:
            st.warning("Please provide API URL, API Key, and Model ID.")

elif feature == "Create Embeddings":
    input_text = st.text_area("Enter text for embedding:")
    
    # Add parameter controls
    st.sidebar.header("Embedding Parameters")
    model = st.sidebar.text_input("Enter embedding model name:", value="v1")
    encoding_format = st.sidebar.selectbox("Encoding Format", ["float", "base64"])

    if st.button("Create Embeddings"):
        if api_url and api_key and input_text:
            embeddings = create_embeddings(api_url, api_key, [input_text], model, encoding_format)
            st.json(embeddings)
        else:
            st.warning("Please provide API URL, API Key, and input text.")

# Add a sidebar with some information
st.sidebar.header("About")
st.sidebar.info("This is a demo of the X.AI Grok-beta API using Streamlit with various features including chat, image vision, and REST API capabilities.")
