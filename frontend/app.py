import streamlit as st
import requests
import os

BACKEND_URL = "https://drive-ai-backend-6nka.onrender.com"

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
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": user_input},
                timeout=120,
            )
        except requests.RequestException as exc:
            st.error(f"Backend request failed: {exc}")
            st.stop()

        if not response.ok:
            # FastAPI returns JSON for handled errors; show text fallback too.
            try:
                err = response.json()
            except ValueError:
                err = {"detail": response.text}
            st.error("Backend is waking up. Please wait 30-60 seconds and try again.")
            st.stop()

        try:
            data = response.json()
        except ValueError:
            st.error("Backend returned a non-JSON response.")
            st.code(response.text)
            st.stop()

    # Show assistant response
    with st.chat_message("assistant"):

        st.write("### Generated Query")

        if data.get("usedFallback"):
            st.info("Using fallback query generator (LLM unavailable).")

        st.code(data["query"])

        st.write("### Files Found")

        files = data.get("files", [])

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