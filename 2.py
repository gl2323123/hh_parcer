import fake_headers
import requests
import bs4
import re
from fake_headers import Headers
import json
from tqdm import tqdm

headers = Headers(browser="chrome", os="win")
''''
class_vacancy='serp-item'
class_salary='bloko-header-section-2 bloko-header-section-2_lite'
class_name = 'bloko-header-section-3'
class_link = 'vacancy-serp-item__meta-info-company'
class_for_text = 'g-user-content'
'''''

def get_fakeheaders():
    header_gen = fake_headers.Headers(os ='win', browser='chrome')
    return header_gen.generate()

vacancys = []
count = 0
count_false = 0

for page in tqdm(range(0, 300), desc='Поиск вакансий ...'):
    response = requests.get(
        f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page}', headers=get_fakeheaders())
    html_data = response.text
    soup = bs4.BeautifulSoup(html_data, 'lxml')
    tag = soup.find_all('div', class_='serp-item')

    for mask in tag:

        lay = mask.find('a')
        link = lay['href']

        sal = mask.find('span', class_="bloko-header-section-2")
        if sal is not None:
            zp = sal.text
            pattern = re.compile(r'\u202f')
            repl = ' '
            salary = re.sub(pattern, repl, zp)
        else:
            salary = "Не указано"

        name = mask.find(class_="bloko-header-section-3").text

        text1 = mask.find('div', class_='vacancy-serp-item__meta-info-company').text
        company = re.sub(r'\s+', ' ', text1).strip()

        fa = mask.find('div', class_="vacancy-serp-item-company").text
        faaa = re.findall(r'(?:Москва|Санкт-Петербург)', fa)
        city = faaa[0]

        response1 = requests.get(link, headers=get_fakeheaders())
        html_data1 = response1.text
        soup1 = bs4.BeautifulSoup(html_data1, 'lxml')
        tag1 = soup1.find('div', class_='g-user-content')


        vacancy = {
            'link': link,
            'salary': salary,
            'company': company,
            'city': city,
            'name': name
        }

        if salary is not None:
            if salary:
                saltext = salary.strip()
                match1 = re.search(r'[$]',saltext)
                if match1:
                    match_word = match1.group(0)
                    vacancys.append(vacancy)
                    count += 1
                else:
                    count_false += 1
                    continue
        else:
            continue

        if tag1 is not None:
            if tag:
                text = tag1.text
                match = re.search(r'\b(Django|Flask)\b', text)
                if match:
                    match_word = match.group(0)
                    vacancys.append(vacancy)
                    count += 1
                else:
                    count_false += 1
                    continue
        else:
            continue

        filename = 'zp_in_$.json'

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(vacancys, file, indent=4, ensure_ascii=False)

print(f'Количество подходящих вакансий - {count}')