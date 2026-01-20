
import pandas as pd
from pathlib import Path
from typing import Optional, Literal, Any, Union

class FileManager:
    """File manager for course exchange data storage."""
    
    def __init__(self, base_dir: str = "data"):
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
    
    def _read_file(self, file_type: Literal['nus', 'pu', 'mapping']) -> pd.DataFrame:
        path = self._get_path(file_type)
        
        if not path.exists():
            return pd.DataFrame()
        
        try:
            if path.suffix.lower() == '.csv':
                return pd.read_csv(path)
            elif path.suffix.lower() == '.json':
                return pd.read_json(path)
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
        except Exception as e:
            raise IOError(f"Failed to read {file_type} data from {path}. Data is untouched. Error: {e}")
    
    def _write_file(self, df: pd.DataFrame, file_type: Literal['nus', 'pu', 'mapping']) -> None:
        path = self._get_path(file_type)
        
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix.lower() == '.csv':
                df.to_csv(path, index=False)
            elif path.suffix.lower() == '.json':
                df.to_json(path, orient='records', indent=2)
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
        except Exception as e:
            raise IOError(f"Failed to write {file_type} data to {path}. Data is untouched. Error: {e}")
    
    def _import_file(self, file_source: Any, file_type: Literal['nus', 'pu', 'mapping']) -> pd.DataFrame:
        """
        Import data from a file-like object (e.g., Streamlit UploadedFile, BytesIO).
        
        Parameters:
        -----------
        file_source : file-like object
            File object to read from (e.g., UploadedFile, BytesIO)
        file_type : Literal['nus', 'pu', 'mapping']
            Type of file being imported
        
        Returns:
        --------
        pd.DataFrame
            Imported data
        """
        try:
            # Try to get filename to determine file type
            filename = getattr(file_source, 'name', '')
            
            if filename.endswith('.csv') or not filename:
                # Default to CSV if no extension or .csv
                return pd.read_csv(file_source)
            elif filename.endswith('.json'):
                return pd.read_json(file_source)
            else:
                raise ValueError(f"Unsupported file type: {filename}")
        except Exception as e:
            raise IOError(
                f"Import failed: Cannot read file object. Data is untouched. Error: {e}"
            )


    def _export_file(self, file_destination: Any, file_type: Literal['nus', 'pu', 'mapping']) -> None:
        """
        Export data to a file-like object.
        
        Parameters:
        -----------
        file_destination : file-like object
            Writable file object (e.g., BytesIO)
        file_type : Literal['nus', 'pu', 'mapping']
            Type of file being exported
        """
        df = self._read_file(file_type)
        
        if df is None:
            raise FileNotFoundError(
                f"Export failed: No {file_type} data found. Data is untouched."
            )
        
        try:
            # Try to determine format from filename attribute
            filename = getattr(file_destination, 'name', '')
            
            if filename.endswith('.json'):
                df.to_json(file_destination, orient='records', indent=2)
            else:
                # Default to CSV
                df.to_csv(file_destination, index=False)
        except Exception as e:
            raise IOError(
                f"Export failed: Cannot write to file object. Data is untouched. Error: {e}"
            )


    def get_export_buffer(self, file_type: Literal['nus', 'pu', 'mapping'], format) -> Union[str, bytes]:
        """
        Converts internal data to a string/bytes buffer for browser downloading.
        
        Parameters:
        -----------
        file_type : Literal['nus', 'pu', 'mapping']
            Type of data to export
        format : str
            Export format ('csv' or 'json')
        
        Returns:
        --------
        str or bytes
            CSV string or JSON string
        """
        df = self._read_file(file_type)
        
        if df is None or df.empty:
            return ""
        
        if format.lower() == 'csv':
            return df.to_csv(index=False)
        elif format.lower() == 'json':
            return df.to_json(orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    # ==================== Read Operations ====================
    
    def read_nus(self) -> pd.DataFrame:
        return self._read_file('nus')
    
    def read_pu(self) -> pd.DataFrame:
        return self._read_file('pu')
    
    def read_mapping(self) -> pd.DataFrame:
        return self._read_file('mapping')
    
    def read_all(self) -> dict:
        return {
            'nus': self.read_nus(),
            'pu': self.read_pu(),
            'mapping': self.read_mapping()
        }
    
    # ==================== Write Operations ====================
    
    def write_nus(self, df: pd.DataFrame) -> None:
        self._write_file(df, 'nus')
    
    def write_pu(self, df: pd.DataFrame) -> None:
        self._write_file(df, 'pu')
    
    def write_mapping(self, df: pd.DataFrame) -> None:
        self._write_file(df, 'mapping')
    
    def write_all(self, nus_df: pd.DataFrame, pu_df: pd.DataFrame, mapping_df: pd.DataFrame) -> None:
        self.write_nus(nus_df)
        self.write_pu(pu_df)
        self.write_mapping(mapping_df)
    
    # ==================== Import/Export Operations ====================

    def import_nus(self, file_source: Any) -> pd.DataFrame:
        return self._import_file(file_source, 'nus')

    def import_pu(self, file_source: Any) -> pd.DataFrame:
        return self._import_file(file_source, 'pu')

    def export_mapping(self, file_destination: Any) -> None:
        self._export_file(file_destination, 'mapping')
