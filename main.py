from logic.emails import predict_email_body_phishing
from logic.phishing_site_urls import predict_url_phishing
from fastapi import (
                    FastAPI, File, UploadFile, Form, status, HTTPException,APIRouter
                    )   


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

    # Return the prediction result
    return {"phishing": prediction}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@api_router.post("/url/")
async def check_phishing_url(url: str = Form(...)):
  """
  This endpoint takes an email body as input and predicts if it's a phishing email.
  """
  try:
    # Call your logic function to predict phishing (replace with your logic)
    prediction = predict_url_phishing(url)

    # Return the prediction result
    return {"phishing": prediction}
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
    prediction = predict_url_phishing(url)

    # Return the prediction result
    return {"phishing": prediction}
  except Exception as e:
    # Handle any errors during prediction
    print(f"An error occurred: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")




# Include the API router in the main app
app.include_router(api_router)






