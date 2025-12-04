import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from linkedin_scraper import Person
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

def load_cookies(driver):
    cookie_str = os.getenv("LINKEDIN_COOKIE")
    if not cookie_str:
        raise Exception("LINKEDIN_COOKIE env var not set")
    
    driver.get("https://www.linkedin.com")
    cookies = cookie_str.strip().split(";")
    for c in cookies:
        if "=" in c:
            name, value = c.strip().split("=", 1)
            driver.add_cookie({"name": name, "value": value, "domain": ".linkedin.com"})
    driver.refresh()

@app.post("/scrape")
def scrape_profile(data: ScrapeRequest):
    try:
        driver = create_driver()
        load_cookies(driver)
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
