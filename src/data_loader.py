import pandas as pd
import os
from src.config import DOC_INFO_FILE, NACC_DETAIL_FILE

def load_master_data():
    """อ่านและเชื่อมตารางข้อมูลหลัก"""
    print("📂 Loading Metadata...")
    try:
        # 1. อ่านไฟล์
        df_doc = pd.read_csv(DOC_INFO_FILE)
        df_detail = pd.read_csv(NACC_DETAIL_FILE)

        # 2. ล้างชื่อหัวตาราง (ลบช่องว่างที่มองไม่เห็น)
        df_doc.columns = df_doc.columns.str.strip().str.replace('\ufeff', '')
        df_detail.columns = df_detail.columns.str.strip().str.replace('\ufeff', '')

        # 3. 🎯 จุดแก้สำคัญ: หยิบชื่อไฟล์จาก 'doc_location_url'
        if 'doc_location_url' in df_doc.columns:
            df_doc['document_name'] = df_doc['doc_location_url'].apply(lambda x: os.path.basename(str(x)))
            print("🔧 Fix: ดึงชื่อไฟล์มาจากช่อง 'doc_location_url' เรียบร้อยแล้ว")
        else:
            print("⚠️ Warning: หาช่อง doc_location_url ไม่เจอ (โปรดเช็คไฟล์ CSV)")

        # 4. เชื่อมตาราง
        master = pd.merge(df_doc, df_detail, on='nacc_id', how='left')

        print(f"✅ Loaded {len(master)} records.")
        return master

    except FileNotFoundError as e:
        print(f"❌ Error: หาไฟล์ CSV ไม่เจอ! ({e})")
        return pd.DataFrame()