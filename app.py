import streamlit as st
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt setup
prompt = """
You are a YouTube video summarizer. You will take the transcript text, summarize the entire video, and provide the important points within 800  words. Please provide the summary of the text given here:
"""

# Extract video ID from different YouTube URL formats
def extract_video_id(youtube_url):
    try:
        parsed_url = urlparse(youtube_url)
        if parsed_url.netloc in ("www.youtube.com", "youtube.com"):
            query_params = parse_qs(parsed_url.query)
            return query_params["v"][0] if "v" in query_params else None
        elif parsed_url.netloc == "youtu.be":
            return parsed_url.path[1:]
        elif "shorts" in parsed_url.path:
            return parsed_url.path.split("/")[2]
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None

# Get transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("Invalid YouTube link. Please check the link format.")
            return None

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)         
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except Exception as e:
        st.error("Could not retrieve a transcript. Possible reasons:\n"
                 "- Subtitles are disabled for this video.\n"
                 "- The video is private or unavailable.\n"
                 "- The video is region-locked.\n\n"
                 f"Technical error: {e}")
        return None

# Generate summary using Google Gemini model
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt + transcript_text)                    
    return response.text

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.error("Invalid YouTube link. Please enter a valid URL.")

if st.button("Get Detailed Notes"):
    if youtube_link and video_id:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.warning("Failed to extract transcript. Try a different video.")



