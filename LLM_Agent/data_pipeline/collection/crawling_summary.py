import os
import sys
import time
import json
from urllib.parse import quote

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.web_brower import setup_browser

from selenium.webdriver.common.by import By

import click

class CollectJobSummary:
    def __init__(self, keyword):
        self.keyword = keyword
        self.save_path = os.path.join("storage", "raw_data", "JD", f"{keyword}_summary.json")
        
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        
    def collect_summary(self):
        browser = setup_browser()
        
        print("> 브라우저 시작")
        url = f'https://www.wanted.co.kr/search?query={quote(self.keyword)}&tab=position'
        browser.get(url)
        time.sleep(5)
        
        last_height = browser.execute_script("return document.body.scrollHeight")
        pause_time = 3
        
        print("> 브라우저 탐색")
        while True:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)

            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(">> 더 이상 로딩할 내용이 없습니다.")
                break
            last_height = new_height
            
        print("> 채용 공고 리스트 확인")
        job_cards = browser.find_elements(By.CSS_SELECTOR, 'div[role="listitem"] > a')
        job_data = {}
        
        print("> 채용 공고 데이터 정리")
        for card in job_cards:
            page_id = card.get_attribute('data-position-id')
            if not page_id in job_data:
                position_name = card.get_attribute('data-position-name')
                company_name = card.get_attribute('data-company-name')
                position_url = card.get_attribute('href')

                job_data[page_id] = {
                    'position_name': position_name,
                    'company_name': company_name,
                    'position_url': position_url
                }
                
        browser.quit()
        
        self.save_json(job_data)
        
    def save_json(self, data):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"> 저장 완료: {self.save_path}")

@click.command()
@click.option('-k', '--keyword', required=True, type=click.STRING, help='The job keyword you want to search for')

def main(keyword):
    collector = CollectJobSummary(keyword)
    collector.collect_summary()

if __name__ == '__main__':
    main()