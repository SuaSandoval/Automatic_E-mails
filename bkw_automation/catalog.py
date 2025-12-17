"""
Catalog management for BKW automation.

Handles loading, validation, and TR-ID matching against the codeids.csv catalog.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)


def load_catalog(catalog_path: Path, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Load the TR-ID catalog from CSV file.
    
    Args:
        catalog_path: Path to codeids.csv
        verbose: Enable detailed logging
        
    Returns:
        DataFrame with catalog or None if not found
    """
    if not catalog_path.exists():
        logger.error(f"Catalog not found: {catalog_path}")
        return None
    
    # Try different encodings (common for German characters)
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    catalog = None
    
    for encoding in encodings:
        try:
            catalog = pd.read_csv(catalog_path, encoding=encoding)
            if verbose:
                logger.info(f"Loaded catalog with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if catalog is None:
        logger.error(f"Failed to load catalog with any encoding: {encodings}")
        return None
    
    if verbose:
        logger.info(f"Loaded catalog: {len(catalog)} entries")
        logger.info(f"Columns: {list(catalog.columns)}")
    
    # Validate required columns
    required_cols = ['Name', 'Technische Ressourcen-ID']
    missing_cols = [col for col in required_cols if col not in catalog.columns]
    
    if missing_cols:
        logger.error(f"Catalog missing required columns: {missing_cols}")
        return None
    
    return catalog


def match_file_to_tr_id(filename: str, catalog: pd.DataFrame, verbose: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """
    Match a filename to a TR-ID using the catalog.
    
    Args:
        filename: Excel filename (stem, without extension)
        catalog: Catalog DataFrame
        verbose: Enable detailed logging
        
    Returns:
        Tuple of (tr_id, matched_name) or (None, None) if no match
    """
    for _, row in catalog.iterrows():
        name = str(row['Name'])
        if name in filename:
            tr_id = row['Technische Ressourcen-ID']
            if verbose:
                logger.info(f"Matched '{filename}' → {name} → {tr_id}")
            return tr_id, name
    
    if verbose:
        logger.warning(f"No catalog match for: {filename}")
    
    return None, None


def validate_catalog_coverage(catalog: pd.DataFrame, 
                              excel_files: List[Path], 
                              verbose: bool = False) -> Dict:
    """
    Validate bidirectional coverage between catalog and data files.
    
    Checks:
    - Which catalog entries have corresponding files
    - Which files have no catalog match
    
    Args:
        catalog: Catalog DataFrame
        excel_files: List of Excel file paths
        verbose: Enable detailed logging
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'catalog_with_files': [],
        'catalog_without_files': [],
        'files_with_match': [],
        'files_without_match': [],
        'total_catalog_entries': len(catalog),
        'total_files': len(excel_files)
    }
    
    # Check which catalog entries have files
    for _, row in catalog.iterrows():
        name = str(row['Name'])
        tr_id = row['Technische Ressourcen-ID']
        
        has_file = any(name in f.stem for f in excel_files)
        
        if has_file:
            results['catalog_with_files'].append({'name': name, 'tr_id': tr_id})
        else:
            results['catalog_without_files'].append({'name': name, 'tr_id': tr_id})
    
    # Check which files have catalog matches
    for excel_file in excel_files:
        tr_id, matched_name = match_file_to_tr_id(excel_file.stem, catalog, verbose=False)
        
        if tr_id:
            results['files_with_match'].append({
                'file': excel_file.name,
                'tr_id': tr_id,
                'matched_name': matched_name
            })
        else:
            results['files_without_match'].append({'file': excel_file.name})
    
    # Logging
    if verbose or results['catalog_without_files'] or results['files_without_match']:
        logger.info("=" * 80)
        logger.info("CATALOG COVERAGE VALIDATION")
        logger.info("=" * 80)
        
        logger.info(f"\n📊 Catalog entries: {results['total_catalog_entries']}")
        logger.info(f"   - With matching files: {len(results['catalog_with_files'])}")
        logger.info(f"   - Without files: {len(results['catalog_without_files'])}")
        
        if results['catalog_without_files']:
            logger.warning("\n⚠ Catalog entries WITHOUT corresponding files:")
            for entry in results['catalog_without_files']:
                logger.warning(f"   - {entry['name']} ({entry['tr_id']})")
        
        logger.info(f"\n📦 Data files: {results['total_files']}")
        logger.info(f"   - With catalog match: {len(results['files_with_match'])}")
        logger.info(f"   - Without match: {len(results['files_without_match'])}")
        
        if results['files_without_match']:
            logger.warning("\n⚠ Files WITHOUT catalog match:")
            for entry in results['files_without_match']:
                logger.warning(f"   - {entry['file']}")
        
        logger.info("=" * 80)
    
    return results


def build_filename(tr_id: str, date_str: str, suffix: str = "WindgeschwIstAnlage") -> str:
    """
    Build BKW-compliant filename.
    
    Format: tecres_<TR-ID>_<suffix>_<date>.csv
    
    Args:
        tr_id: Technical Resource ID (e.g., D1025649750)
        date_str: Date string (e.g., 16-12-2025)
        suffix: Middle part of filename (default: WindgeschwIstAnlage)
        
    Returns:
        Formatted filename
    """
    return f"tecres_{tr_id}_{suffix}_{date_str}.csv"
