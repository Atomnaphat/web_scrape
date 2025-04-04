import requests
import json
import pandas as pd
import pymongo

api_key = "AIzaSyC2PI05iU8fkez-YN5cezugL08t4PauLCw"  # แทนที่ด้วย API key ของคุณ
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

headers = {'Content-Type': 'application/json'}

def find_road_and_village_from_csv(csv_file, column_name):
    """
    ค้นหาถนนและหมู่บ้านจากไฟล์ CSV โดยใช้คอลัมน์ที่ระบุ และเก็บผลลัพธ์ลง MongoDB
    """
    try:
        df = pd.read_csv(csv_file)
        if column_name not in df.columns:
            return "ไม่พบคอลัมน์ที่ระบุในไฟล์ CSV"

        # เชื่อมต่อกับ MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")  # แก้ไข connection string ตาม MongoDB ของคุณ
        db = client["your_database_name"]  # แทนที่ด้วยชื่อฐานข้อมูลของคุณ
        collection = db["results"]  # แทนที่ด้วยชื่อ collection ที่คุณต้องการเก็บผลลัพธ์

        results = []
        for address in df[column_name]:
            data = {
                "contents": [{
                    "parts": [{"text": f"ต้องการ ถนนและหมู่บ้านของ {address} เพื่อส่งไปรษณีย์"}]
                }]
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                result = response.json()
                results.append(result)
                # แทรกผลลัพธ์ลง MongoDB
                collection.insert_one({"address": address, "result": result})
            else:
                error_message = f"Error: {response.status_code} - {response.text}"
                results.append(error_message)
                # แทรกข้อผิดพลาดลง MongoDB
                collection.insert_one({"address": address, "error": error_message})
        return results

    except FileNotFoundError:
        return "ไม่พบไฟล์ CSV"
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# ตัวอย่างการใช้งาน
csv_file = "Book1.csv"  # แทนที่ด้วยชื่อไฟล์ CSV ของคุณ
column_name = "ชื่ออปท."  # คอลัมน์ที่ต้องการค้นหา

results = find_road_and_village_from_csv(csv_file, column_name)
if isinstance(results, str):
    print(results)  # พิมพ์ข้อผิดพลาดถ้ามี
else:
    for result in results:
        print(result)