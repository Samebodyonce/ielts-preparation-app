import json
import random

# This is a mock database. In a real application, you would use a proper database.
READING_TESTS = [
    {
        "passage": "The Industrial Revolution was a period of major industrialization and innovation during the late 18th and early 19th century. The Industrial Revolution began in Great Britain and quickly spread throughout the world. This time period saw the mechanization of agriculture and textile manufacturing and a revolution in power, including steam ships and railroads, that affected social, cultural and economic conditions.",
        "questions": [
            {
                "id": 1,
                "text": "When did the Industrial Revolution begin?",
                "options": ["Late 17th century", "Late 18th century", "Early 19th century", "Mid 19th century"],
                "correct_answer": "Late 18th century"
            },
            {
                "id": 2,
                "text": "Where did the Industrial Revolution start?",
                "options": ["United States", "France", "Germany", "Great Britain"],
                "correct_answer": "Great Britain"
            }
        ]
    }
]

def get_reading_test():
    # In a real application, you would select a random test or based on user progress
    return random.choice(READING_TESTS)

def check_answers(user_answers):
    # In a real application, you would need to know which test the user took
    test = READING_TESTS[0]
    correct_answers = {q['id']: q['correct_answer'] for q in test['questions']}
    
    score = sum(1 for q_id, answer in user_answers.items() if answer == correct_answers.get(int(q_id), None))
    total_questions = len(test['questions'])
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": (score / total_questions) * 100
    }
