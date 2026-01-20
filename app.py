import streamlit as st
import boto3
import json
import os

# ================= CONFIG =================
MODEL_ID = "amazon.nova-lite-v1:0"
REGION = "us-east-1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAT_FILE = os.path.join(BASE_DIR, "chat_history.json")

# ================= AWS CLIENT =================
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION
)

# ================= STORAGE =================
def load_history():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(messages):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

# ================= PAGE =================
st.set_page_config(
    page_title="Sugar AI Assistant",
    page_icon="🍬",
    layout="wide"
)

# ================= SMALL DELETE BUTTON STYLE =================
st.markdown("""
<style>
button[kind="secondary"] {
    padding: 0.15rem 0.35rem !important;
    font-size: 0.7rem !important;
    line-height: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# ================= SIDEBAR =================
with st.sidebar:
    st.title("🍬 Sugar AI")
    st.caption("Powered by Amazon Bedrock (Nova Lite)")
    st.divider()

    if st.button("🗑 Clear All Chats"):
        st.session_state.messages = []
        save_history([])
        st.rerun()

    st.subheader("📜 Chat History")

    if not st.session_state.messages:
        st.info("No chats yet")
    else:
        for i, msg in enumerate(st.session_state.messages):
            with st.container():
                col1, col2 = st.columns([6, 1])

                with col1:
                    role = "🧑 User" if msg["role"] == "user" else "🤖 Bot"
                    st.markdown(
                        f"**{role}**  \n{msg['content'][:45]}",
                        unsafe_allow_html=True
                    )

                with col2:
                    if st.button("✖", key=f"delete_{i}", help="Delete this message"):
                        st.session_state.messages.pop(i)
                        save_history(st.session_state.messages)
                        st.rerun()

                st.divider()

# ================= MAIN UI =================
st.markdown(
    "<h1 style='text-align:center'>🍬 Sugar AI Assistant</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:gray'>Persistent AI Chatbot</p>",
    unsafe_allow_html=True
)

# ================= CHAT DISPLAY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= INPUT =================
user_prompt = st.chat_input("Ask Sugar AI...")

if user_prompt:
    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": user_prompt}
    )
    save_history(st.session_state.messages)

    payload = {
        "messages": [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in st.session_state.messages
        ],
        "inferenceConfig": {
            "maxTokens": 400,
            "temperature": 0.6
        }
    }

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        data = json.loads(response["body"].read())
        reply = data["output"]["message"]["content"][0]["text"]

    except Exception as e:
        reply = f"⚠️ Error: {e}"

    # Save assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    save_history(st.session_state.messages)

    st.rerun()

