import google.generativeai as genai
import PyPDF2 as pdf
import json   #output in JSON format
import os

def configure_genai(api_key):
    """
    Configures the Google Generative AI client with the provided API key.
    """
    try:
        if not api_key:
            raise ValueError("API key must be provided.")
        genai.configure(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to configure Google Generative AI client:  {str(e)}")


#read PDF file and extract text and match it with JD
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.
    """
    try:
        if pdf_file is None:
            raise ValueError("No file uploaded.")

        reader = pdf.PdfReader(pdf_file)
        if (len(reader.pages) == 0):
            raise Exception("PDF file is empty or has no readable pages.")
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        if not text:
            raise Exception("No text found in the PDF file.")
            
        return " ".join(text)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")   
    

#Define function to prepare the prompt for the model
def prepare_prompt(job_description, resume_text):
    """
    Prepares the prompt for the model using the job description and resume text.
    """
    try:
        if not job_description or not resume_text:
            raise ValueError("Job description and resume text must be provided.")
        
        prompt_template="""
        Act as an expert ATS(Applicant Tracking System) specialist with deep expertise in:
        -Technical skills
        - Software engineering
        - Data science
        - Data Analysis
        -Big Data Engineering
        Evaluate the following resume against the job description. Consider that the job market is
        highly competitive. Provide a detailed feedback for resume improvement.
                
        Job Description: {job_description}

        Resume :{resume_text}

        Provide a response in the following JSON format only:
        {{
            "JD Match_score": "Percentage between 0-100",
            "Missing Keywords": ["keyword1", "keyword2", ...],
            "Profile Summary": "Detailed analysis of the match and specific improvement suggestions"
        }}

        """
        return prompt_template.format(
            job_description=job_description.strip(),  # Ensure no leading/trailing whitespace
            resume_text=resume_text.strip()  # Ensure no leading/trailing whitespace
        )
    except Exception as e:
        raise Exception(f"Failed to prepare prompt: {str(e)}")  
    
#Define function to call the model and get the response
def get_gemini_response(prompt):
    """
    Calls the Google Generative AI model with the prepared prompt and returns the response.
    """
    try:
        if not prompt:
            raise ValueError("Prompt must be provided.")
        # Ensure the model is configured before making the call
        model=genai.GenerativeModel(model_name="gemini-1.5-flash")        
        response = model.generate_content(prompt)
        if not response or not response.text:
            raise Exception("No response received from the model.")
        # Try to parse the response as JSON
        try:
            response_json = json.loads(response.text)
            #validate required fields
            required_fields = ["JD Match_score", "Missing Keywords", "Profile Summary"]
            for field in required_fields:
                if field not in response_json:
                    raise ValueError(f"Response JSON is missing required field: {field}")
            
            return response.text
        
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON-like content
            import re
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response.text,re.DOTALL)
            if match:
                return match.group()     
            else:
                raise Exception("could not extract valid JSON response")
            
    except Exception as e:
        raise Exception(f"Failed to get response from Google Generative AI: {str(e)}")  