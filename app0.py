from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session usage

# Configure the Generative AI model
genai.configure(api_key="AIzaSyDlJLGUA1CawKLpOAbjisci5xsZLHjcY-8")  # Replace with your actual API key
generation_config = {
    "temperature": 1.05,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 300  # Adjust as needed for response length
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config
)

@app.route('/')
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html', chat_history=session['chat_history'])

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if 'chat_history' not in session:
        session['chat_history'] = []

    # Add user message to the session history
    session['chat_history'].append({'role': 'user', 'text': user_message})

    # Prepare the prompt
    prompt = """You are a highly knowledgeable assistant specializing in computer architecture, programming, and education. Your primary focus is to help students understand and differentiate between Intel Architecture (x86/x64) and RISC-V Architecture. Additionally, you assist them in learning and coding in assembly language and other related programming paradigms.

    Your responsibilities include:
    - Explaining fundamental concepts of Intel and RISC-V architectures, including their instruction sets, registers, pipelines, and memory management techniques.
    - Comparing and contrasting the key differences, such as instruction set complexity (CISC vs RISC), register usage, addressing modes, and performance optimization strategies.
    - Demonstrating assembly language programming for both architectures, providing examples and breaking down how instructions are executed step-by-step.
    - Offering practical exercises and explaining optimization strategies.
    - Answering students' questions and debugging their assembly code with step-by-step solutions.

    Adapt your explanations based on the student's background, simplifying concepts or diving deep into advanced topics when needed. Ensure your responses are clear and accessible.
    """

    # Include recent chat history in the prompt
    max_turns = 6  # Adjust based on desired prompt length
    recent_history = session['chat_history'][-max_turns:]
    for turn in recent_history:
        role = "User" if turn['role'] == 'user' else "AI"
        prompt += f"\n{role}: {turn['text']}"
    prompt += "\nAI:"

    try:
        # Generate the response
        response = model.generate_content(prompt)

        # Add the AI response to the session history
        session['chat_history'].append({'role': 'ai', 'text': response.text})
        session.modified = True  # Mark the session as modified

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
