import requests
import json
import pandas as pd
import pymongo

api_key = "AIzaSyC2PI05iU8fkez-YN5cezugL08t4PauLCw"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

headers = {'Content-Type': 'application/json'}

def find_road_and_village_from_csv(csv_file, column_name):
    """
    ค้นหาถนนและหมู่บ้านจากไฟล์ CSV และเก็บ address และ text จากผลลัพธ์ลง MongoDB
    """
    try:
        df = pd.read_csv(csv_file)
        if column_name not in df.columns:
            return "ไม่พบคอลัมน์ที่ระบุในไฟล์ CSV"

        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["your_database_name"]
        collection = db["results"]

        results = []
        for address in df[column_name]:
            data = {
                "contents": [{
                    "parts": [{"text": f"ต้องการชื่อถนนและหมู่ที่เท่าไรของ {address}"}]
                }]
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                result = response.json()
                results.append(result)
                # เก็บเฉพาะ address และ text ลง MongoDB
                if 'candidates' in result and result['candidates']:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    collection.insert_one({"address": address, "text": text})
                else:
                    collection.insert_one({"address": address, "text": "ไม่พบข้อมูล"})
            else:
                error_message = f"Error: {response.status_code} - {response.text}"
                results.append(error_message)
                collection.insert_one({"address": address, "error": error_message})
        return results

    except FileNotFoundError:
        return "ไม่พบไฟล์ CSV"
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# ตัวอย่างการใช้งาน
csv_file = "Book1.csv"
column_name = "ชื่ออปท." # แก้ไขตรงนี้
district_col = "อำเภอ" # เพิ่มตรงนี้
province_col = "จังหวัด" # เพิ่มตรงนี้
subdistrict_col = "ตำบล" # เพิ่มตรงนี้

results = find_road_and_village_from_csv(csv_file, column_name)
if isinstance(results, str):
    print(results)
else:
    for result in results:
        print(result)