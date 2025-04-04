import pymongo
import mysql.connector

# เชื่อมต่อ MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["your_mongodb_database"]  # แทนที่ด้วยชื่อฐานข้อมูล MongoDB ของคุณ
mongo_collection = mongo_db["your_mongodb_collection"] # แทนที่ด้วยชื่อคอลเลกชัน MongoDB ของคุณ

# เชื่อมต่อ MySQL
mysql_config = {
    'user': 'your_mysql_user',  # แทนที่ด้วยชื่อผู้ใช้ MySQL ของคุณ
    'password': 'your_mysql_password', # แทนที่ด้วยรหัสผ่าน MySQL ของคุณ
    'host': 'localhost',
    'database': 'your_mysql_database'  # แทนที่ด้วยชื่อฐานข้อมูล MySQL ของคุณ
}
mysql_conn = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor()

# ฟังก์ชันสำหรับแทรกข้อมูลลงในตาราง tbMaterial
def insert_material(material_data):
    sql = """
        INSERT INTO tbMaterial (commodity_code, commodity_name_th, commodity_name_en, unit_name, head_category, head_category_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        material_data['commodityCode'],
        material_data['commodityNameTH'],
        material_data['commodityNameEN'],
        material_data['unitName'],
        material_data['headCategory'],
        material_data['headCategoryName']
    )
    mysql_cursor.execute(sql, values)
    return mysql_cursor.lastrowid #คืนค่า material_id ที่เพิ่งสร้าง

# ฟังก์ชันสำหรับแทรกข้อมูลลงในตาราง tbPrice
def insert_price(price_data, material_id):
    sql = """
        INSERT INTO tbPrice (material_id, year, month, price_cur, price_vat, type, type_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        material_id,
        price_data['year'],
        price_data['month'],
        price_data['priceCur'],
        price_data['priceVAT'],
        price_data['type'],
        price_data['typeName']
    )
    mysql_cursor.execute(sql, values)

# ดึงข้อมูลจาก MongoDB และแทรกไปยัง SQL
for document in mongo_collection.find():
    for material_data in document['api_response']:
        material_id = insert_material(material_data)
        for year_data in material_data['years']:
            for month_data in year_data['months']:
                price_data = {
                    'year': year_data['year'],
                    'month': month_data['month'],
                    'priceCur': month_data['priceCur'],
                    'priceVAT': month_data['priceVAT'],
                    'type': month_data['type'],
                    'typeName': month_data['typeName']
                }
                insert_price(price_data, material_id)

# บันทึกการเปลี่ยนแปลงและปิดการเชื่อมต่อ
mysql_conn.commit()
mysql_cursor.close()
mysql_conn.close()
mongo_client.close()

print("Data migration completed successfully.")