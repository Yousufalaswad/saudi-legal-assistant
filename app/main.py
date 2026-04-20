import streamlit as st
import os
from dotenv import load_dotenv
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pipeline import load_vectorstore, ask_question

load_dotenv()

st.set_page_config(
    page_title="Saudi Legal Assistant | المساعد القانوني السعودي",
    page_icon="⚖️",
    layout="centered"
)

# CSS for RTL Arabic support
st.markdown("""
<style>
.arabic-text {
    direction: rtl;
    text-align: right;
    font-family: 'Arial', sans-serif;
    font-size: 16px;
}
.disclaimer {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 10px;
    margin-top: 10px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("⚖️ Saudi Legal Assistant")
st.markdown("**المساعد القانوني السعودي**")
st.caption("Bilingual legal information for labor, rental, traffic & enforcement matters | معلومات قانونية ثنائية اللغة")

# Disclaimer banner
st.warning("⚠️ This tool provides legal **information** only, not legal advice. Always consult a licensed lawyer for your specific case. | هذه الأداة تقدم **معلومات** قانونية فقط وليست استشارة قانونية.")

# API keys
groq_api_key = os.getenv("GROQ_API_KEY", "")
cohere_api_key = os.getenv("COHERE_API_KEY", "")

if not groq_api_key or not cohere_api_key:
    st.error("Missing API keys. Make sure GROQ_API_KEY and COHERE_API_KEY are set in .env")
    st.stop()

# Load vectorstore once and cache it
@st.cache_resource
def get_vectorstore():
    with st.spinner("Loading legal knowledge base..."):
        return load_vectorstore(cohere_api_key)

vectorstore = get_vectorstore()

# Sidebar with example questions
with st.sidebar:
    st.header("📋 Example Questions")
    st.markdown("**Labor Law | نظام العمل**")
    if st.button("How is end-of-service calculated?"):
        st.session_state["prefill"] = "How is end-of-service benefit calculated in Saudi Arabia?"
    if st.button("كيف أحسب مكافأة نهاية الخدمة؟"):
        st.session_state["prefill"] = "كيف أحسب مكافأة نهاية الخدمة في السعودية؟"

    st.markdown("**Rental | الإيجار**")
    if st.button("Can my landlord evict me without notice?"):
        st.session_state["prefill"] = "Can my landlord evict me without notice in Saudi Arabia?"
    if st.button("هل يحق للمالك طردي بدون إشعار؟"):
        st.session_state["prefill"] = "هل يحق لصاحب العقار طردي بدون إشعار مسبق؟"

    st.markdown("**Traffic | المرور**")
    if st.button("How do I dispute a traffic fine?"):
        st.session_state["prefill"] = "How do I dispute a traffic fine in Saudi Arabia?"

    st.markdown("**Enforcement | التنفيذ**")
    if st.button("How to collect unpaid salary?"):
        st.session_state["prefill"] = "How do I collect unpaid salary from my employer in Saudi Arabia?"
    if st.button("كيف أستوفي راتبي المتأخر؟"):
        st.session_state["prefill"] = "كيف أستوفي راتبي المتأخر من صاحب العمل؟"

    st.divider()
    st.caption("Powered by Saudi law database + Groq AI")
    st.caption("Built by Yousuf Alaswad | FIU Computer Engineering")

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle prefill from sidebar buttons
prefill = st.session_state.pop("prefill", None)

# Chat input
question = st.chat_input("Ask a legal question in English or Arabic... | اسأل سؤالاً قانونياً بالعربية أو الإنجليزية")

if prefill:
    question = prefill

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching legal database... | جاري البحث في قاعدة البيانات القانونية..."):
            try:
                answer, sources, language = ask_question(question, vectorstore, groq_api_key)

                st.markdown(answer)

                if sources:
                    with st.expander("📚 Sources | المصادر"):
                        for source in sources:
                            st.caption(f"• {source}")

            except Exception as e:
                answer = f"Sorry, an error occurred: {str(e)}"
                st.error(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})