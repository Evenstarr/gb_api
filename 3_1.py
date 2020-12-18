from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

from pymongo import MongoClient


def get_soup(url, path):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    response = requests.get(f'{url}{path}', headers={'User-Agent': user_agent})
    if response.ok:
        return bs(response.text, 'html.parser')
    else:
        return False


def parse_vacancy(vacancy, vacancy_item):
    vacancy_salary = vacancy_item.get('vacancy_salary')
    short_link = vacancy_item.get('short_link')

    salary_min, salary_max, salary_currency = None, None, None

    link = vacancy.find('a')

    vacancy_name = link.text
    if short_link:
        vacancy_link = vacancy_item.get('url') + link['href']
    else:
        vacancy_link = link['href']

    if vacancy_item.get('url') == 'https://spb.hh.ru':
        vid = link['data-vacancy-id']
    else:
        vid = link['href'].split(".")[0].split("-")[-1]

    salary = vacancy.find('span', vacancy_salary)
    if salary:
        s_text = salary.text.replace(u'\xa0', u'')

        if vacancy_item.get('url') == 'https://spb.hh.ru':
            s_list = s_text.split()
            if s_list[-1] == 'руб.':
                salary_currency = 'RUR'
            else:
                salary_currency = s_list[-1]
            if s_list[0] == 'от':
                salary_min = s_list[1]
            elif s_list[0] == 'до':
                salary_max = s_list[1]
            else:
                try:
                    salary_min = s_list[0].split('-')[0]
                    salary_max = s_list[0].split('-')[1]
                except IndexError:
                    pass
        else:
            salary = re.findall(r'(?:^(\D+)|(\d+))', s_text)

            if salary[0][0] == 'от':
                salary_min = salary[1][1]
            elif salary[0][0] == 'до':
                salary_max = salary[1][1]
            elif salary[0][0] != "По договорённости":
                if len(salary) > 1:
                    salary_min = int(salary[0][1])
                    salary_max = int(salary[1][1])
                else:
                    salary_min, salary_max = salary[0][1], salary[0][1]

            try:
                salary_currency = re.findall(r'([\D]+)/месяц$', s_text)[0]
                if salary_currency == 'руб.':
                    salary_currency = 'RUR'
            except IndexError:
                pass

    if salary_max:
        salary_max = int(salary_max)
    if salary_min:
        salary_min = int(salary_min)
    return {'name': vacancy_name, 'url': vacancy_item.get('url'), 'vid': vid, 'link': vacancy_link, 'salary_min': salary_min, 'salary_max': salary_max,
            'salary_currency': salary_currency}


sites = [
    {
         "url": "https://spb.hh.ru",
         "path": "/search/vacancy?L_is_autosearch=false&area=2&clusters=true&enable_snippets=true&text=python&page=0",
         "vacancy_div": {"data-qa": "vacancy-serp__vacancy"},
         "vacancy_salary": {"data-qa": "vacancy-serp__vacancy-compensation"},
         "next": {"data-qa": "pager-next"},
         "short_link": False,
    },
    {
        "url": "https://spb.superjob.ru",
        # "path": "/vacancy/search/?keywords=Продавец&page=1", # тут есть разнообразные варианты
        "path": "/vacancy/search/?keywords=python&page=1",
        "vacancy_div": {"class": "f-test-vacancy-item"},
        "vacancy_salary": {"class": "f-test-text-company-item-salary"},
        "next": {"class": "f-test-button-dalshe"},
        "short_link": True
    }
]


vacancies = []

for item in sites:
    url = item.get('url')
    path = item.get('path')
    while True:
        soup = get_soup(url, path)
        if not soup:
            break

        vacancies_html = soup.findAll('div', item.get('vacancy_div'))
        if vacancies_html:
            for vacancy in vacancies_html:
                vacancies.append(parse_vacancy(vacancy, item))

        is_next = soup.find('a', item.get('next'))

        if not is_next:
            break

        path = is_next['href']


client = MongoClient('localhost', 27017)

db = client['test_db']
collection = db.vacancies

db.collection.insert_many(vacancies)

# df = pd.DataFrame(vacancies)
# # csv None не хочет писать. А оно там есть.
# df.to_csv("res.csv", sep='\t', encoding='utf-8')
