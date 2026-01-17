
import pandas as pd
from pathlib import Path
from typing import Optional, Literal, Any

class FileManager:
    """File manager for course exchange data storage."""
    
    def __init__(self, base_dir: str = "data"):
        """
        Initialize file manager with base directory.
        
        Args:
            base_dir: Base directory for data files (default: "data")
        """
        self.base_dir = Path(base_dir)
        self.nus_path = self.base_dir / "nus.csv"
        self.pu_path = self.base_dir / "pu.csv"
        self.mapping_path = self.base_dir / "mapping.csv"
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, file_type: Literal['nus', 'pu', 'mapping']) -> Path:
        """Get the path for a specific file type."""
        path_map = {
            'nus': self.nus_path,
            'pu': self.pu_path,
            'mapping': self.mapping_path
        }
        return path_map[file_type]
    
    # ==================== Base Read/Write Methods ====================
    
    def _read_csv(self, file_type: Literal['nus', 'pu', 'mapping']) -> Optional[pd.DataFrame]:
        """
        Base method to read CSV file.
        
        Args:
            file_type: Type of file to read ('nus', 'pu', or 'mapping')
            
        Returns:
            DataFrame if file exists, None otherwise
            
        Raises:
            IOError: If file exists but cannot be read
        """
        path = self._get_path(file_type)
        
        if not path.exists():
            return None
        
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise IOError(f"Failed to read {file_type} data from {path}. Data is untouched. Error: {e}")
    
    def _write_csv(self, df: pd.DataFrame, file_type: Literal['nus', 'pu', 'mapping']) -> None:
        """
        Base method to write CSV file. Creates file if it doesn't exist.
        
        Args:
            df: DataFrame to write
            file_type: Type of file to write ('nus', 'pu', or 'mapping')
            
        Raises:
            IOError: If write operation fails
        """
        path = self._get_path(file_type)
        
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
        except Exception as e:
            raise IOError(f"Failed to write {file_type} data to {path}. Data is untouched. Error: {e}")
    
    def _import_csv(self, filepath: str, file_type: Literal['nus', 'pu', 'mapping']) -> pd.DataFrame:
        """
        Base method to import CSV from external file.
        
        Args:
            filepath: Path to source CSV file
            file_type: Type of file to import ('nus', 'pu', or 'mapping')
            
        Returns:
            DataFrame that was imported
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            IOError: If file cannot be read
        """
        source_path = Path(filepath)
        
        if not source_path.exists():
            raise FileNotFoundError(
                f"Import failed: Source file not found at {filepath}. Data is untouched."
            )
        
        try:
            df = pd.read_csv(source_path)
        except Exception as e:
            raise IOError(
                f"Import failed: Cannot read file at {filepath}. Data is untouched. Error: {e}"
            )
        
        return df
    
    def _export_csv(self, filepath: str, file_type: Literal['nus', 'pu', 'mapping']) -> None:
        """
        Base method to export CSV to external file.
        
        Args:
            filepath: Destination path for CSV file
            file_type: Type of file to export ('nus', 'pu', or 'mapping')
            
        Raises:
            FileNotFoundError: If source data doesn't exist
            IOError: If file cannot be written
        """
        df = self._read_csv(file_type)
        source_path = self._get_path(file_type)
        
        if df is None:
            raise FileNotFoundError(
                f"Export failed: No {file_type} data found at {source_path}. Data is untouched."
            )
        
        try:
            export_path = Path(filepath)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(export_path, index=False)
        except Exception as e:
            raise IOError(
                f"Export failed: Cannot write to {filepath}. Data is untouched. Error: {e}"
            )
    
    # ==================== Read Operations ====================
    
    def read_nus(self) -> Optional[pd.DataFrame]:
        return self._read_csv('nus')
    
    def read_pu(self) -> Optional[pd.DataFrame]:
        return self._read_csv('pu')
    
    def read_mapping(self) -> Optional[pd.DataFrame]:
        return self._read_csv('mapping')
    
    def read_all(self) -> dict:
        return {
            'nus': self.read_nus(),
            'pu': self.read_pu(),
            'mapping': self.read_mapping()
        }
    
    # ==================== Write Operations ====================
    
    def write_nus(self, df: pd.DataFrame) -> None:
        self._write_csv(df, 'nus')
    
    def write_pu(self, df: pd.DataFrame) -> None:
        self._write_csv(df, 'pu')
    
    def write_mapping(self, df: pd.DataFrame) -> None:
        self._write_csv(df, 'mapping')
    
    def write_all(self, nus_df: pd.DataFrame, pu_df: pd.DataFrame, mapping_df: pd.DataFrame) -> None:
        self.write_nus(nus_df)
        self.write_pu(pu_df)
        self.write_mapping(mapping_df)
    
    # ==================== Import/Export Operations ====================
    
    def import_nus(self, filepath: str) -> pd.DataFrame:
        return self._import_csv(filepath, 'nus')
    
    def import_pu(self, filepath: str) -> pd.DataFrame:
        return self._import_csv(filepath, 'pu')
    
    def export_mapping(self, filepath: str) -> None:
        self._export_csv(filepath, 'mapping')


    def import_external_file(self, file_source: Any) -> pd.DataFrame:
        """
        Reads a CSV from a Streamlit UploadedFile object or a string path.
        """
        try:
            return pd.read_csv(file_source)
        except Exception as e:
            raise IOError(f"Could not read the selected CSV file. Error: {e}")

    def get_export_buffer(self, file_type: Literal['nus', 'pu', 'mapping']) -> str:
        """
        Converts internal data to a CSV string for browser downloading.
        """
        df = self._read_csv(file_type)
        if df is None or df.empty:
            return ""
        return df.to_csv(index=False)