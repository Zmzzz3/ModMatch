from sentence_transformers import SentenceTransformer, util

class Mapping:
    def __init__(self, home_row, partner_row, score=0.0):
        self.home_row = home_row         # Pandas Series
        self.partner_row = partner_row   # Pandas Series
        self.similarity_score = score

class MappingEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def score_mapping(self, home_row, partner_row):
        """Standard 1-to-1 scoring."""
        text_a = str(home_row['description'])
        text_b = str(partner_row['description'])
        embeddings = self.model.encode([text_a, text_b], convert_to_tensor=True)
        score = float(util.cos_sim(embeddings[0], embeddings[1]))
        return score

    def get_preview_pairings(self, home_row, partner_rows):
        """
        Step 1: Takes selection and returns a list of candidate Mapping objects.
        This is the 'Preview' generator.
        """
        preview_list = []
        for _, p_row in partner_rows.iterrows():
            score = self.score_mapping(home_row, p_row)
            preview_list.append(Mapping(home_row, p_row, score))
        return preview_list

    def finalize_selections(self, preview_list, selected_indices):
        """
        Step 2: Takes the full preview list and the indices the user checked.
        Returns only the confirmed rows and scores.
        """
        final_results = []
        for idx in selected_indices:
            m = preview_list[idx]
            # Return a dictionary or a custom object with the raw rows
            final_results.append({
                "home_row": m.home_row,
                "partner_row": m.partner_row,
                "score": m.similarity_score
            })
        return final_results

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

