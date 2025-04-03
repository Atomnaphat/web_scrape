import requests
from bs4 import BeautifulSoup
import csv

web = 'https://www.homepro.co.th/?gad_source=1&gclid=Cj0KCQjwna6_BhCbARIsALId2Z0rOI4zRhA4NykPO06nTECiPWWe1ZAL284kar05xpU5wI0o5M1jvyMaAuShEALw_wcB'

try:
    response = requests.get(web)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    products = soup.find_all('div', class_='product-plp-card')

    data = []  # List สำหรับเก็บข้อมูลสินค้า

    for product in products:
        title_element = product.find('div', class_='item-title')
        price_element = product.find('div', class_='original-price')

        if title_element and price_element:
            title = title_element.text.strip()
            price = price_element.text.strip()
            data.append([title, price])
        else:
            print("ข้อมูลสินค้าไม่สมบูรณ์")

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