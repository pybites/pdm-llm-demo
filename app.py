import pandas as pd
import streamlit as st

from llm import data_chat

# Initialize session state to store messages
if "messages" not in st.session_state:
    st.session_state.messages = []

if "data_list" not in st.session_state:
    st.session_state.data_list = []


# Function to handle user input
def handle_input():
    user_input = st.session_state.user_input
    if user_input:
        # Get a response from the LLM
        try:
            response = data_chat(
                user_input=user_input,
                source_data=st.session_state.data_list,
                chat_history="\n".join(
                    f"{author}: {message}"
                    for author, message in st.session_state.messages
                ),
            )
            st.session_state.messages.append(("User", user_input))
            st.session_state.messages.append(("Bot", response))
        except Exception as e:
            st.error(f"An error occurred: {e}")


# Function to clear the conversation
def clear_conversation():
    st.session_state.messages = []


def main():
    st.title("Chat with your data")

    # File uploader to upload the Excel file
    uploaded_file = st.file_uploader("Choose a file to load", type=["xlsx", "csv"])

    if uploaded_file is not None:
        # Read the Excel file into a DataFrame
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        # Convert the DataFrame to a list of dictionaries
        st.session_state.data_list = df.to_dict(orient="records")

        # Display information about the data that is loaded.
        st.write(f"`{len(st.session_state.data_list)}` records loaded.")

        # Display the data
        st.dataframe(data=df)

    # Display messages in containers
    with st.container():
        for role, message in st.session_state.messages:
            if role == "User":
                chat_message = st.chat_message("user")
                chat_message.write(message)
            else:
                chat_message = st.chat_message("ai")
                chat_message.write(message)

    with st.container():
        # Chat input box
        st.chat_input("User input:", key="user_input", on_submit=handle_input)

        # Button to clear the conversation
        if st.button("Clear Conversation"):
            clear_conversation()


if __name__ == "__main__":
    main()
