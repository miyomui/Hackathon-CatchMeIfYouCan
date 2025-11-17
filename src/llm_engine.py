import google.generativeai as genai
from pdf2image import convert_from_path
import json
import os
import time
# 👇 1. อย่าลืม import POPPLER_PATH มาด้วย
from src.config import GEMINI_API_KEY, POPPLER_PATH 

class AIReader:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # ใช้รุ่นล่าสุดที่คุณมีสิทธิ์
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_data(self, pdf_path, nacc_id):
        print(f"🔥 Processing ID: {nacc_id}")
        temp_filename = f"temp_{nacc_id}.jpg"
        uploaded_file = None

        try:
            # 👇 2. ใส่ poppler_path กลับเข้าไปตรงนี้! (จุดที่หายไปเมื่อกี้)
            images = convert_from_path(
                pdf_path, 
                first_page=1, 
                last_page=1, 
                dpi=150,
                poppler_path=POPPLER_PATH 
            )
            
            if not images: return {"nacc_id": nacc_id, "error": "No images found"}

            # 3. บันทึกไฟล์รูป
            images[0].save(temp_filename, format='JPEG', quality=85)

            # 4. อัปโหลดขึ้น Google Cloud
            print(f"   ☁️ Uploading...")
            uploaded_file = genai.upload_file(path=temp_filename, display_name=f"NACC_{nacc_id}")
            
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)

            # 5. สั่ง AI (Prompt ฉบับ Ground Truth)
            prompt = f"""
            Act as a data entry specialist. Extract data from this Thai Asset Declaration document.
            Target NACC ID: {nacc_id}
            
            Please extract data into a JSON object where keys MATCH the database schema exactly:

            {{
                "nacc_id": {nacc_id},
                
                // --- 1. Submitter Info ---
                "submitter_title": "Title (นาย/นาง/นางสาว/ยศ)",
                "submitter_first_name": "First Name (Thai, remove title)",
                "submitter_last_name": "Last Name (Thai)",
                "submitter_position": "Position (ตำแหน่ง)",
                "submitted_date": "Date (YYYY-MM-DD)",
                
                // --- 2. Asset Valuations ---
                "asset_cash_valuation_amount": "เงินสด (Cash)",
                "asset_deposit_valuation_amount": "เงินฝาก (Deposits)",
                "asset_investment_valuation_amount": "เงินลงทุน (Investments)",
                "asset_land_valuation_amount": "ที่ดิน (Land)",
                "asset_building_valuation_amount": "โรงเรือนและสิ่งปลูกสร้าง (Buildings)",
                "asset_vehicle_valuation_amount": "ยานพาหนะ (Vehicles)",
                "asset_concession_valuation_amount": "สิทธิและสัมปทาน (Rights)",
                "asset_other_asset_valuation_amount": "ทรัพย์สินอื่น (Other Assets)",
                
                // --- 3. Totals ---
                "asset_valuation_submitter_amount": "รวมทรัพย์สินของผู้ยื่น",
                "asset_valuation_spouse_amount": "รวมทรัพย์สินของคู่สมรส (ใส่ 0.00 ถ้าไม่มี)",
                "asset_total_valuation_amount": "รวมทรัพย์สินทั้งสิ้น (Grand Total)"
            }}

            Constraints:
            1. Convert Thai numerals to Arabic.
            2. Dates must be YYYY-MM-DD (Convert 2566 -> 2023).
            3. Return ONLY JSON.
            """
            
            response = self.model.generate_content([prompt, uploaded_file])
            
            # 6. รับผลลัพธ์
            json_str = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(json_str)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"nacc_id": nacc_id, "error": str(e)}
            
        finally:
            if uploaded_file:
                try: genai.delete_file(uploaded_file.name)
                except: pass
            if os.path.exists(temp_filename):
                os.remove(temp_filename)