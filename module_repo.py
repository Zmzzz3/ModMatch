import pandas as pd
import os

class ModuleRepository:
    def __init__(self, home_path, partner_path):
        self.home_path = home_path
        self.partner_path = partner_path
        self.df_home, self.df_partner = self.load_data()

    def load_data(self):
        df_h = pd.read_csv(self.home_path)
        df_p = pd.read_csv(self.partner_path)
        
        df_h.columns = df_h.columns.str.strip().str.lower()
        df_p.columns = df_p.columns.str.strip().str.lower()
        
        return df_h, df_p
