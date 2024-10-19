import json
import random
from .common import generate_audio
import os

# This is a mock database. In a real application, you would use a proper database.
LISTENING_TESTS = [
    {
        "audio_url": "/static/audio/listening_test_1.mp3",
        "questions": [
            {
                "id": 1,
                "text": "What is the main topic of the conversation?",
                "options": ["Weather", "Travel", "Work", "Education"],
                "correct_answer": "Travel"
            },
            {
                "id": 2,
                "text": "When is the speaker planning to travel?",
                "options": ["Next week", "Next month", "Next year", "Tomorrow"],
                "correct_answer": "Next month"
            }
        ]
    }
]

def get_listening_test():
    test = random.choice(LISTENING_TESTS)
    
    for question in test['questions']:
        audio_file = generate_audio(question['text'])
        if audio_file:
            question['audio_url'] = audio_file
    
    return test

def check_answers(user_answers):
    # In a real application, you would need to know which test the user took
    test = LISTENING_TESTS[0]
    correct_answers = {q['id']: q['correct_answer'] for q in test['questions']}
    
    score = sum(1 for q_id, answer in user_answers.items() if answer == correct_answers.get(int(q_id), None))
    total_questions = len(test['questions'])
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": (score / total_questions) * 100
    }

def cleanup_audio_files(test):
    for question in test['questions']:
        if 'audio_url' in question:
            try:
                os.remove(question['audio_url'])
            except:
                pass
