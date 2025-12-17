"""
Data processing pipeline for BKW automation.

Handles ZIP extraction, Excel to CSV conversion, and batch processing.
"""

import pandas as pd
import logging
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .formatters import formatdkw
from .catalog import match_file_to_tr_id, build_filename

logger = logging.getLogger(__name__)


def extract_zip_file(zip_path: Path, extract_dir: Path, verbose: bool = False) -> List[Path]:
    """
    Extract ZIP file and return list of Excel files.
    
    Args:
        zip_path: Path to ZIP file
        extract_dir: Directory to extract to
        verbose: Enable detailed logging
        
    Returns:
        List of extracted Excel file paths
    """
    # Clean extract directory
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        logger.info(f"Extracting ZIP: {zip_path.name}")
        logger.info(f"Extract to: {extract_dir}")
    
    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)
    
    # Find Excel files
    excel_files = list(extract_dir.rglob('*.xlsx')) + list(extract_dir.rglob('*.xls'))
    
    if verbose:
        logger.info(f"Found {len(excel_files)} Excel file(s)")
        for f in excel_files:
            logger.info(f"  - {f.name}")
    
    return excel_files


def process_excel_file(excel_path: Path,
                       tr_id: Optional[str],
                       date_str: str,
                       local_output_folder: Path,
                       onedrive_output_folder: Path,
                       apply_formatting: bool = True,
                       verbose: bool = False) -> Tuple[bool, Dict]:
    """
    Process a single Excel file: load, format, save as CSV.
    
    Args:
        excel_path: Path to Excel file
        tr_id: Technical Resource ID (or None for fallback naming)
        date_str: Date string for filename
        local_output_folder: Local output directory
        onedrive_output_folder: OneDrive output directory
        apply_formatting: Whether to apply formatdkw transformation
        verbose: Enable detailed logging
        
    Returns:
        Tuple of (success: bool, info: dict)
    """
    info = {
        'source': excel_path.name,
        'tr_id': tr_id,
        'success': False,
        'error': None
    }
    
    try:
        # Load Excel
        df = pd.read_excel(excel_path)
        
        if verbose:
            logger.info(f"Loaded {excel_path.name}: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Build filename
        if tr_id:
            csv_name = build_filename(tr_id, date_str)
        else:
            csv_name = f"{excel_path.stem}_{date_str}.csv"
        
        info['output'] = csv_name
        
        # Apply formatting
        if apply_formatting:
            df = formatdkw(df)
            if verbose:
                logger.info("Applied formatdkw transformation")
        
        info['rows'] = len(df)
        
        # Save to both locations
        local_path = local_output_folder / csv_name
        onedrive_path = onedrive_output_folder / csv_name
        
        df.to_csv(local_path, index=False, sep=';')
        df.to_csv(onedrive_path, index=False, sep=';')
        
        file_size = local_path.stat().st_size / 1024
        info['size_kb'] = file_size
        
        if verbose:
            logger.info(f"Saved: {csv_name} ({file_size:.2f} KB)")
            logger.info(f"  - Local: {local_output_folder}")
            logger.info(f"  - OneDrive: {onedrive_output_folder}")
        
        info['success'] = True
        
    except Exception as e:
        info['error'] = str(e)
        logger.error(f"Error processing {excel_path.name}: {e}")
    
    return info['success'], info


def process_daily_data(source_folder: Path,
                      catalog: pd.DataFrame,
                      local_output_dir: Path,
                      onedrive_output_dir: Path,
                      date_str: str,
                      verbose: bool = False,
                      allow_fallback: bool = False) -> Dict:
    """
    Process all data for a given date.
    
    Args:
        source_folder: Folder containing date subdirectory with ZIP
        catalog: Catalog DataFrame
        local_output_dir: Base local output directory
        onedrive_output_dir: Base OneDrive output directory
        date_str: Date string (dd-mm-YYYY)
        verbose: Enable detailed logging
        
    Returns:
        Processing summary dictionary
    """
    summary = {
        'total_files': 0,
        'successful': 0,
        'failed': 0,
        'files': [],
        'processed_paths': []
    }
    
    today_folder = source_folder / date_str
    
    logger.info("=" * 80)
    logger.info("PROCESSING DAILY DATA")
    logger.info("=" * 80)
    logger.info(f"Date: {date_str}")
    logger.info(f"Source: {today_folder}")
    logger.info("=" * 80)
    
    # Validate folder exists
    if not today_folder.exists():
        logger.error(f"Date folder not found: {today_folder}")
        return summary
    
    # Find ZIP file (validate it's actually a ZIP)
    zip_candidates = sorted(today_folder.glob('*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not zip_candidates:
        logger.error(f"No ZIP files found in: {today_folder}")
        return summary
    
    # Validate the ZIP file is actually valid
    zip_path = None
    for candidate in zip_candidates:
        if zipfile.is_zipfile(candidate):
            zip_path = candidate
            break
        else:
            logger.warning(f"Skipping invalid ZIP file: {candidate.name}")
    
    if zip_path is None:
        logger.error(f"No valid ZIP files found in: {today_folder}")
        return summary
    
    logger.info(f"\n✓ Found ZIP: {zip_path.name}\n")
    
    # Extract ZIP
    extract_dir = local_output_dir / f"extracted_{date_str}"
    excel_files = extract_zip_file(zip_path, extract_dir, verbose=verbose)
    
    summary['total_files'] = len(excel_files)
    
    if not excel_files:
        logger.warning("No Excel files found in ZIP")
        return summary
    
    # Validate catalog coverage
    from .catalog import validate_catalog_coverage
    validate_catalog_coverage(catalog, excel_files, verbose=verbose)
    
    # Create date-based output folders
    local_date_folder = local_output_dir / date_str
    onedrive_date_folder = onedrive_output_dir / date_str
    
    local_date_folder.mkdir(parents=True, exist_ok=True)
    onedrive_date_folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n📦 Processing {len(excel_files)} file(s)...\n")
    
    # Process each file
    for idx, excel_file in enumerate(excel_files, 1):
        logger.info(f"[{idx}/{len(excel_files)}] {excel_file.name}")
        
        # Match to catalog
        tr_id, matched_name = match_file_to_tr_id(excel_file.stem, catalog, verbose=verbose)
        
        if tr_id:
            logger.info(f"  ✓ Matched: {matched_name} → {tr_id}")
        else:
            if not allow_fallback:
                logger.warning("  ⚠ No catalog match, skipping file (fallback disabled)")
                summary['failed'] += 1
                summary['files'].append({
                    'source': excel_file.name,
                    'output': None,
                    'tr_id': None,
                    'rows': 0,
                    'size_kb': 0,
                    'success': False,
                    'error': 'No catalog match'
                })
                print()
                continue
            logger.warning(f"  ⚠ No catalog match, using fallback name")
        
        # Process
        success, info = process_excel_file(
            excel_file,
            tr_id,
            date_str,
            local_date_folder,
            onedrive_date_folder,
            apply_formatting=True,
            verbose=verbose
        )
        
        if success:
            summary['successful'] += 1
            summary['processed_paths'].append(local_date_folder / info['output'])
        else:
            summary['failed'] += 1
            logger.error(f"  ✗ {info['error']}")
        
        summary['files'].append(info)
        print()
    
    # Summary
    logger.info("=" * 80)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total files: {summary['total_files']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info("=" * 80)
    
    if summary['files'] and verbose:
        logger.info("\n📋 Processed Files:")
        for item in summary['files']:
            if item['success']:
                logger.info(f"  • {item['source']} → {item['output']}")
                logger.info(f"    TR-ID: {item['tr_id']}, Rows: {item['rows']}, Size: {item['size_kb']:.2f} KB")
    
    return summary
