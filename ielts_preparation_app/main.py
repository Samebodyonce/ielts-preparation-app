from flask import Flask, render_template, request, jsonify, send_file, session
from utils import listening, reading, writing, speaking, diagnostics
from utils.langchain_utils import use_ielts_agent
from utils.common import generate_audio
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Добавьте это для работы с сессиями

# Флаг для отслеживания первого запроса
first_request = True

@app.before_request
def clear_session_on_first_request():
    global first_request
    if first_request:
        session.clear()
        first_request = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listening')
def listening_page():
    return render_template('listening.html')

@app.route('/reading')
def reading_page():
    return render_template('reading.html')

@app.route('/writing')
def writing_page():
    return render_template('writing.html')

@app.route('/speaking')
def speaking_page():
    return render_template('speaking.html')

@app.route('/diagnostics')
def diagnostics_page():
    return render_template('diagnostics.html')

@app.route('/adaptive_learning')
def adaptive_learning_page():
    return render_template('adaptive_learning.html')

@app.route('/api/get_writing_topic', methods=['GET'])
def get_writing_topic():
    custom_topic = request.args.get('custom_topic')
    topic = writing.get_writing_topic(custom_topic)
    return jsonify({"topic": topic})

@app.route('/api/analyze_writing', methods=['POST'])
def analyze_writing():
    essay = request.json['essay']
    task_type = request.json['task_type']
    topic = request.json['topic']
    result = writing.analyze_essay(essay, task_type, topic)
    return jsonify(result)

@app.route('/api/get_speaking_topic', methods=['GET'])
def get_speaking_topic():
    custom_topic = request.args.get('custom_topic')
    topic = speaking.get_speaking_topic(custom_topic)
    return jsonify({"topic": topic})

@app.route('/api/analyze_speaking', methods=['POST'])
def analyze_speaking():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    topic = request.form['topic']
    
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    result = speaking.analyze_speech(audio_file, topic)
    if result is None:
        return jsonify({"error": "Failed to analyze speech"}), 500
    
    return jsonify(result)

@app.route('/api/get_listening_test', methods=['GET'])
def get_listening_test():
    test = listening.get_listening_test()
    return jsonify(test)

@app.route('/api/check_listening_answers', methods=['POST'])
def check_listening_answers():
    user_answers = request.json['answers']
    result = listening.check_answers(user_answers)
    test = listening.LISTENING_TESTS[0]  # Предполагаем, что это текущий тест
    listening.cleanup_audio_files(test)
    return jsonify(result)

@app.route('/api/get_reading_test', methods=['GET'])
def get_reading_test():
    test = reading.get_reading_test()
    return jsonify(test)

@app.route('/api/check_reading_answers', methods=['POST'])
def check_reading_answers():
    user_answers = request.json['answers']
    result = reading.check_answers(user_answers)
    return jsonify(result)

@app.route('/api/get_diagnostic_test/<skill>')
def get_diagnostic_test(skill):
    test = diagnostics.get_diagnostic_test(skill)
    return jsonify(test)

@app.route('/api/evaluate_diagnostic_test/<skill>', methods=['POST'])
def evaluate_diagnostic_test(skill):
    if skill == 'speaking':
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        audio_file = request.files['audio']
        result = diagnostics.evaluate_diagnostic_test(skill, [audio_file])
    else:
        answers = json.loads(request.form['answers'])
        result = diagnostics.evaluate_diagnostic_test(skill, answers)
    
    if result is None:
        return jsonify({"error": "Failed to evaluate the test"}), 500
    
    # Сохраняем результат во временном хранилище сессии
    if 'temp_diagnostic_results' not in session:
        session['temp_diagnostic_results'] = {}
    session['temp_diagnostic_results'][skill] = result
    session.modified = True  # Явно отмечаем сессию как измененную
    
    return jsonify({"score": result})

@app.route('/api/save_diagnostic_results', methods=['POST'])
def save_diagnostic_results():
    if 'temp_diagnostic_results' not in session:
        return jsonify({"error": "No diagnostic results found"}), 400
    
    # Сохраняем результаты в постоянное хранилище
    session['diagnostic_results'] = session['temp_diagnostic_results']
    
    # Добавляем результат в историю прогресса
    if 'progress_history' not in session:
        session['progress_history'] = []
    session['progress_history'].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        **session['diagnostic_results']
    })
    
    # Очищаем временное хранилище
    session.pop('temp_diagnostic_results', None)
    session.modified = True  # Явно отмечаем сессию как измененную
    
    return jsonify({"message": "Diagnostic results saved successfully"})

@app.route('/api/create_learning_plan', methods=['POST'])
def create_learning_plan():
    results = request.json['results']
    plan = diagnostics.create_learning_plan(results)
    return jsonify({"plan": plan})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    input_text = request.json['input']
    if 'history' not in session:
        session['history'] = []
    history = session['history']
    final_answer, mini_test, listening_text = use_ielts_agent(input_text, history)
    history.append({"role": "user", "content": input_text})
    history.append({"role": "assistant", "content": final_answer})
    session['history'] = history[-10:]  # Сохраняем только последние 10 сообщений
    
    response_data = {"result": final_answer}
    
    if mini_test:
        response_data["mini_test"] = mini_test
    
    if listening_text:
        # Генерируем аудио только для текста прослушивания
        audio_file = generate_audio(listening_text)
        if audio_file:
            response_data["audio_url"] = f"/audio/{audio_file}"
        response_data["listening_text"] = listening_text
    
    return jsonify(response_data)

@app.route('/api/save_target_skills', methods=['POST'])
def save_target_skills():
    targets = request.json
    if 'targets' not in session:
        session['targets'] = {}
    session['targets'] = targets
    session.modified = True
    return jsonify({"message": "Target skills saved successfully"})

@app.route('/api/get_progress', methods=['GET'])
def get_progress():
    if 'diagnostic_results' not in session or not session['diagnostic_results']:
        # Если нет сохраненных результатов, возвращаем нулевые значения и рекомендацию пройти диагностику
        return jsonify({
            "current": {
                "listening": 0,
                "reading": 0,
                "writing": 0,
                "speaking": 0
            },
            "history": [],
            "targets": session.get('targets', {
                "listening": 7.0,
                "reading": 7.0,
                "writing": 7.0,
                "speaking": 7.0
            }),
            "recommendation": "We recommend taking the diagnostic test to get a more accurate assessment of your skills."
        })
    else:
        # Если есть сохраненные результаты, возвращаем их
        return jsonify({
            "current": session['diagnostic_results'],
            "history": session.get('progress_history', []),
            "targets": session.get('targets', {
                "listening": 7.0,
                "reading": 7.0,
                "writing": 7.0,
                "speaking": 7.0
            })
        })

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_file(filename, mimetype='audio/mpeg')

@app.route('/api/check_mini_test', methods=['POST'])
def check_mini_test():
    answers = request.json['answers']
    # Здесь должна быть логика проверки ответов мини-теста
    # Для демонстрации просто возвращаем количество правильных ответов
    correct_answers = session.get('current_mini_test_answers', [])
    score = sum(1 for user_answer, correct_answer in zip(answers, correct_answers) if user_answer == correct_answer)
    return jsonify({"score": score, "total": len(correct_answers)})

def extract_mini_test(result):
    # Извлекаем и форматируем мини-тест из ответа агента
    test_part = result.split("Mini Test:")[1].strip()
    questions = [q.strip() for q in test_part.split('\n') if q.strip()]
    formatted_test = {
        "text": result.split("Mini Test:")[0].strip(),
        "questions": []
    }
    for q in questions:
        if q.startswith("Q:"):
            formatted_test["questions"].append({"question": q[2:].strip(), "options": []})
        elif q.startswith("- ") and formatted_test["questions"]:
            formatted_test["questions"][-1]["options"].append(q[2:].strip())
    return formatted_test

if __name__ == '__main__':
    app.run(debug=True)
