from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pymongo
import time
from datetime import datetime
import re
import random

# ฟังก์ชันช่วยดึงลิงก์จาก onclick
def extract_link_from_onclick(onclick_text):
    match = re.search(r"['\"](/product/[^'\"]+)['\"]", onclick_text)
    return f"https://www.thaiwatsadu.com{match.group(1)}" if match else "ไม่มีลิงก์"

# URL ของหน้าเว็บ
web = 'https://www.thaiwatsadu.com/th/category/วัสดุก่อสร้าง-53'

# เชื่อมต่อ MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["scraping_db"]
collection = db["thaiwatsadu_logs"]

# ตั้งค่า Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.0.0 Safari/537.36')

# เพิ่ม experimental options
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)

try:
    # เริ่มต้น WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    # ตั้งค่า CDP
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.0.0 Safari/537.36'
    })
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    print(f"กำลังเข้าถึง URL: {web}")
    driver.get(web)
    
    # รอให้หน้าเว็บโหลดเสร็จ
    print("รอการโหลดหน้าเว็บ...")
    time.sleep(random.uniform(15, 20))
    
    # รอให้มีสินค้าแสดงในหน้าเว็บ
    wait = WebDriverWait(driver, 30)
    try:
        # รอให้มี element ที่มี class ที่ต้องการ
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pt-1.md\\:pt-2.pb-2.bg-white.hover\\:shadow-md.cursor-pointer.rounded')))
        print("พบ element สินค้า")
    except Exception as e:
        print(f"ไม่พบ element สินค้า: {str(e)}")
    
    # เลื่อนหน้าจอลงเพื่อโหลดเนื้อหาเพิ่ม
    print("กำลังเลื่อนหน้าจอ...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(random.uniform(5, 8))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(5, 8))
    
    # วิเคราะห์ HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # ค้นหาสินค้าทั้งหมด
    products = soup.find_all('div', class_='pt-1 md:pt-2 pb-2 bg-white hover:shadow-md cursor-pointer rounded')
    print(f"พบสินค้าทั้งหมด: {len(products)} รายการ")
    
    if len(products) == 0:
        print("\nDebug: ตรวจสอบ HTML ที่ได้:")
        print(driver.page_source[:2000])
        raise Exception("ไม่พบข้อมูลสินค้าในหน้าเว็บ")

    data = []
    incomplete_count = 0

    for product in products:
        try:
            # Debug: Print product HTML
            print("\nกำลังประมวลผลสินค้า:")
            print(product.prettify()[:200])
            
            # หาชื่อสินค้า
            title = None
            title_elem = product.find('div', class_='font-semibold text-lg leading-5 hover:underline')
            if title_elem:
                title = title_elem.text.strip()
            else:
                # ลองหา title ด้วยวิธีอื่น
                title_elem = product.find('div', class_=lambda x: x and 'font-semibold' in x)
                if title_elem:
                    title = title_elem.text.strip()
                else:
                    title_elem = product.find('div', class_=lambda x: x and 'text-lg' in x)
                    if title_elem:
                        title = title_elem.text.strip()
            
            if not title:
                title = "ไม่พบชื่อสินค้า"

            # หาราคา
            price = None
            price_elem = product.find('div', class_='text-grayDark text-sm leading-3 line-through')
            if price_elem:
                price = price_elem.text.strip()
            else:
                # ลองหาราคาด้วยวิธีอื่น
                price_elem = product.find('div', class_=lambda x: x and 'text-grayDark' in x)
                if price_elem:
                    price = price_elem.text.strip()
                else:
                    price_elem = product.find('div', class_=lambda x: x and 'line-through' in x)
                    if price_elem:
                        price = price_elem.text.strip()
            
            if not price:
                price = "ไม่มีราคา"

            # ค้นหาลิงก์
            link = "ไม่มีลิงก์"
            link_elem = product.find('a', href=True)
            if link_elem:
                if link_elem.has_attr('data-url'):
                    link = f"https://www.thaiwatsadu.com{link_elem['data-url']}"
                elif link_elem.has_attr('onclick'):
                    link = extract_link_from_onclick(link_elem['onclick'])
                else:
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = f"https://www.thaiwatsadu.com{link}"

            print(f"✅ {title} - {price} - {link}")

            data.append({
                "title": title,
                "price": price,
                "link": link,
                "scraped_at": datetime.now()
            })

        except Exception as e:
            incomplete_count += 1
            print(f"⚠️ เกิดข้อผิดพลาดในการประมวลผลสินค้า: {str(e)}")

    print(f"ข้อมูลสมบูรณ์: {len(data)} รายการ")
    print(f"ข้อมูลไม่สมบูรณ์: {incomplete_count} รายการ")

    # บันทึกลง MongoDB
    if data:
        collection.insert_many(data)
        print("📌 บันทึกลง MongoDB สำเร็จ")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    print("Stack trace:", e.__traceback__)

finally:
    if 'driver' in locals():
        driver.quit()
