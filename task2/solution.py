
import requests
from bs4 import BeautifulSoup
import csv
from collections import defaultdict
import re
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WikiAnimalParser:
    def __init__(self):
        self.base_url = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.animals_by_letter = defaultdict(int)
        self.session = self._create_session()

    def _create_session(self):
        """Создает сессию с настройками повторных попыток и таймаутов"""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get_page_content(self, url):
        """Получает содержимое страницы"""
        # Отключаем предупреждения о небезопасных запросах
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = self.session.get(
            url,
            headers=self.headers,
            verify=False,  # Отключаем проверку SSL
            timeout=30
        )
        response.raise_for_status()
        return response.text

    def parse_page(self, html):
        """Парсит страницу и извлекает названия животных"""
        soup = BeautifulSoup(html, 'html.parser')
        content_div = soup.find('div', {'class': 'mw-category'})
        
        if not content_div:
            return []
        
        return [a.text for a in content_div.find_all('a')]

    def get_next_page_url(self, html):
        """Получает URL следующей страницы"""
        soup = BeautifulSoup(html, 'html.parser')
        next_link = soup.find('a', string='Следующая страница')
        if next_link:
            return 'https://ru.wikipedia.org' + next_link['href']
        return None

    def count_animals_by_letter(self, animals):
        """Подсчитывает количество животных на каждую букву"""
        for animal in animals:
            # Получаем первую букву названия, исключая специальные символы
            first_letter = re.sub(r'[^а-яА-Я]', '', animal)
            if first_letter:
                self.animals_by_letter[first_letter[0].upper()] += 1

    def save_to_csv(self, filename='beasts.csv'):
        """Сохраняет результаты в CSV файл"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Сортируем буквы по алфавиту
            for letter in sorted(self.animals_by_letter.keys()):
                writer.writerow([letter, self.animals_by_letter[letter]])

    def run(self):
        """Основной метод для запуска парсера"""
        current_url = self.base_url
        page_count = 0

        while current_url:
            try:
                html = self.get_page_content(current_url)
                animals = self.parse_page(html)
                self.count_animals_by_letter(animals)
                current_url = self.get_next_page_url(html)
                page_count += 1
                print(f"Обработана страница {page_count}")
            except requests.RequestException as e:
                print(f"Ошибка при получении страницы: {e}")
                print(f"URL: {current_url}")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                print(f"URL: {current_url}")
                break

        print(f"Всего обработано страниц: {page_count}")
        self.save_to_csv()
        print(f"Результаты сохранены в файл beasts.csv")

if __name__ == '__main__':
    parser = WikiAnimalParser()
    parser.run()