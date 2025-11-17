import os
import pandas as pd
from tqdm import tqdm
from src.config import PDF_DIR, OUTPUT_DIR, TEST_LIMIT
from src.data_loader import load_master_data
from src.llm_engine import AIReader

def main():
    # 1. เตรียมระบบ
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    master_df = load_master_data()
    ai_engine = AIReader()
    
    # 2. คัดเลือกงาน (Queue)
    work_queue = master_df.head(TEST_LIMIT) if TEST_LIMIT else master_df
    results = []
    
    print(f"🚀 Starting process for {len(work_queue)} documents...")
    
    # 3. เริ่มลูปงาน
    for _, row in tqdm(work_queue.iterrows(), total=len(work_queue)):
        filename = row['document_name']
        pdf_path = os.path.join(PDF_DIR, filename)
        
        if os.path.exists(pdf_path):
            # สั่ง AI ทำงาน
            data = ai_engine.extract_data(pdf_path, row['nacc_id'])
            results.append(data)
        else:
            # บันทึกว่าหาไฟล์ไม่เจอ
            results.append({"nacc_id": row['nacc_id'], "error": "PDF Not Found"})

    # 4. บันทึกผลลัพธ์
    output_path = os.path.join(OUTPUT_DIR, "submission_result.csv")
    pd.DataFrame(results).to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n🎉 Done! Results saved at: {output_path}")

if __name__ == "__main__":
    main()