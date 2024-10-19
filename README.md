# IELTS Preparation App

IELTS Preparation App is a comprehensive application designed to help students prepare for the IELTS exam. It includes adaptive learning, diagnostic tests, and practice modules for all four sections of the IELTS test.

## Features

- Adaptive Learning: Personalized study plans based on user performance
- Diagnostic Tests: Assess your current IELTS level across all skills
- Practice Modules: 
  - Listening
  - Reading
  - Writing
  - Speaking
- Progress Tracking: Visualize your improvement over time
- AI-powered Analysis: Get detailed feedback on your writing and speaking tasks

## Requirements

- Python 3.7+
- pip (Python package manager)
- OpenAI API key

## Installation

1. Clone the repository:   ```
   git clone https://github.com/your-username/ielts-preparation-app.git
   cd ielts-preparation-app   ```

2. Create a virtual environment:
   - Windows:     ```
     python -m venv venv
     venv\Scripts\activate     ```
   - macOS/Linux:     ```
     python3 -m venv venv
     source venv/bin/activate     ```

3. Install dependencies:   ```
   pip install -r requirements.txt   ```

4. Create a `.env` file in the root directory and add your OpenAI API key:   ```
   OPENAI_API_KEY=your_api_key_here   ```

## Running the Application

1. Ensure you're in the virtual environment.

2. Start the Flask application:
   - Windows:     ```
     set FLASK_APP=ielts_preparation_app/main.py
     flask run     ```
   - macOS/Linux:     ```
     export FLASK_APP=ielts_preparation_app/main.py
     flask run     ```

3. Open a web browser and navigate to `http://127.0.0.1:5000/`.

## Docker Support

To run the application using Docker:

1. Ensure Docker is installed on your system.

2. Build the Docker image:   ```
   docker build -t ielts-preparation-app .   ```

3. Run the container:   ```
   docker run -p 5000:5000 -e OPENAI_API_KEY=your_api_key_here ielts-preparation-app   ```

4. Access the application at `http://localhost:5000/`.

## Project Structure

- `ielts_preparation_app/`: Main application directory
  - `main.py`: Flask application entry point
  - `utils/`: Utility modules for each IELTS section
  - `static/`: CSS and JavaScript files
  - `templates/`: HTML templates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
