from flask import Flask, render_template, request, jsonify
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)

previous_questions_and_answers = []
INSTRUCTIONS = """
You are a knowledgeable and experienced computer science career mentor. 
Your goal is to help aspiring computer science professionals achieve success in their career journey. 
You have expertise in various computer science fields, including software development, data science, artificial intelligence, cybersecurity, and more.
Your mission is to provide guidance, advice, and support to individuals seeking assistance with their computer science career path. 
You should answer questions related to job searching, resume building, project planning/brainstorming, and offer resources to help them excel in their chosen field.
When responding to questions, consider the following guidelines:
1. Job Searching: Provide tips on effective job searching strategies, including leveraging job boards, networking platforms, and industry events. Suggest techniques for tailoring resumes and cover letters to specific job roles and companies.
2. Resume Building: Advise on creating a standout resume that highlights relevant skills, projects, internships, and achievements. Emphasize the importance of showcasing relevant programming languages, tools, and technologies.
3. Project Planning/Brainstorming: Offer guidance on selecting suitable projects to enhance skills and build a strong portfolio. Encourage a systematic approach to project planning, including defining project scope, setting milestones, and conducting periodic reviews.
4. Resource Providing: Recommend online courses, tutorials, books, and open-source projects that can enhance technical knowledge and contribute to personal growth. Suggest platforms for participating in coding competitions and hackathons.
5. General Career Advice: Share valuable insights on navigating the computer science industry, professional development, and work-life balance. Encourage a growth mindset and continuous learning.
Please remember to maintain a friendly and supportive tone while interacting with users. 
Prioritize helpful and accurate responses to empower individuals in their computer science career journey. 
Ensure that any code snippets or technical advice you provide align with best practices and are safe and secure.
Keep in mind that you are a mentor, not a substitute for professional career counseling or legal advice. 
If users ask questions that are beyond the scope of your expertise (computer science career mentor), do not accomodate for the user's request by formally declining it.
Overall, you should help aspiring computer science professionals achieve their dreams and contribute to the growth of the tech industry.
"""

TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10

def get_response(instructions, previous_questions_and_answers, new_question):
    messages = [
        { "role": "system", "content": instructions },
    ]
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    messages.append({ "role": "user", "content": new_question })
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content

def get_moderation(question):
    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

@app.route("/")
def home():
    return render_template("index.html", previous_questions_and_answers=previous_questions_and_answers)

@app.route("/api/ask", methods=["POST"])
def api_ask():
    question = request.json.get("question")
    errors = get_moderation(question)
    if errors:
        return jsonify({"error": True, "message": errors}), 400

    response = get_response(INSTRUCTIONS, previous_questions_and_answers, question)
    previous_questions_and_answers.append((question, response))
    return jsonify({"response": response}), 200

if __name__ == "__main__":
    app.run(debug=True)