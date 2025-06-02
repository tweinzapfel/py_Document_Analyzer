import streamlit as st
from openai import OpenAI
import os
from io import BytesIO
import PyPDF2
from docx import Document
import base64

# Page configuration
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide"
)

# OpenAI client setup
headers = {
    "authorization": st.secrets["api_key"],
    "content-type": "application/json"
}

# Set your OpenAI API key (make sure it's in your environment variables or you can paste it here for testing)
client = OpenAI(api_key=st.secrets["api_key"])
# Custom CSS for better styling
css = """
<style>
.main-header {
    color: #1f77b4;
    text-align: center;
    padding: 1rem 0;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 2rem;
}
.summary-box {
    background-color: #f8f9fa;
    border-left: 4px solid #1f77b4;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}
.error-box {
    background-color: #fff5f5;
    border-left: 4px solid #e53e3e;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from uploaded Word document"""
    try:
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading Word document: {str(e)}")
        return None

def call_ai_api(text, summary_length="medium", focus_area="general"):
    """
    Make API call to AI LLM service
    Replace this function with your preferred API implementation
    """
    
    # Example API configuration - replace with your actual API details
    API_URL = "https://api.openai.com/v1/chat/completions"  # Replace with your API endpoint
    API_KEY = "your-api-key-here"  # Replace with your actual API key
    
    # Adjust prompt based on user preferences
    length_instructions = {
        "short": "Provide a brief summary in 2-3 sentences.",
        "medium": "Provide a concise summary in 1-2 paragraphs.",
        "long": "Provide a detailed summary with key points and important details."
    }
    
    focus_instructions = {
        "general": "Focus on the main themes and overall content.",
        "key_points": "Focus on extracting and listing the key points and main arguments.",
        "action_items": "Focus on identifying action items, tasks, and next steps.",
        "decisions": "Focus on decisions made, conclusions reached, and recommendations."
    }
    
    prompt = f"""
    Please summarize the following document. 
    {length_instructions.get(summary_length, length_instructions['medium'])}
    {focus_instructions.get(focus_area, focus_instructions['general'])}
    
    Document content:
    {text}
    
    Summary:
    """
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",  # Replace with your preferred model
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }
    
    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages=[
                { 
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        st.markdown("### Document Summary")
        st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)
    st.markdown("Upload a document or paste text to get an AI-powered summary")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Input Options")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Upload Document", "Paste Text"],
            index=0
        )
        
        text_content = ""
        
        if input_method == "Upload Document":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, Word (.docx), Text (.txt)"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Process different file types
                if uploaded_file.type == "application/pdf":
                    text_content = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text_content = extract_text_from_docx(uploaded_file)
                elif uploaded_file.type == "text/plain":
                    text_content = str(uploaded_file.read(), "utf-8")
                
                if text_content:
                    word_count = len(text_content.split())
                    st.info(f"📊 Extracted {word_count} words from document")
        
        else:  # Paste Text
            text_content = st.text_area(
                "Paste your text here:",
                height=300,
                placeholder="Enter the text you want to summarize..."
            )
            
            if text_content:
                word_count = len(text_content.split())
                st.info(f"📊 Text contains {word_count} words")
    
    with col2:
        st.subheader("⚙️ Summary Options")
        
        # Summary customization options
        summary_length = st.selectbox(
            "Summary Length:",
            ["short", "medium", "long"],
            index=1,
            help="Choose how detailed you want the summary to be"
        )
        
        focus_area = st.selectbox(
            "Focus Area:",
            ["general", "key_points", "action_items", "decisions"],
            index=0,
            help="Choose what aspect of the document to emphasize"
        )
        
        # Add some spacing
        st.write("")
        st.write("")
        
        # Generate summary button
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            if text_content and text_content.strip():
                if len(text_content.split()) < 10:
                    st.warning("⚠️ Text seems too short for meaningful summarization. Please provide more content.")
                else:
                    with st.spinner("🤖 AI is analyzing your document..."):
                        summary = call_ai_api(text_content, summary_length, focus_area)
                    
                    # Display results in full width
                    st.markdown("---")
                    st.subheader("📋 Summary Results")
                    
                    if summary and not summary.startswith("An error occurred"):
                        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                        
                        # Add download button for summary
                        st.download_button(
                            label="💾 Download Summary",
                            data=summary,
                            file_name="document_summary.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error(summary)
            else:
                st.warning("⚠️ Please upload a document or paste some text first!")
    
    # Footer with instructions
    st.markdown("---")
    st.markdown("""
    ### 📝 Instructions:
    1. **Upload a document** (PDF, Word, or Text file) or **paste text** directly
    2. **Choose your preferences** for summary length and focus area
    3. **Click 'Generate Summary'** to get your AI-powered summary
    4. **Download the summary** as a text file if needed

    """)


if __name__ == "__main__":
    main()
