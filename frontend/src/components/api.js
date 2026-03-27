import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL });

/**
 * Analyze a resume file with or without a job description.
 * @param {File} file - PDF or DOCX resume
 * @param {string} jobDescription
 * @param {boolean} withJobDescription
 * @param {number} temperature
 * @param {number} maxTokens
 */
export async function analyzeResume(file, jobDescription, withJobDescription, temperature, maxTokens) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('job_description', jobDescription);
  formData.append('with_job_description', withJobDescription);
  formData.append('temperature', temperature);
  formData.append('max_tokens', maxTokens);

  const res = await api.post('/analyze_resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/**
 * Rephrase text for ATS optimization.
 * @param {string} text
 * @param {number} temperature
 * @param {number} maxTokens
 */
export async function rephraseText(text, temperature, maxTokens) {
  const res = await api.post('/rephrase', {
    text,
    temperature,
    max_tokens: maxTokens,
  });
  return res.data;
}

/**
 * Generate a cover letter from a resume file and job description.
 * @param {File} file
 * @param {string} jobDescription
 * @param {number} temperature
 * @param {number} maxTokens
 */
export async function generateCoverLetter(file, jobDescription, temperature, maxTokens) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('job_description', jobDescription);
  formData.append('temperature', temperature);
  formData.append('max_tokens', maxTokens);

  const res = await api.post('/generate_cover_letter', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/**
 * Generate 10 interview questions based on a job description.
 * @param {string} jobDescription
 * @param {number} temperature
 * @param {number} maxTokens
 */
export async function generateInterviewQuestions(jobDescription, temperature, maxTokens) {
  const res = await api.post('/generate_interview_questions', {
    job_description: jobDescription,
    temperature,
    max_tokens: maxTokens,
  });
  return res.data;
}
