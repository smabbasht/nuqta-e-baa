# streamlit_gui.py
import streamlit as st
from chatbot import main

# Set page title
st.title("Chatbot Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your message:"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get chatbot response
    try:
        response = main(prompt)
        
        # Display chatbot response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add chatbot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
