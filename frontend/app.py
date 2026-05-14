import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Drive AI Agent",
    page_icon="📁",
    layout="wide"
)

# Sidebar
with st.sidebar:

    st.title("📁 Drive AI Agent")

    st.write(
        "AI-powered Google Drive search assistant."
    )

    st.divider()

    st.write("### Supported Searches")

    st.write("- PDFs")
    st.write("- Images")
    st.write("- Reports")
    st.write("- Invoices")
    st.write("- Spreadsheets")

# Main title
st.title("📁 Drive AI Agent")

# Chat input
user_input = st.chat_input(
    "Search your Google Drive files..."
)

if user_input:

    # Show user message
    st.chat_message("user").write(user_input)

    # Loading spinner
    with st.spinner("Searching Google Drive..."):

        # Send request to backend
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input}
        )

        data = response.json()

    # Show assistant response
    with st.chat_message("assistant"):

        st.write("### Generated Query")

        st.code(data["query"])

        st.write("### Files Found")

        files = data["files"]

        # Empty results
        if not files:

            st.warning("No matching files found.")

        # Show files
        else:

            for file in files:

                with st.container(border=True):

                    st.write(f"📄 {file['name']}")

                    st.write(
                        f"Type: {file['mimeType']}"
                    )

                    st.link_button(
                        "Open File",
                        file["webViewLink"]
                    )