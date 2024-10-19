import json
import os
from .common import get_openai_response, client, get_random_topic

def transcribe_audio(audio_file):
    try:
        temp_filename = "temp_audio.wav"
        audio_file.save(temp_filename)
        
        with open(temp_filename, "rb") as file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=file
            )
        
        os.remove(temp_filename)
        return transcript.text
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

def analyze_speech(audio_file, topic):
    transcript = transcribe_audio(audio_file)
    if not transcript:
        return None

    prompt = f"""Analyze the following IELTS Speaking response based on the given topic and provide feedback. Response format:

{{
  "scores": {{
    "fluency": number from 0 to 9,
    "pronunciation": number from 0 to 9,
    "vocabulary": number from 0 to 9,
    "grammar": number from 0 to 9,
    "overall": number from 0 to 9
  }},
  "feedback": [
    {{
      "aspect": "aspect of speech (e.g., pronunciation, grammar)",
      "comment": "specific feedback"
    }}
  ],
  "recommendations": "String with general recommendations",
  "topic_relevance": "Comment on how well the response addresses the given topic"
}}

Topic: {topic}

Transcript:
'''
{transcript}
'''
"""
    result = get_openai_response(prompt)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("Error parsing the API response.")
            return None
    return None

def get_speaking_topic(custom_topic=None):
    if custom_topic:
        return custom_topic
    return get_random_topic('speaking')
