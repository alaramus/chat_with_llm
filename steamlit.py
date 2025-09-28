#  pip install streamlit, openai
#  To start the application, run -> streamlit run chat_with_llm.py

import streamlit as st
from openai import OpenAI


def add_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
        }}
        .stSelectbox label, .stTextInput label {{
            color: black;
        }}
        .response-text {{
            color: black;
            font-size: 16px;
        }}
        .api-key-input {{
            margin-bottom: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


add_background(
    "https://images.pexels.com/photos/4553036/pexels-photo-4553036.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&dpr=1")

st.markdown("<h1 style='color:black;'>Chat with LLM</h1>", unsafe_allow_html=True)

if 'api_key_confirmed' not in st.session_state:
    st.session_state.api_key_confirmed = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if not st.session_state.api_key_confirmed:
    st.markdown("<h1 style='color:black;'>API Key Setup</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        api_key_input = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            help="Your API key will not be stored and is only used for this session",
            placeholder="sk-...",
            key="api_key_input"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        confirm_button = st.button("Confirm", type="primary")

    if confirm_button and api_key_input:
        try:
            test_client = OpenAI(api_key=api_key_input)
            test_client.models.list()
            st.session_state.api_key = api_key_input
            st.session_state.api_key_confirmed = True
            st.success("API key confirmed successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid API key: {str(e)}")
    elif confirm_button and not api_key_input:
        st.warning("Please enter your API key first.")

    if not st.session_state.api_key_confirmed:
        st.info("You can get your API key from https://platform.openai.com/api-keys")
        st.stop()

client = OpenAI(api_key=st.session_state.api_key)

if st.button("Reset API Key"):
    st.session_state.api_key_confirmed = False
    st.session_state.api_key = ""
    st.rerun()

model = st.selectbox("Select model:", ("gpt-4o", "gpt-4", "gpt-3.5-turbo"))

user_input = st.text_input("Your request:")

languages = [
    "English",
    "Mandarin Chinese",
    "Spanish",
    "Hindi",
    "Arabic",
    "French",
    "Russian",
    "Portuguese",
    "German",
    "Japanese"
]

lang1 = st.selectbox("Select language for first response:", languages)
lang2 = st.selectbox("Select language for second response:", languages)

if st.button("Send"):
    if user_input:
        col1, col2 = st.columns(2)
        with col1:
            response1_placeholder = st.empty()
        with col2:
            response2_placeholder = st.empty()

        response1_content = ""
        response2_content = ""

        try:
            stream1 = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant. Always respond only in {lang1}, regardless of the input language."
                    },
                    {
                        "role": "user",
                        "content": f"{user_input}\n\nPlease respond strictly in {lang1}."
                    }
                ],
                stream=True,
            )

            stream2 = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant. Always respond only in {lang2}, regardless of the input language."
                    },
                    {
                        "role": "user",
                        "content": f"{user_input}\n\nPlease respond strictly in {lang2}."
                    }
                ],
                stream=True,
            )

            it1 = iter(stream1)
            it2 = iter(stream2)

            while True:
                done1 = False
                done2 = False

                try:
                    chunk1 = next(it1)
                    if chunk1.choices[0].delta.content is not None:
                        response1_content += chunk1.choices[0].delta.content
                        response1_placeholder.markdown(
                            f"<div class='response-text'><b>{lang1} response:</b><br><br>{response1_content}</div>",
                            unsafe_allow_html=True
                        )
                except StopIteration:
                    done1 = True

                try:
                    chunk2 = next(it2)
                    if chunk2.choices[0].delta.content is not None:
                        response2_content += chunk2.choices[0].delta.content
                        response2_placeholder.markdown(
                            f"<div class='response-text'><b>{lang2} response:</b><br><br>{response2_content}</div>",
                            unsafe_allow_html=True
                        )
                except StopIteration:
                    done2 = True

                if done1 and done2:
                    break

        except Exception as e:
            st.error(f"Error during API call: {str(e)}")
            st.info("Please check your API key and try again.")
    else:
        st.warning("Please enter a request.")
