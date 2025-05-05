import os
import json
import pandas as pd

raw_data_path = os.path.join("storage", "raw_data", "JD")
output_path = os.path.join(raw_data_path, "summary_raw.csv")

def load_json_files():
    data_list = []
    for file in os.listdir(raw_data_path):
        if file.endswith("_summary.json"):
            with open(os.path.join(raw_data_path, file), "r", encoding="utf-8") as f:
                json_data = json.load(f)
                for page_id, content in json_data.items():
                    content["page_id"] = page_id
                    data_list.append(content)
    return pd.DataFrame(data_list)

def merge_and_save():
    df = load_json_files()
    df = df[["page_id", "position_name", "company_name", "position_url"]]
    df = df.drop_duplicates(subset="page_id")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"> summary_raw.csv 저장 완료: {output_path} ({len(df)}개 공고)")
    
if __name__ == "__main__":
    merge_and_save()