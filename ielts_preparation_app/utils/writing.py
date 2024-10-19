import json
from .common import get_openai_response, get_random_topic

def create_analysis_prompt(essay, task_type, topic):
    task_description = "Writing Task 1" if task_type == 1 else "Writing Task 2"
    prompt = f"""You are an IELTS {task_description} examiner. Analyze the following essay based on the given topic and provide the response **only** in JSON format without any additional comments. Response format:

{{
  "scores": {{
    "task_achievement": number from 0 to 9,
    "coherence_and_cohesion": number from 0 to 9,
    "lexical_resource": number from 0 to 9,
    "grammatical_range_and_accuracy": number from 0 to 9,
    "overall": number from 0 to 9
  }},
  "improvements": [
    {{
      "text": "Error text",
      "suggestion": "Suggestion for correction"
    }}
  ],
  "recommendations": "String with general recommendations",
  "topic_relevance": "Comment on how well the essay addresses the given topic"
}}

Topic: {topic}

Essay:
'''
{essay}
'''
"""
    return prompt

def analyze_essay(essay, task_type, topic):
    prompt = create_analysis_prompt(essay, task_type, topic)
    result = get_openai_response(prompt)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("Error parsing the API response.")
            return None
    return None

def get_writing_topic(custom_topic=None):
    if custom_topic:
        return custom_topic
    return get_random_topic('writing')
