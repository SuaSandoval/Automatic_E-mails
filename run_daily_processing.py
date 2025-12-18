"""
Daily BKW Data Processing Script

Automated script to process BKW data from OneDrive.
Runs the full pipeline: catalog loading, data extraction, processing, and validation.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

import pandas as pd
from dotenv import load_dotenv

# Ensure console can handle UTF-8 (prevents UnicodeEncodeError on Windows terminals)
try:  # pragma: no cover
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Add project root to Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configure logging
log_dir = project_root / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Ensure console logs are ASCII-safe (Windows consoles may not handle emojis)
class _AsciiFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = str(record.msg).encode('ascii', 'replace').decode('ascii')
        except Exception:
            record.msg = str(record.msg)
        return True

for _handler in logging.getLogger().handlers:
    if isinstance(_handler, logging.StreamHandler):
        _handler.addFilter(_AsciiFilter())

logger = logging.getLogger(__name__)

# Import BKW automation modules
from bkw_automation.catalog import load_catalog
from bkw_automation.processors import process_daily_data
from bkw_automation.validators import verify_csv_file, generate_processing_summary


def main():
    """Main processing function."""
    logger.info("=" * 80)
    logger.info("BKW DAILY PROCESSING STARTED")
    logger.info("=" * 80)
    
    try:
        # ====================================================================
        # CONTROL VARIABLES
        # ====================================================================
        VERBOSE = False               # Set to False to reduce logging output
        PROCESS_DATE = None          # Set to 'dd-mm-YYYY' for specific date, or None for today
        ALLOW_FALLBACK = False       # If False, skip files not found in catalog
        SAVE_TO_ONEDRIVE = True      # Set to False to only save locally (sync OneDrive separately)
        # ====================================================================
        # PATH CONFIGURATION
        # ====================================================================
        ONEDRIVE_FOLDER = Path(os.getenv('ONEDRIVE_FOLDER', Path.home() / 'OneDrive'))
        DATA_SUBFOLDER = Path(os.getenv('DATA_SUBFOLDER', 'Data'))
        OUTPUT_SUBFOLDER = Path(os.getenv('OUTPUT_SUBFOLDER', 'Processed'))
        CATALOGUE_SUBFOLDER = Path(os.getenv('CATALOGUE_SUBFOLDER', 'Catalogue'))
        
        # Resolve full paths
        DATA_SOURCE_DIR = DATA_SUBFOLDER if DATA_SUBFOLDER.is_absolute() else ONEDRIVE_FOLDER / DATA_SUBFOLDER
        OUTPUT_DIR = OUTPUT_SUBFOLDER if OUTPUT_SUBFOLDER.is_absolute() else ONEDRIVE_FOLDER / OUTPUT_SUBFOLDER
        CATALOGUE_DIR = CATALOGUE_SUBFOLDER if CATALOGUE_SUBFOLDER.is_absolute() else ONEDRIVE_FOLDER / CATALOGUE_SUBFOLDER
        LOCAL_OUTPUT_DIR = project_root / 'data' / 'output'
        
        # Create directories
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Configuration loaded")
        logger.info(f"  Data source: {DATA_SOURCE_DIR}")
        logger.info(f"  Output: {OUTPUT_DIR}")
        logger.info(f"  Log file: {log_file}")
        
        # ====================================================================
        # LOAD CATALOG
        # ====================================================================
        catalog_file = CATALOGUE_DIR / 'codeids.csv'
        catalog = load_catalog(catalog_file, verbose=VERBOSE)
        
        if catalog is None:
            logger.error(f"Failed to load catalog from: {CATALOGUE_DIR}")
            return 1
        
        logger.info(f"✓ Catalog loaded: {len(catalog)} entries")
        
        # ====================================================================
        # PROCESS DATA
        # ====================================================================
        today_str = PROCESS_DATE if PROCESS_DATE else datetime.now().strftime('%d-%m-%Y')
        logger.info(f"Processing date: {today_str}")
        
        # Use local output only if OneDrive sync disabled
        onedrive_output = OUTPUT_DIR if SAVE_TO_ONEDRIVE else LOCAL_OUTPUT_DIR
        
        processing_summary = process_daily_data(
            source_folder=DATA_SOURCE_DIR,
            catalog=catalog,
            local_output_dir=LOCAL_OUTPUT_DIR,
            onedrive_output_dir=onedrive_output,
            date_str=today_str,
            verbose=VERBOSE,
            allow_fallback=ALLOW_FALLBACK
        )
        
        processed_files = processing_summary.get('processed_paths', [])
        logger.info(f"\n✓ Processed {processing_summary['successful']}/{processing_summary['total_files']} files")
        
        # ====================================================================
        # VERIFY OUTPUT
        # ====================================================================
        if processed_files:
            summary = generate_processing_summary(processed_files, verbose=VERBOSE)
            
            # Verify first file
            sample_file = processed_files[0]
            verification = verify_csv_file(sample_file, verbose=VERBOSE)
            
            if verification['valid']:
                logger.info(f"✓ Validation passed for: {sample_file.name}")
            else:
                logger.warning(f"⚠ Validation issues in: {sample_file.name}")
        else:
            logger.warning("⚠ No files were processed")
        
        logger.info("=" * 80)
        logger.info("BKW DAILY PROCESSING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        return 0
        
    except Exception as e:
        logger.error(f"PROCESSING FAILED: {e}", exc_info=True)
        logger.info("=" * 80)
        logger.info("BKW DAILY PROCESSING FAILED")
        logger.info("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
