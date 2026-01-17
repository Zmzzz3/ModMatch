import pandas as pd
import os
from module import Module

class ModuleRepository:
    def __init__(self, filename="home_modules_db.csv"):
        self.filename = filename
        self.all_modules = self.load_all()

    def save(self, module):
        """Appends a single Module object to the CSV and updates the cache."""
        data = {
            "university": [module.university],
            "name": [module.name],
            "code": [module.code],
            "description": [module.description.replace("\n", " ")]
        }
        df = pd.DataFrame(data)
        
        header = not os.path.exists(self.filename)
        df.to_csv(self.filename, mode='a', index=False, header=header)
        
        self.all_modules.append(module)

    def load_all(self):
        """Returns a list of Module objects from the CSV."""
        if not os.path.exists(self.filename):
            return []
        
        df = pd.read_csv(self.filename)
        return [Module(row['university'], row['name'], row['code'], row['description']) 
                for _, row in df.iterrows()]
    
    def find_mod_by_code(self, code):
        """Finds a module, ignoring spaces and capitalization."""
        search_code = str(code).strip().upper()
        for mod in self.all_modules:
            if mod.code.strip().upper() == search_code:
                return mod
        return None
    

if __name__ == "__main__":
    home_repo = ModuleRepository("data/home_modules_db.csv")
    partner_repo = ModuleRepository("data/partner_modules_db.csv")

    description = "This course introduces the fundamental concepts of problem solving by computing and programming using an imperative programming language. It is the first and foremost introductory course to computing. Topics covered include computational thinking and computational problem solving, designing and specifying an algorithm, basic problem formulation and problem solving approaches, program development, coding, testing and debugging, fundamental programming constructs (variables, types, expressions, assignments, functions, control structures, etc.), fundamental data structures (arrays, strings, composite data types), basic sorting, and recursion."
    mod = Module("NUS", "Programming Methodology", "CS1010", description)
    home_repo.save(mod)

