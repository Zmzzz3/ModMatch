from sentence_transformers import SentenceTransformer, util
from module import Module

class Mapping:
    def __init__(self, home_module, partner_module, similarity_score=0.0):
        self.home_module = home_module
        self.partner_module = partner_module
        self.similarity_score = similarity_score
        self.status = "Pending"
        self.ai_commentary = ""
    
    def set_similarity_score(self, score:float):
        self.similarity_score = score

class MappingEngine:
    def __init__(self):   
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def check_and_score_mapping(self, mapping:Mapping):
        """
        Takes two specific Module objects and returns their similarity score.
        """
        mod_a = mapping.home_module
        mod_b = mapping.partner_module
        text_a = mod_a.description
        text_b = mod_b.description
        
        embeddings = self.model.encode([text_a, text_b], convert_to_tensor=True)
        
        score = util.cos_sim(embeddings[0], embeddings[1])

        mapping.set_similarity_score(float(score))

        return float(score)

    def print_mapping_result(self, mapping:Mapping):
        """
        Prints the two mods' description and the similarity score.
    
        :param mapping: Mapping object
        """
        home_mod = mapping.home_module
        partner_mod = mapping.partner_module
        home_mod.print_module()
        partner_mod.print_module()
        score = self.check_and_score_mapping(mapping)
        print(f"\nComparison score: {score}")


if __name__ == "__main__":
    
    description1 = """This course introduces students to the design and implementation 
        of fundamental data structures and algorithms. The course covers basic data 
        structures (linked lists, stacks, queues, hash tables, binary heaps, trees, 
        and graphs), searching and sorting algorithms, basic analysis of algorithms, 
        and basic object-oriented programming concepts."""

    cs2040c = Module("NUS", "Data Structures and Algorithms", "CS2040C", description1)
    
    description2 = """This course introduces students to the design and implementation of 
        fundamental data structures and algorithms. The course covers basic data 
        structures (linked lists, stacks, queues, hash tables, binary heaps, trees, 
        and graphs), searching and sorting algorithms, and basic analysis of algorithms."""

    cs2040s = Module("NUS2", "Data Structures Thing", "CS2040S", description2)

    description3 = "This course introduces the topic of gender by using basic concepts like biological sex, nature, nurture, roles, norms and culture. The meaning of gender categories is examined in relation to difference, exchange, reproduction, knowledge and social change. Although the main perspective is ethnographic, this course is intended to be an exercise in interdisciplinary thinking. Understanding gender provides a foundation to analyze social structures (power and inequality), social institutions (family, kinship, education, economy, the state, health) and cultural issues (science, food, emotions, popular culture)."

    sc2220 = Module("NUS3", "Gender Studies", "SC2220", description3)

    mapping = Mapping(cs2040c, sc2220, 0)
    map_engine = MappingEngine()
    score = map_engine.print_mapping_result(mapping)

