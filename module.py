class Module:
    def __init__(self, university, name, code, description):
        self.university = university
        self.name = name
        self.code = code
        self.description = description
        self.mapping:Module = None

    def print_module(self):
        """Combines name and description for better AI analysis."""
        print(f"University: {self.university}")
        print(f"{self.code}: {self.name}")
        print(f"{self.description}")

if __name__ == "__main__":
    test_mod = Module("NUS", "CS2040C", "Data Structures and Algorithms", "Test description")
    test_mod.print_module()
    
