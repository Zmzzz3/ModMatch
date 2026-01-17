class Module:
    def __init__(self, university, module_code, module_name, module_description):
        self.university = university
        self.module_name = module_name
        self.module_code = module_code
        self.module_description = module_description

    def print_module(self):
        """Combines name and description for better AI analysis."""
        print(f"University: {self.university}")
        print(f"{self.module_code}: {self.module_name}")
        print(f"{self.module_description}")

test_mod = Module("NUS", "CS2040C", "Data Structures and Algorithms", "Test description")
test_mod.print_module()
    
