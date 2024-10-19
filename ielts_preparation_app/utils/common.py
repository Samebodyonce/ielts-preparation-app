import os
import random
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WRITING_TOPICS = [
    "The advantages and disadvantages of living in a big city",
    "The importance of environmental protection",
    "The role of technology in education",
    "The benefits and drawbacks of working from home",
    "The impact of social media on society"
]

SPEAKING_TOPICS = [
    "Describe a place you like to visit in your free time",
    "Talk about a hobby you enjoy",
    "Describe a person who has influenced you",
    "Talk about a memorable trip you've taken",
    "Describe your favorite book or movie"
]

def get_random_topic(topic_type):
    if topic_type == 'writing':
        return random.choice(WRITING_TOPICS)
    elif topic_type == 'speaking':
        return random.choice(SPEAKING_TOPICS)
    else:
        return "Invalid topic type"

def get_openai_response(prompt, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while accessing the OpenAI API: {e}")
        return None

def generate_audio(text, voice="alloy"):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Сохраняем аудио во временный файл
        temp_filename = f"temp_audio_{random.randint(1000, 9999)}.mp3"
        response.stream_to_file(temp_filename)
        
        return temp_filename
    except Exception as e:
        print(f"An error occurred while generating audio: {e}")
        return None
