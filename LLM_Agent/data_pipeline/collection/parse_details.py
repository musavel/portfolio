import os
import sys
import time
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.web_brower import setup_browser

raw_data_path = os.path.join("storage", "raw_data", "JD")
input_csv = os.path.join(raw_data_path, "summary.csv")
output_json = os.path.join(raw_data_path, "job_details.json")

def scroll_and_click_more(driver):
    try:
        more_button = driver.find_element(By.XPATH, "//button[contains(., '상세 정보 더 보기')]")
        driver.execute_script("arguments[0].click();", more_button)
        
        # 우대사항이 포함된 섹션이 로딩될 때까지 대기 (최대 5초)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), '우대')]"))
        )
        
    except Exception as e:
        print("상세 정보 더 보기 클릭 또는 우대 사항 없음:", e)

def clean_text_lines(raw_text: str) -> str:
    lines = raw_text.split("\n")
    cleaned = []
    
    for line in lines:
        line = line.strip()
        
        while line and not re.match(r"[a-zA-Z0-9가-힣]", line[0]):
            line = line[1:].lstrip()
            
        if line:
            cleaned.append(line)
            
    return "\n".join(cleaned)

def extract_experience(soup):
    try:
        spans = soup.select("span.JobHeader_JobHeader__Tools__Company__Info__b9P4Y.wds-rgovpd")
        
        if len(spans) >= 2:
            text = spans[1].get_text(strip=True)
            
            if text.startswith("경력 "):
                return text.replace("경력 ", "")
            
            return text
        
        return ""
    
    except Exception:
        return ""

def extract_sections(soup):
    result = {"tasks": "", "requires": "", "preferences": ""}
    sections = soup.select("h3.wds-1y0suvb")

    for h3 in sections[:3]:
        title = h3.text.strip()
        content_lines = []

        for sibling in h3.find_all_next():
            if sibling == h3:
                continue
            if sibling.name == "h3":
                break
            if sibling.name == "span" and "wds-wcfcu3" in sibling.get("class", []):
                inner = sibling.find("span")
                if inner:
                    raw = inner.get_text(separator="\n").strip()
                    cleaned = clean_text_lines(raw)
                    content_lines.append(cleaned)

        joined = "\n".join(content_lines)

        if "주요" in title:
            result["tasks"] = joined
        elif "자격" in title:
            result["requires"] = joined
        elif "우대" in title:
            result["preferences"] = joined

    return result

def parse_all():
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    df = df[df["tag_kor"] != "기타"].reset_index(drop=True)

    browser = setup_browser()
    parsed_data = []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="상세 페이지 파싱 중"):
        try:
            browser.get(row["position_url"])
            time.sleep(2)

            scroll_and_click_more(browser)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            sections = extract_sections(soup)
            
            experience = extract_experience(soup)

            parsed_data.append({
                "page_id": row["page_id"],
                "tag_eng": row["tag_eng"],
                "tag_kor": row["tag_kor"],
                "experience": experience,
                "tasks": sections["tasks"],
                "requires": sections["requires"],
                "preferences": sections["preferences"]
            })
            
            if (idx + 1) % 5 == 0:
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
                print(f"> 임시 저장 완료: {output_json} (총 {len(parsed_data)}개)")

        except Exception as e:
            print(f"> {row['page_id']} 파싱 실패: {e}")

    browser.quit()

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)

    print(f"> 상세 정보 파싱 완료: {output_json}")

if __name__ == "__main__":
    parse_all()