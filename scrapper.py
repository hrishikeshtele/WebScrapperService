import os
import random
import time
from random import randint

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import spacy


def extract_skills(nlp, nlp_text, skills_file=None):
    noun_chunks = nlp(nlp_text).noun_chunks
    raw_tokens = nlp.tokenizer(nlp_text)
    tokens = [token.text for token in raw_tokens if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), './skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


if __name__ == '__main__':

    nlp = spacy.load('en_core_web_sm')
    job_list = []

    job_titles = []
    with open('Jobs') as f:
        job_titles = f.readlines()

    random.shuffle(job_titles)
    for job_title in job_titles:
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        time.sleep(randint(10, 20))
        for i in range(0, 20, 10):
            driver.get('https://www.indeed.com/jobs?q=' + job_title + '&l=United%20States&start=' + str(i))
            jobs = []
            driver.implicitly_wait(randint(10, 30))

            for job in driver.find_elements(By.CLASS_NAME, "result"):
                driver.implicitly_wait(20)
                time.sleep(randint(1, 4))
                soup = BeautifulSoup(job.get_attribute('innerHTML'), 'html.parser')

                for data in soup(['style', 'script']):
                    data.decompose()
                print(
                    "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(' '.join(soup.stripped_strings))
                sum_div = job.find_element(By.CLASS_NAME, "job_seen_beacon")
                try:
                    sum_div.click()
                except:
                    close_button = driver.find_element(By.CLASS_NAME, 'popover-x-button-close')[0]
                    close_button.click()
                    sum_div.click()
                job_desc = driver.find_element(By.ID, 'jobDescriptionText').text
                print(
                    ".................................................................................................")

                job_list.append([job_title, extract_skills(nlp, job_desc)])

        driver.close()
    print(job_list)
    # df.to_csv("ai.csv", index=False)
