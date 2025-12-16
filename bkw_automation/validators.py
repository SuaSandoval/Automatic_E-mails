"""
Data validation utilities for BKW automation.

Handles output verification and quality checks.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def verify_csv_file(csv_path: Path, verbose: bool = False) -> Dict:
    """
    Verify a CSV file and return quality metrics.
    
    Args:
        csv_path: Path to CSV file
        verbose: Enable detailed logging
        
    Returns:
        Dictionary with verification results
    """
    results = {
        'file': csv_path.name,
        'path': str(csv_path),
        'exists': csv_path.exists(),
        'valid': False
    }
    
    if not csv_path.exists():
        logger.error(f"File not found: {csv_path}")
        return results
    
    try:
        # Load CSV
        df = pd.read_csv(csv_path, sep=';')
        
        # Basic metrics
        results.update({
            'valid': True,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum())
        })
        
        # Data types
        results['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Status distribution (if applicable)
        if 'status' in df.columns:
            results['status_distribution'] = df['status'].value_counts().to_dict()
        
        # Timestamp validation (if applicable)
        if 'timestamp' in df.columns:
            # Check format
            sample_timestamps = df['timestamp'].head(5).tolist()
            results['timestamp_format'] = 'ISO 8601 with Z' if all('Z' in str(t) for t in sample_timestamps if pd.notna(t)) else 'Other'
        
        if verbose:
            logger.info(f"\n📄 {csv_path.name}")
            logger.info(f"   Rows: {results['rows']:,}")
            logger.info(f"   Columns: {results['columns']}")
            logger.info(f"   Missing values: {results['missing_values']}")
            logger.info(f"   Duplicates: {results['duplicate_rows']}")
            
            if 'status_distribution' in results:
                logger.info(f"   Status distribution: {results['status_distribution']}")
        
    except Exception as e:
        results['error'] = str(e)
        logger.error(f"Error verifying {csv_path.name}: {e}")
    
    return results


def check_data_quality(df: pd.DataFrame, verbose: bool = False) -> Dict:
    """
    Perform comprehensive data quality checks.
    
    Args:
        df: DataFrame to check
        verbose: Enable detailed logging
        
    Returns:
        Dictionary with quality metrics
    """
    quality = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'missing_values_total': int(df.isnull().sum().sum()),
        'missing_by_column': df.isnull().sum().to_dict(),
        'duplicate_rows': int(df.duplicated().sum()),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    
    # Completeness percentage
    total_cells = df.shape[0] * df.shape[1]
    quality['completeness_pct'] = round((1 - quality['missing_values_total'] / total_cells) * 100, 2) if total_cells > 0 else 100
    
    # Column-specific checks
    if 'timestamp' in df.columns:
        quality['timestamp_nulls'] = int(df['timestamp'].isnull().sum())
        quality['timestamp_unique'] = int(df['timestamp'].nunique())
    
    if 'value' in df.columns:
        quality['value_nulls'] = int(df['value'].isnull().sum())
        quality['value_range'] = {
            'min': float(df['value'].min()) if not df['value'].isnull().all() else None,
            'max': float(df['value'].max()) if not df['value'].isnull().all() else None,
            'mean': float(df['value'].mean()) if not df['value'].isnull().all() else None
        }
    
    if 'status' in df.columns:
        quality['status_distribution'] = df['status'].value_counts().to_dict()
    
    if verbose:
        logger.info("\n🔍 Data Quality Report:")
        logger.info(f"   Total rows: {quality['total_rows']:,}")
        logger.info(f"   Total columns: {quality['total_columns']}")
        logger.info(f"   Completeness: {quality['completeness_pct']}%")
        logger.info(f"   Missing values: {quality['missing_values_total']}")
        logger.info(f"   Duplicate rows: {quality['duplicate_rows']}")
        
        if 'status_distribution' in quality:
            logger.info(f"   Status distribution: {quality['status_distribution']}")
    
    return quality


def generate_processing_summary(processed_files: List[Path], 
                                verbose: bool = False) -> Dict:
    """
    Generate summary of processed files with aggregated metrics.
    
    Args:
        processed_files: List of processed CSV file paths
        verbose: Enable detailed logging
        
    Returns:
        Summary dictionary
    """
    summary = {
        'total_files': len(processed_files),
        'total_size_kb': 0,
        'total_rows': 0,
        'files': []
    }
    
    for csv_path in processed_files:
        verification = verify_csv_file(csv_path, verbose=False)
        
        if verification['valid']:
            file_size_kb = csv_path.stat().st_size / 1024
            summary['total_size_kb'] += file_size_kb
            summary['total_rows'] += verification['rows']
            
            summary['files'].append({
                'name': verification['file'],
                'rows': verification['rows'],
                'size_kb': round(file_size_kb, 2)
            })
    
    summary['total_size_mb'] = round(summary['total_size_kb'] / 1024, 2)
    
    if verbose:
        logger.info("\n📊 Processing Summary:")
        logger.info(f"   Total files: {summary['total_files']}")
        logger.info(f"   Total rows: {summary['total_rows']:,}")
        logger.info(f"   Total size: {summary['total_size_mb']} MB")
        
        logger.info("\n   Files:")
        for file_info in summary['files']:
            logger.info(f"     • {file_info['name']}: {file_info['rows']:,} rows ({file_info['size_kb']:.2f} KB)")
    
    return summary


def display_sample_data(csv_path: Path, n_rows: int = 5) -> None:
    """
    Display sample data from CSV file.
    
    Args:
        csv_path: Path to CSV file
        n_rows: Number of rows to display from head/tail
    """
    if not csv_path.exists():
        logger.error(f"File not found: {csv_path}")
        return
    
    try:
        df = pd.read_csv(csv_path, sep=';')
        
        logger.info(f"\n📝 Sample data from {csv_path.name}:")
        logger.info(f"\nFirst {n_rows} rows:")
        print(df.head(n_rows).to_string())
        
        logger.info(f"\nLast {n_rows} rows:")
        print(df.tail(n_rows).to_string())
        
    except Exception as e:
        logger.error(f"Error displaying sample data: {e}")
