import requests
import pandas as pd

def fetch_nusmods_data() -> pd.DataFrame :
    """
    Fetch module data from NUSMods API and return as DataFrame.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: nus_code, nus_mod, nus_desc
    """
    # Construct API URL
    url = f"https://api.nusmods.com/v2/2024-2025/moduleInfo.json"
    
    # Set headers to accept gzip compression
    headers = {
        'Accept-Encoding': 'gzip',
        'User-Agent': 'NUSMods-Python-Client'
    }
    
    try:
        # Fetch data from API
        print(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse JSON response
        modules = response.json()
        print(f"Successfully fetched {len(modules)} modules")
        
        # Extract relevant fields and rename columns
        df = pd.DataFrame(modules)
        
        # Select and rename columns
        df_filtered = df[['moduleCode', 'title', 'description']].copy()
        df_filtered.columns = ['nus_code', 'nus_mod', 'nus_desc']
        
        return df_filtered
            
    except requests.exceptions.RequestException as e:
        raise IOError(f"Error fetching data from NUSMods API: {e}")
    except KeyError as e:
        raise ValueError(f"Error parsing data - missing expected field: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error occurred: {e}")