import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

POPPLER_PATH = os.path.join(BASE_DIR, 'poppler', 'Library', 'bin')


PDF_DIR = os.path.join(DATA_DIR, '1_raw_pdf')
METADATA_DIR = os.path.join(DATA_DIR, '2_metadata')
ENUM_DIR = os.path.join(DATA_DIR, '3_enums')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

DOC_INFO_FILE = os.path.join(METADATA_DIR, "Train_doc_info.csv")
NACC_DETAIL_FILE = os.path.join(METADATA_DIR, "Train_nacc_detail.csv")

TEST_LIMIT = None