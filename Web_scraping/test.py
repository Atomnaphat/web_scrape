import requests
from bs4 import BeautifulSoup
import csv

# URL ของหน้าเว็บ HomePro
web = 'https://www.homepro.co.th/?gad_source=1&gclid=Cj0KCQjwna6_BhCbARIsALId2Z0rOI4zRhA4NykPO06nTECiPWWe1ZAL284kar05xpU5wI0o5M1jvyMaAuShEALw_wcB'

try:
    # ดึงข้อมูลหน้าเว็บ
    response = requests.get(web)
    response.raise_for_status()

    # วิเคราะห์ HTML ด้วย BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # ค้นหาสินค้าทั้งหมดในหน้า
    products = soup.find_all('div', class_='product-plp-card')

    print(f"พบสินค้าทั้งหมดในหน้าเว็บ: {len(products)} รายการ")

    data = []  # List สำหรับเก็บข้อมูลสินค้า
    incomplete_count = 0  # ตัวแปรนับจำนวนสินค้าที่ข้อมูลไม่ครบ

    for product in products:
        try:
            title = product.find('div', class_='item-title').text.strip()
            price = product.find('div', class_='original-price').text.strip()
            data.append([title, price])
        except AttributeError:
            incomplete_count += 1
            print("ข้อมูลสินค้าไม่สมบูรณ์ ข้ามรายการนี้")

    print(f"จำนวนสินค้าที่ดึงข้อมูลได้สมบูรณ์: {len(data)} รายการ")
    print(f"จำนวนสินค้าที่ข้อมูลไม่สมบูรณ์: {incomplete_count} รายการ")

    # บันทึกข้อมูลลงในไฟล์ CSV
    with open('homepro_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Price'])  # เขียน header
        writer.writerows(data)  # เขียนข้อมูลสินค้า

    print("บันทึกข้อมูลลงในไฟล์ homepro_products.csv สำเร็จ")

except requests.exceptions.RequestException as e:
    print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
