import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service(executable_path=os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver"))

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

@app.post("/scrape")
def scrape_profile(data: ScrapeRequest):
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if not email or not password:
        raise HTTPException(status_code=500, detail="Missing LinkedIn credentials")

    try:
        driver = create_driver()
        actions.login(driver, email, password)
        person = Person(data.url, driver=driver)

        result = {
            "name": person.name,
            "job_title": person.job_title,
            "experiences": [str(exp) for exp in person.experiences],
            "educations": [str(edu) for edu in person.educations],
            "interests": person.interests,
        }

        driver.quit()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
