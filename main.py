from bs4 import BeautifulSoup
import requests
from random import random
from time import sleep
import csv


def generate_url(job_title, job_location, page):
    url = 'https://www.indeed.com/jobs?q=' + job_title + \
          '&l=' + job_location + '&sort=date' + '&start=' + str(page * 10)
    return url


def save_record_to_csv(record, filepath, create_new_file=False):
    """Save an individual record to file; set `new_file` flag to `True` to generate new file"""
    header = ["JobTitle", "Company", "Location", "Salary", "PostDate", "Summary", "JobUrl"]
    if create_new_file:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        with open(filepath, mode='a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(record)


def collect_job_cards_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', 'jobsearch-SerpJobCard')
    return cards, soup


def sleep_for_random_interval():
    seconds = random() * 10
    sleep(seconds)


def request_jobs_from_indeed(job_title, job_location):
    response = requests.get(
        url='https://headers.scrapeops.io/v1/browser-headers',
        params={
            'api_key': 'd02bd3cc-9d85-4ad5-a0c1-6d6ba0156b56',
            'num_headers': '2'}
    )
    print(response.json()['result'][0])
    # res = requests.get(
    #     url='https://proxy.scrapeops.io/v1/',
    #     params={
    #         'api_key': 'd02bd3cc-9d85-4ad5-a0c1-6d6ba0156b56',
    #         'url': "https://www.indeed.com/jobs?q=" + job_title + "&l=" + job_location + '"',
    #         'bypass': 'cloudflare',
    #     },
    # )
    # print('Response Body: ', response.json())
    #
    # response = requests.get(
    #     url='https://proxy.scrapeops.io/v1/',
    #     params={
    #         'api_key': 'd02bd3cc-9d85-4ad5-a0c1-6d6ba0156b56',
    #         'url': "https://www.indeed.com/jobs?q=" + job_title + "&l=" + job_location + '"',
    #         'bypass': 'cloudflare',
    #     },
    # )

    res = requests.get("https://www.indeed.com/jobs?q=" + job_title + "&l=" + job_location + '"',
                       headers=response.json()['result'][0])
    if res.status_code == 200:
        return res.text
    else:
        return None


def find_next_page(soup):
    try:
        pagination = soup.find("a", {"aria-label": "Next"}).get("href")
        return "https://www.indeed.com" + pagination
    except AttributeError:
        return None


def extract_job_card_data(card):
    atag = card.h2.a
    try:
        job_title = atag.get('title')
    except AttributeError:
        job_title = ''
    try:
        company = card.find('span', 'company').text.strip()
    except AttributeError:
        company = ''
    try:
        location = card.find('div', 'recJobLoc').get('data-rc-loc')
    except AttributeError:
        location = ''
    try:
        job_summary = card.find('div', 'summary').text.strip()
    except AttributeError:
        job_summary = ''
    try:
        post_date = card.find('span', 'date').text.strip()
    except AttributeError:
        post_date = ''
    try:
        salary = card.find('span', 'salarytext').text.strip()
    except AttributeError:
        salary = ''
    job_url = 'https://www.indeed.com' + atag.get('href')
    return job_title, company, location, job_summary, salary, post_date, job_url


def main(job_title, job_location):
    unique_jobs = set()  # track job urls to avoid collecting duplicate records
    print("Starting to scrape indeed for `{}` in `{}`".format(job_title, job_location))
    # save_record_to_csv(None, filepath, create_new_file=True)

    while True:
        html = request_jobs_from_indeed(job_title, job_location)
        break
        if not html:
            break
        cards, soup = collect_job_cards_from_page(html)
        for card in cards:
            record = extract_job_card_data(card)
            if not record[-1] in unique_jobs:
                # save_record_to_csv(record, filepath)
                unique_jobs.add(record[-1])
        sleep_for_random_interval()
        break
        # url = find_next_page(soup)
        # if not url:
        #     break
    print('Finished collecting {:,d} job postings.'.format(len(unique_jobs)))
    print(unique_jobs)


if __name__ == '__main__':
    # job search settings
    title = 'Software Engineer'
    loc = 'san jose, ca'

    # without email settings
    main(title, loc)
