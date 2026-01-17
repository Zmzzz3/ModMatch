from sentence_transformers import SentenceTransformer, util

class Mapping:
    def __init__(self, home_row, partner_row, score=0.0):
        self.home_row = home_row         # Pandas Series from nus_df
        self.partner_row = partner_row   # Pandas Series from partner_df
        self.similarity_score = score

class MappingEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def score_mapping(self, home_row, partner_row):
        """
        Calculates similarity using the new storage column names:
        'nus_desc' for Home and 'pu_desc' for Partner.
        """
        text_a = str(home_row['nus_desc'])
        text_b = str(partner_row['pu_desc'])
        
        embeddings = self.model.encode([text_a, text_b], convert_to_tensor=True)
        score = float(util.cos_sim(embeddings[0], embeddings[1]))
        return score

    def get_preview_pairings(self, home_row, partner_rows):
        """
        Generates 1-to-1 candidate Mapping objects for the Preview table.
        """
        preview_list = []
        for _, p_row in partner_rows.iterrows():
            score = self.score_mapping(home_row, p_row)
            preview_list.append(Mapping(home_row, p_row, score))
        return preview_list

    def finalize_selections(self, preview_list, selected_preview_indices):
        """
        Prepares data specifically for CourseStorage.add_pairing().
        Returns the original indices and the calculated scores.
        """
        final_data = {
            "nus_index": None,
            "partner_indices": [],
            "scores": []
        }

        for idx in selected_preview_indices:
            m = preview_list[idx]
            
            final_data["nus_index"] = m.home_row.name 
            final_data["partner_indices"].append(m.partner_row.name)
            final_data["scores"].append(m.similarity_score)
            
        return final_data


