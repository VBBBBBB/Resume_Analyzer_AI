# Resume Analyzer AI

An intelligent ATS Resume Analyzer powered by Llama-3 through Groq API, and built with Gradio.

## Features

- **Resume ATS Analyzer:** Analyzes your resume against a specific job description. Identifies missing keywords, match percentage, and recommendations.
- **Content Rephraser:** Optimize specific paragraphs or bullet points to align better with an ATS-friendly format.
- **Cover Letter Generator:** Automatically creates a tailored cover letter using the provided resume and job description.
- **Interview Questions Generator:** Retrieves 10 probable role-specific or behavioral questions based on the given job description.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VBBBBBB/Resume_Analyzer_AI.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Resume_Analyzer_AI
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your Groq API Key:
   ```bash
   # On Windows (PowerShell)
   $env:GROQ_API_KEY="your_api_key_here"
   
   # On Linux/MacOS
   export GROQ_API_KEY="your_api_key_here"
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## License

This project is open-source.