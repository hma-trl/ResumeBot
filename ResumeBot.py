import requests
from flask import Flask, request
from docxtpl import DocxTemplate
import os

TOKEN = '7773859491:AAHB_5J4B76G7SlhHNnFHdo5YCuxEccAFho'
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)
user_data = {}

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def send_document(chat_id, file_path):
    with open(file_path, 'rb') as f:
        requests.post(URL + "sendDocument", data={"chat_id": chat_id}, files={"document": f})

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_input = data["message"].get("text", "")

        if chat_id not in user_data:
            user_data[chat_id] = {"step": "name"}
            send_message(chat_id, "Welcome! Please enter your full name:")
        else:
            step = user_data[chat_id]["step"]
            if step == "name":
                user_data[chat_id]["name"] = user_input
                user_data[chat_id]["step"] = "job"
                send_message(chat_id, "Job title?")
            elif step == "job":
                user_data[chat_id]["job_title"] = user_input
                user_data[chat_id]["step"] = "exp"
                send_message(chat_id, "Experience?")
            elif step == "exp":
                user_data[chat_id]["experience"] = user_input
                user_data[chat_id]["step"] = "edu"
                send_message(chat_id, "Education?")
            elif step == "edu":
                user_data[chat_id]["education"] = user_input
                user_data[chat_id]["step"] = "skills"
                send_message(chat_id, "Skills (comma-separated)?")
            elif step == "skills":
                user_data[chat_id]["skills"] = user_input
                doc = DocxTemplate("templates/resume_basic.docx")
                doc.render(user_data[chat_id])
                filename = f"resume_{chat_id}.docx"
                doc.save(filename)
                send_document(chat_id, filename)
                os.remove(filename)
                user_data.pop(chat_id)
    return {"ok": True}
