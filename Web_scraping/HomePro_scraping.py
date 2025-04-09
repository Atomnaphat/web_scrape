import requests
from bs4 import BeautifulSoup
import pymongo
import csv
from datetime import datetime

# ฟังก์ชันช่วยดึงลิงก์จาก onclick
import re
def extract_link_from_onclick(onclick_text):
    match = re.search(r"['\"](/product/[^'\"]+)['\"]", onclick_text)
    return f"https://www.homepro.co.th{match.group(1)}" if match else "ไม่มีลิงก์"

# URL ของหน้าเว็บ
web = 'https://www.homepro.co.th/?gad_source=1'

# เชื่อมต่อ MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["scraping_db"]
collection = db["homepro_logs"]

try:
    # ดึงข้อมูล
    response = requests.get(web)
    response.raise_for_status()

    # วิเคราะห์ HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # ค้นหาสินค้าทั้งหมด
    products = soup.find_all('div', class_='product-plp-card')

    print(f"พบสินค้าทั้งหมด: {len(products)} รายการ")

    data = []
    incomplete_count = 0

    for product in products:
        try:
            title = product.find('div', class_='item-title').text.strip()
            price = product.find('div', class_='original-price').text.strip()

            # ค้นหาลิงก์
            link_element = product.find('a', href=True)
            if link_element and link_element.has_attr('data-url'):
                link = f"https://www.homepro.co.th{link_element['data-url']}"
            elif link_element and link_element.has_attr('onclick'):
                link = extract_link_from_onclick(link_element['onclick'])
            elif link_element:
                link = link_element['href']
                # เช็คว่าลิงก์มีโดเมนแล้วหรือไม่ ถ้าไม่มีให้เพิ่ม https://www.homepro.co.th
                if not link.startswith('http'):
                    link = f"https://www.homepro.co.th{link}"
            else:
                link = "ไม่มีลิงก์"

            print(f"✅ ดึงลิงก์สำเร็จ: {link}")

            data.append({
                "title": title,
                "price": price,
                "link": link,
                "scraped_at": datetime.now()
            })
        except AttributeError:
            incomplete_count += 1
            print("⚠️ ข้อมูลสินค้าไม่สมบูรณ์ ข้ามรายการนี้")

    print(f"ข้อมูลสมบูรณ์: {len(data)} รายการ")
    print(f"ข้อมูลไม่สมบูรณ์: {incomplete_count} รายการ")

    # บันทึกลง MongoDB
    if data:
        collection.insert_many(data)
        print("📌 บันทึกลง MongoDB สำเร็จ")

    # บันทึก CSV
    csv_filename = "homepro_products.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Price', 'Link', 'Scraped_At'])
        for item in data:
            writer.writerow([item["title"], item["price"], item["link"], item["scraped_at"]])

    print(f"📌 บันทึกไฟล์ {csv_filename} สำเร็จ")

except requests.exceptions.RequestException as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
