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
def generate_response(prompt, api_url, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",  # Adjust this to match your API's model name
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(api_url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit UI
st.title("X.AI Chat API Demo")

# Setup API in sidebar
api_url, api_key = setup_api()

user_input = st.text_area("Enter your message:", height=100)

if st.button("Send"):
    if user_input and api_url and api_key:
        with st.spinner("Generating response..."):
            response = generate_response(user_input, api_url, api_key)
        st.text_area("API Response:", value=response, height=300)
    elif not user_input:
        st.warning("Please enter a message.")
    else:
        st.warning("Please provide both API URL and API Key in the sidebar.")

# Add a sidebar with some information
st.sidebar.header("About")
st.sidebar.info("This is a demo of the X.AI Chat API using Streamlit.")
