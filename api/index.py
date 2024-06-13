from flask import Flask, g, request, jsonify
import requests
import os
import dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


ROOT_FOLDER = os.path.abspath(__file__).rsplit('/', 2)[0]
dotenv.load_dotenv(os.path.join(ROOT_FOLDER, '.env'))

AIRTABLE_TABLE_API_PATH = os.environ.get('AIRTABLE_TABLE_API_PATH')
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')

SMTP_EMAIL = os.environ.get('SMTP_EMAIL')
SMTP_EMAIL_PWD = os.environ.get('SMTP_EMAIL_PWD')
SMTP_EMAIL_SERVER = os.environ.get('SMTP_EMAIL_SERVER')
SMTP_EMAIL_PORT = int(os.environ.get('SMTP_EMAIL_PORT', 465))

AIRTABLE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIRTABLE_API_KEY}"
}

app = Flask(__name__)


@app.route('/', methods=['GET'])
def _():
    return jsonify({'status': 'UP', 'msg': 'Hello from Silvertongue Labs'})


def _send_mail(data):
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = SMTP_EMAIL
    msg['Subject'] = '[New Lead]: Silvertongue Labs'

    msg.attach(MIMEText(str(data), 'plain'))
    try:
        server = smtplib.SMTP(SMTP_EMAIL_SERVER, SMTP_EMAIL_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_EMAIL_PWD)
        server.sendmail(SMTP_EMAIL, SMTP_EMAIL, msg.as_string())
        return True
    except Exception as e:
        return False
        pass
    finally:
        server.quit()


def _add_to_airtable(data):
    payload = {"records": [
        {"fields": data}]
    }

    res = requests.request(
        method='POST', url=AIRTABLE_TABLE_API_PATH,
        json=payload, headers=AIRTABLE_HEADERS
    )
    return res


@app.route('/contact-form', methods=['POST'])
def add_contact_form_data():
    data = request.get_json()
    data = {
        'first name': data.get('name'),
        'last name': data.get('lastName'),
        'role': data.get('role'),
        'company': data.get('company'),
        'location': data.get('location'),
        'objective': data.get('objective'),
        'email': data.get('email'),
    }
    res = _add_to_airtable(data)
    mail = _send_mail(data)
    print(res.text, mail)

    if (res.status_code == 200) or mail:
        return jsonify({"data": {"message": "Great! We will reach out to you very soon!"}}), 201
    else:
        return jsonify({"data": {"message": "Oh No!! Something went wrong! Lets try that again?"}}), 500


