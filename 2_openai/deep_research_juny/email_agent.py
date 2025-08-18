from typing import Dict
from dotenv import load_dotenv
import os
from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from agents import Agent, function_tool
load_dotenv(override=True)

gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

@function_tool
def send_email(subject: str, body: str):
    to_list = ["junytrece@gmail.com"]

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = ", ".join(to_list)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_list, msg.as_string())
    return {"status": "success"}

INSTRUCTIONS = """Puedes enviar un correo electrónico basado en un informe detallado.
Se te proporcionará un informe detallado. Debes usar tu herramienta para enviar un correo electrónico."""

email_agent = Agent(
    name="Agente de correo electrónico",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
