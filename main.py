from logic.emails import predict_email_body_phishing,check_email_domain
from logic.phishing_site_urls import predict_url_phishing
from logic.dns_ import check_phishing_dns
from voice.main import base64_to_audio_segment, Data

from fastapi import (
                    FastAPI, File, UploadFile, Form, status, HTTPException,APIRouter
                    )   
import pymysql.cursors
import speech_recognition as sr
import pyttsx3
import io
from pydub import AudioSegment
import base64
from documents.main import get_emails_urls_from_pages_contents_from,extract_emails_and_urls
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
from pathlib import Path
import os
import hashlib

app = FastAPI()

# Create a router for API endpoints
api_router = APIRouter(prefix="/api")

# Function to create the temporary folder if it doesn't exist
def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

@api_router.get("/")
async def index():
    """
    Index endpoint to check if the server is running.
    """
    return {"messgae":"I am working good !"}

@api_router.post("/email/email-body-phishing")
async def check_phishing_email(emailBody: str = Form(...)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    # Call your logic function to predict phishing (replace with your logic)
    prediction = predict_email_body_phishing([emailBody])
    if prediction == 0:
        urls, emails=extract_emails_and_urls(emailBody)
        emails_with_phishing = []
        for email in emails:
            if not check_email_domain(email):
                emails_with_phishing.append(email)
        urls_with_phishing = []
        for url in urls:
            if predict_url_phishing(url):
                urls_with_phishing.append(url)
        return {"phishing": 1,"emails": emails_with_phishing,"urls":urls_with_phishing}
    
    # Return the prediction result
    return {"phishing": prediction}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/email/email-phishing")
async def check_phishing_email_structure(email: str = Form(...)):
  try:
    ok= check_email_domain(email)
    if ok:
        return {"phishing": 0}
    return {"phishing": 1}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
  
@api_router.post("/url/")
async def check_phishing_url(url: str = Form(...),local_dns_resolution:str=Form(...)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    # Call your logic function to predict phishing (replace with your logic)
    prediction = predict_url_phishing(url)
    # Call your logic function to predict phishing (replace with your logic)
    dns_phishing = 0 if check_phishing_dns(url,local_dns_resolution) else 1
    # Return the prediction result
    return {"phishing": prediction,"dns_phishing":dns_phishing}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/document/pdf/")
async def check_phishing_url_inside_pdf(pdf: UploadFile = File(None)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    if emails is None:
        raise HTTPException(status_code=status,detail="Emails TXT files are missing.")
    # Check if the resume file is a PDF file
    if not pdf.filename.lower().endswith('.pdf'):
        raise HTTPException(detail="The resume file must be a PDF file.")
    
    temp_dir:str = str(Path("./temp"))
    # Check if temp_dir exists, if not, create it
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    pdf_id:str = str(uuid.uuid4())
    with open(f"{temp_dir}/{pdf_id}.pdf", "wb") as resume_file:
        shutil.copyfileobj(pdf.file, resume_file)

    urls, emails=get_emails_urls_from_pages_contents_from(pdf)
    # Return the prediction result
    emails_with_phishing = []
    for email in emails:
           if not check_email_domain(email):
                emails_with_phishing.append(email)
    urls_with_phishing = []
    for url in urls:
              if predict_url_phishing(url):
                 urls_with_phishing.append(url)
    return {"emails": emails_with_phishing,"urls":urls_with_phishing} 
     
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/document/text/")
async def check_phishing_url_inside_text(text: str = Form(...)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    urls, emails=extract_emails_and_urls(text)
    # Return the prediction result
    emails_with_phishing = []
    for email in emails:
           if not check_email_domain(email):
                emails_with_phishing.append(email)
    urls_with_phishing = []
    for url in urls:
              if predict_url_phishing(url):
                 urls_with_phishing.append(url)
    return {"emails": emails_with_phishing,"urls":urls_with_phishing} 
     
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/url/dns/")
async def check_phishing_url_dns(url: str = Form(...),local_dns_resolution:str=Form(...)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    # Call your logic function to predict phishing (replace with your logic)
    phishing = 0 if check_phishing_dns(url,local_dns_resolution) else 1
    # Return the prediction result
    return {"phishing": phishing}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/perform_action")
async def perform_action(data: Data):
    langue = data.langue
    if langue == "":
        langue = "anglais"
    if langue.lower() == "francais":
        langue = "fr"
    elif langue.lower() == "anglais":
        langue = "en"
    elif langue.lower() == "arabe":
        langue = "ar"
    else:
        raise HTTPException(status_code=400, detail="Langue non prise en charge")

    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="vishing",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        recognizer = sr.Recognizer()
        text_speech = pyttsx3.init()
    except Exception as e:
        print("Something went wrong:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    with conn.cursor() as cursor:
        if langue == "fr":
            cursor.execute(f"SELECT Orders.*, Categories.category_name FROM Orders INNER JOIN Categories ON Orders.category_id = Categories.category_id")
        elif langue == "ar":
            cursor.execute(f"SELECT Orders_ar.*, Categories_ar.category_name FROM Orders_ar INNER JOIN Categories_ar ON Orders_ar.category_id = Categories_ar.category_id")
        rows = cursor.fetchall()
        hotwords = [row["hotwords"].split(",") for row in rows]
        category_names = [row["category_name"] for row in rows]
        orders = [row["sentence"] for row in rows]

    audio_segment = base64_to_audio_segment(data.base64data)

    if data.provider == "vosk":
        print("Provider : Vosk")
    elif data.provider == "google":
        if langue.lower() == "fr":
            langue = "fr-FR"
        elif langue.lower() == "en":
            langue = "en-US"
        elif langue.lower() == "ar":
            langue = "ar-AR"
        else:
            langue = "en-US"
        if audio_segment is not None:
            recognizer = sr.Recognizer()
            audio_bytes = io.BytesIO()
            audio_segment.export(audio_bytes, format="wav")
            with sr.AudioFile(audio_bytes) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=langue)
            print("Texte reconnu par google :", text)

    try:
        matched_categories = []
        matched_category_names = set()
        for i, hotword_list in enumerate(hotwords):
            for hotword in hotword_list:
                if hotword in text.lower():
                    category_name = category_names[i]
                    if category_name not in matched_category_names:
                        matched_categories.append({"category_name": category_name})
                        matched_category_names.add(category_name)
                        break
        if matched_categories:
            return {
                "langue": langue,
                "text": text.lower(),
                "matched_categories": matched_categories,
            }
        else:
            print("Command not recognized")
            return {
                "matched_categories": [],
                "langue": langue,
                "text": text.lower(),
                "provider": data.provider,
            }
    except sr.UnknownValueError:
        print(f"Désolé, je n'ai pas compris le son en {langue}")
        raise HTTPException(status_code=500, detail=f"Désolé, je n'ai pas compris le son en {langue}")
    except sr.RequestError:
        print(f"Désolé, le service est actuellement indisponible en {langue}")
        raise HTTPException(status_code=500, detail=f"Désolé, le service est actuellement indisponible en {langue}")
    return {
        "status": "error",
        "error": "Error : Action not found",
        "errorMessage": audio_segment
    }

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router in the main app
app.include_router(api_router)





import socket

# Get the hostname of the machine running the FastAPI app
hostname = socket.gethostname()

# Get the IP address associated with the hostname
local_ip = socket.gethostbyname(hostname)

print(f"Connect to your FastAPI application at http://{local_ip}:8000/")
