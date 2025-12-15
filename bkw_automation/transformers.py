"""
Data transformation module for Excel files.

Handles column name cleaning, data validation, and type conversions.
"""

import pandas as pd
import logging
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform and clean Excel data from Rotoforst files."""
    
    def __init__(self):
        """Initialize the transformer."""
        self.original_df: Optional[pd.DataFrame] = None
        self.transformed_df: Optional[pd.DataFrame] = None
        
    def load_excel(self, file_path: str) -> pd.DataFrame:
        """
        Load an Excel file into a DataFrame.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            DataFrame with loaded data
        """
        try:
            self.original_df = pd.read_excel(file_path)
            logger.info(f"✓ Loaded Excel file: {file_path}")
            logger.info(f"  Shape: {self.original_df.shape[0]} rows × {self.original_df.shape[1]} columns")
            return self.original_df
        except Exception as e:
            logger.error(f"✗ Failed to load Excel file: {e}")
            raise
    
    def clean_column_names(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Clean column names.
        
        Transformations:
        - Strip leading/trailing whitespace
        - Convert to lowercase
        - Replace spaces with underscores
        - Remove special characters
        
        Args:
            df: DataFrame to clean (uses self.original_df if None)
            
        Returns:
            DataFrame with cleaned columns
        """
        if df is None:
            df = self.original_df.copy()
        else:
            df = df.copy()
            
        df.columns = (df.columns
                      .str.strip()
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('[^a-z0-9_]', '', regex=True))
        
        logger.info("✓ Cleaned column names")
        return df
    
    def rename_columns(self, df: pd.DataFrame, 
                      mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Apply custom column name mapping.
        
        Args:
            df: DataFrame to rename
            mapping: Dictionary of old_name -> new_name
            
        Returns:
            DataFrame with renamed columns
        """
        df = df.rename(columns=mapping)
        logger.info(f"✓ Applied custom column mapping ({len(mapping)} columns)")
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize data values.
        
        Operations:
        - Strip whitespace from string columns
        - Convert datetime columns
        - Remove duplicates
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Strip whitespace from string columns
        string_cols = df.select_dtypes(include=['object']).columns
        for col in string_cols:
            df[col] = df[col].astype(str).str.strip()
        logger.info(f"✓ Stripped whitespace from {len(string_cols)} columns")
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        removed = initial_rows - len(df)
        if removed > 0:
            logger.info(f"✓ Removed {removed} duplicate rows")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame,
                             strategy: str = 'drop',
                             fill_value: Optional[str] = None) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.
        
        Args:
            df: DataFrame to process
            strategy: 'drop' to remove rows with NaN, 'fill' to fill with value
            fill_value: Value to use when strategy='fill'
            
        Returns:
            DataFrame with handled missing values
        """
        df = df.copy()
        
        if strategy == 'drop':
            initial_rows = len(df)
            df = df.dropna()
            removed = initial_rows - len(df)
            if removed > 0:
                logger.info(f"✓ Removed {removed} rows with missing values")
        elif strategy == 'fill':
            df = df.fillna(fill_value or 'N/A')
            logger.info(f"✓ Filled missing values with: {fill_value or 'N/A'}")
        
        return df
    
    def transform(self, df: Optional[pd.DataFrame] = None,
                 column_mapping: Optional[Dict[str, str]] = None,
                 missing_value_strategy: str = 'drop') -> pd.DataFrame:
        """
        Full transformation pipeline.
        
        Args:
            df: DataFrame to transform (uses self.original_df if None)
            column_mapping: Custom column name mapping
            missing_value_strategy: How to handle missing values
            
        Returns:
            Transformed DataFrame
        """
        if df is None:
            df = self.original_df.copy()
        else:
            df = df.copy()
        
        # Step 1: Clean column names
        df = self.clean_column_names(df)
        
        # Step 2: Apply custom mapping if provided
        if column_mapping:
            df = self.rename_columns(df, column_mapping)
        
        # Step 3: Clean data
        df = self.clean_data(df)
        
        # Step 4: Handle missing values
        df = self.handle_missing_values(df, strategy=missing_value_strategy)
        
        self.transformed_df = df
        logger.info(f"✓ Transformation complete: {len(df)} rows × {len(df.columns)} columns")
        
        return df
    
    def validate(self) -> Dict[str, any]:
        """
        Validate the transformed data.
        
        Returns:
            Dictionary with validation results
        """
        if self.transformed_df is None:
            logger.error("No transformed data to validate")
            return {"valid": False, "error": "No transformed data"}
        
        results = {
            "valid": True,
            "row_count": len(self.transformed_df),
            "column_count": len(self.transformed_df.columns),
            "missing_values": self.transformed_df.isnull().sum().sum(),
            "duplicates": self.transformed_df.duplicated().sum(),
        }
        
        logger.info(f"✓ Validation complete: {results}")
        return results
    
    def export_csv(self, file_path: str) -> None:
        """
        Export transformed data to CSV.
        
        Args:
            file_path: Output file path
        """
        if self.transformed_df is None:
            logger.error("No transformed data to export")
            return
        
        self.transformed_df.to_csv(file_path, index=False)
        logger.info(f"✓ Exported to CSV: {file_path}")
    
    def export_excel(self, file_path: str) -> None:
        """
        Export transformed data to Excel.
        
        Args:
            file_path: Output file path
        """
        if self.transformed_df is None:
            logger.error("No transformed data to export")
            return
        
        self.transformed_df.to_excel(file_path, index=False, sheet_name='Data')
        logger.info(f"✓ Exported to Excel: {file_path}")
