import pandas as pd
import asyncio
from googlesearch import search

async def fetch_road_and_village(subdistrict, district, province):
    query = f"ถนน หมู่ที่ {subdistrict} {district} {province}"
    try:
        search_results = search(query, num_results=5)
        for result in search_results:
            # วิเคราะห์เนื้อหาของผลการค้นหาเพื่อดึงข้อมูลที่ต้องการ
            # นี่อาจต้องใช้การร้องขอ HTTP และการแยกวิเคราะห์ HTML
            pass
        return "-", "-"
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการค้นหา: {e}")
        return "-", "-"

async def process_row(row):
    road, village = await fetch_road_and_village(row['ตำบล'], row['อำเภอ'], row['จังหวัด'])
    return road, village

async def main():
    file_path = "C:/Users/LOQ/Desktop/Job_Report/Job_power_partners/JOB_3/exel/Book1.csv"

    df = pd.read_csv(file_path, sep="\t")

    if "ถนน" not in df.columns:
        df["ถนน"] = "-"
    if "หมู่ที่" not in df.columns:
        df["หมู่ที่"] = "-"

    tasks = [process_row(row) for _, row in df.iterrows()]
    results = await asyncio.gather(*tasks)

    df["ถนน"], df["หมู่ที่"] = zip(*results)

    df.to_csv(file_path, index=False, sep="\t")
    print(f"ไฟล์ที่อัปเดตถูกบันทึกที่ {file_path}")

if __name__ == "__main__":
    asyncio.run(main())
