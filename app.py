import streamlit as st
import json     
import os
from dotenv import load_dotenv
from utils import configure_genai, extract_text_from_pdf, prepare_prompt, get_gemini_response



#Initialize session state
def initialize_session_state():
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
def main():
    #Load environment variables
  
    load_dotenv()
    # Initialize session state
    initialize_session_state()

    #Configure Generative AI 
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
        return
    try:
        configure_genai(api_key)
        st.success("Google Generative AI client configured successfully!")
    except Exception as e:
        st.error(f"Error configuring Google Generative AI client: {str(e)}")
        return
    
    
    #Sidebar
    with st.sidebar:
        st.title("Resume Analyzer")
        st.subheader("About")
        st.write("""
        This smart ATS helps you:
        - Evaluate resume-job description match
        - Identify missing keywords
        - Get personalized improvement suggestions
        """)

    #Main content
    st.title("Smart ATS Resume Analyzer")
    st.subheader("Optimize your resume for ATS")

    #Input selection with validation
    jd = st.text_area("Job Description", placeholder="Paste the job description here...",
                       help="Enter the complete job description for accurate analysis.")
    
    uploaded_file = st.file_uploader("Resume (PDF)", type=["pdf"],
                                     help="Upload your resume in PDF format.")
    
    # Process button with loading state
    if st.button("Analyze Resume",disabled=st.session_state.processing):
        if not jd:
            st.warning("Please provide a job description")
            return
        if not uploaded_file:
            st.warning("Please upload a resume in PDF Format")
            return
        
        st.session_state.processing = True
        st.info("Processing... Please wait.")
        
        try:
            with st.spinner("Analyzing your resume..."):
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                
                # Prepare the prompt
                input_prompt = prepare_prompt(jd, resume_text)
                
                # Get response from Google Generative AI
                response = get_gemini_response(input_prompt)
                response_json = json.loads(response)
                
                # Display the response
                st.success("Analysis Complete!")
               
                # Match Percentage
                match_percentage = response_json.get("JD Match_score", "N/A")
                st.metric("JD Match Score", match_percentage)

                # Missing Keywords
                st.subheader("Missing Keywords")
                missing_keywords = response_json.get("Missing Keywords", [])    
                if missing_keywords:
                    st.write(", ".join(missing_keywords))
                else:
                    st.write("No missing keywords identified.") 

                # Profile Summary
                st.subheader("Profile Summary") 
                st.write(response_json.get("Profile Summary", "No profile summary available ."))  
        
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
        
        finally:
            st.session_state.processing = False


if __name__ == "__main__":
    main()