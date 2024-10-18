import streamlit as st
import requests
import json

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

# Streamlit UI
st.title("X.AI Grok-beta Chat API Demo (Streaming)")

# Setup API in sidebar
api_url, api_key = setup_api()

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

# Add a sidebar with some information
st.sidebar.header("About")
st.sidebar.info("This is a demo of the X.AI Grok-beta Chat API using Streamlit with streaming responses.")
