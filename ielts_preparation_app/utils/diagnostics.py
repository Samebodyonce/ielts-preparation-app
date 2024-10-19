import random
from .common import get_openai_response, generate_audio
from .speaking import transcribe_audio
import os

DIAGNOSTIC_QUESTIONS = {
    'listening': [
        {"question": "What is the capital of France?", "options": ["London", "Berlin", "Paris", "Madrid"], "correct": "Paris"},
        {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"], "correct": "William Shakespeare"},
    ],
    'reading': [
        {
            "passage": "Climate change is a pressing global issue that affects every aspect of our lives. Rising temperatures, extreme weather events, and melting ice caps are just a few of the consequences we're facing. Scientists agree that human activities, particularly the burning of fossil fuels, are the main drivers of climate change. To mitigate its effects, we need to take urgent action on both individual and global scales.",
            "questions": [
                {"question": "What is the main idea of the passage?", "options": ["Economic growth", "Climate change", "Population growth", "Technological advancements"], "correct": "Climate change"},
                {"question": "According to the passage, what is a consequence of climate change?", "options": ["Increased biodiversity", "Rising temperatures", "Economic prosperity", "Decreased pollution"], "correct": "Rising temperatures"},
            ]
        }
    ],
    'writing': [
        {"task": "Write a short paragraph about your favorite hobby."},
        {"task": "Describe the advantages and disadvantages of living in a big city."},
    ],
    'speaking': [
        {"question": "Describe your favorite place to relax."},
        {"question": "Talk about a person who has influenced you greatly."},
    ]
}

def get_diagnostic_test(skill):
    if skill == 'reading':
        return random.choice(DIAGNOSTIC_QUESTIONS[skill])
    elif skill == 'listening':
        questions = random.sample(DIAGNOSTIC_QUESTIONS[skill], k=min(len(DIAGNOSTIC_QUESTIONS[skill]), 5))
        for question in questions:
            audio_file = generate_audio(question['question'])
            if audio_file:
                question['audio_url'] = audio_file
                question['question'] = ''  # Remove the text question
        return questions
    elif skill == 'speaking':
        return random.choice(DIAGNOSTIC_QUESTIONS[skill])
    else:
        return random.sample(DIAGNOSTIC_QUESTIONS[skill], k=min(len(DIAGNOSTIC_QUESTIONS[skill]), 5))

def evaluate_diagnostic_test(skill, answers):
    if skill == 'listening':
        questions = get_diagnostic_test(skill)
        correct = sum(1 for q, a in zip(questions, answers) if q['correct'] == a)
        score = (correct / len(questions)) * 9  # Преобразуем в шкалу IELTS
        return score
    elif skill == 'reading':
        correct = sum(1 for q, a in zip(DIAGNOSTIC_QUESTIONS[skill][0]['questions'], answers) if q['correct'] == a)
        score = (correct / len(answers)) * 9  # Преобразуем в шкалу IELTS
        return score
    elif skill == 'writing':
        prompt = f"Evaluate the following writing response for IELTS proficiency. Provide a score from 1 to 9 and a brief explanation.\n\nResponse: {answers[0]}"
        result = get_openai_response(prompt)
        try:
            score, explanation = result.split('\n', 1)
            score_value = score.split(':')[1].strip()
            # Удаляем все нецифровые символы, кроме точки
            score_value = ''.join(char for char in score_value if char.isdigit() or char == '.')
            return float(score_value)
        except (ValueError, IndexError) as e:
            print(f"Error parsing the score: {e}")
            print(f"Original response: {result}")
            return None
    elif skill == 'speaking':
        audio_file = answers[0]
        transcript = transcribe_audio(audio_file)
        if not transcript:
            print("Failed to transcribe audio")
            return None
        
        prompt = f"Evaluate the following IELTS speaking response transcript. Provide a score from 1 to 9 and a brief explanation.\n\nTranscript: {transcript}"
        result = get_openai_response(prompt)
        try:
            score, explanation = result.split('\n', 1)
            score_value = score.split(':')[1].strip()
            # Удаляем все нецифровые символы, кроме точки
            score_value = ''.join(char for char in score_value if char.isdigit() or char == '.')
            return float(score_value)
        except (ValueError, IndexError) as e:
            print(f"Error parsing the score: {e}")
            print(f"Original response: {result}")
            return None

def identify_strengths_weaknesses(results):
    strengths = [skill for skill, score in results.items() if isinstance(score, (int, float)) and score >= 6.5]
    weaknesses = [skill for skill, score in results.items() if isinstance(score, (int, float)) and score < 6.5]
    return strengths, weaknesses

def create_learning_plan(results):
    strengths, weaknesses = identify_strengths_weaknesses(results)
    overall_score = sum(score for score in results.values() if isinstance(score, (int, float))) / len(results)
    
    plan = f"Your estimated IELTS scores:\n\n"
    for skill, score in results.items():
        if isinstance(score, (int, float)):
            plan += f"{skill.capitalize()}: {score:.1f}\n"
        else:
            plan += f"{skill.capitalize()}: N/A\n"
    plan += f"\nOverall estimated score: {overall_score:.1f}\n\n"
    
    plan += "Your personalized learning plan:\n\n"
    for weakness in weaknesses:
        plan += f"- Focus on improving your {weakness} skills. Your current estimated score is {results[weakness]:.1f}. "
        plan += get_skill_advice(weakness)
        plan += "\n"
    for strength in strengths:
        plan += f"- Maintain your strong {strength} skills. Your current estimated score is {results[strength]:.1f}. "
        plan += "Continue practicing to maintain or improve this score.\n"
    
    return plan

def get_skill_advice(skill):
    advice = {
        'listening': "Practice with various accents and listen to English media daily.",
        'reading': "Read diverse English texts and practice time management for long passages.",
        'writing': "Focus on essay structure, vocabulary, and grammar. Practice writing under timed conditions.",
        'speaking': "Improve fluency by speaking English regularly and expanding your vocabulary."
    }
    return advice.get(skill, "Practice this skill regularly to improve.")

def cleanup_audio_files(questions):
    for question in questions:
        if 'audio_url' in question:
            try:
                os.remove(question['audio_url'])
            except:
                pass
