import spacy
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            raise
        
        # Load sentence transformer for semantic similarity
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Could not load sentence transformer: {e}")
            self.sentence_model = None
        
        # Section patterns
        self.section_patterns = {
            'summary': r'(?:^|\n)\s*(?:summary|profile|objective|about)\s*:?\s*\n',
            'experience': r'(?:^|\n)\s*(?:experience|work history|employment|professional experience)\s*:?\s*\n',
            'education': r'(?:^|\n)\s*(?:education|academic background|qualifications)\s*:?\s*\n',
            'skills': r'(?:^|\n)\s*(?:skills|technical skills|core competencies|expertise)\s*:?\s*\n',
            'certifications': r'(?:^|\n)\s*(?:certifications?|licenses?|credentials?)\s*:?\s*\n',
            'projects': r'(?:^|\n)\s*(?:projects?|portfolio|notable work)\s*:?\s*\n'
        }
        
        # Skill patterns for enhanced entity extraction
        self.skill_patterns = {
            'programming_languages': [
                r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala)\b',
                r'\b(?:HTML|CSS|SQL|R|MATLAB|Perl|Shell|Bash)\b'
            ],
            'frameworks': [
                r'\b(?:React|Angular|Vue|Django|Flask|Spring|Express|Laravel|Rails)\b',
                r'\b(?:TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy)\b',
                r'\b(?:Bootstrap|Tailwind|Material-UI|Ant Design)\b'
            ],
            'tools': [
                r'\b(?:Git|Docker|Kubernetes|Jenkins|GitLab|GitHub|Bitbucket)\b',
                r'\b(?:AWS|Azure|GCP|Heroku|Vercel|Netlify)\b',
                r'\b(?:Jira|Confluence|Slack|Teams|Notion)\b',
                r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b'
            ],
            'certifications': [
                r'\b(?:AWS|Azure|GCP|Google Cloud)\s+(?:Certified|Certification)\b',
                r'\b(?:PMP|CISSP|CISM|CISA|CPA|CFA)\b',
                r'\b(?:Scrum Master|Product Owner|Agile)\s+(?:Certified|Certification)\b'
            ]
        }

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract resume sections using enhanced patterns"""
        sections = {}
        text_lower = text.lower()
        
        for section_name, pattern in self.section_patterns.items():
            matches = list(re.finditer(pattern, text_lower, re.MULTILINE | re.IGNORECASE))
            if matches:
                start_pos = matches[0].end()
                
                # Find the end of this section
                next_section_start = len(text)
                for other_pattern in self.section_patterns.values():
                    if other_pattern == pattern:
                        continue
                    other_matches = list(re.finditer(other_pattern, text_lower[start_pos:], re.MULTILINE | re.IGNORECASE))
                    if other_matches:
                        potential_end = start_pos + other_matches[0].start()
                        if potential_end < next_section_start:
                            next_section_start = potential_end
                
                sections[section_name] = text[start_pos:next_section_start].strip()
        
        return sections

    def extract_keywords_for_jd(self, text: str, limit: int = 50) -> List[str]:
        """Extract keywords from job description text"""
        if not text:
            return []
        
        # Preprocess text
        doc = self.nlp(text.lower())
        
        # Filter tokens
        filtered_tokens = []
        for token in doc:
            if (not token.is_stop and not token.is_punct and not token.is_space 
                and token.pos_ in ['NOUN', 'PROPN', 'ADJ'] 
                and len(token.text) > 2):
                filtered_tokens.append(token.lemma_)
        
        if not filtered_tokens:
            return []
        
        # Use TF-IDF but handle small corpus
        try:
            tfidf = TfidfVectorizer(
                max_features=min(limit, len(set(filtered_tokens))),
                ngram_range=(1, 2),
                min_df=1,
                max_df=1.0  # Allow all documents
            )
            
            tfidf_matrix = tfidf.fit_transform([' '.join(filtered_tokens)])
            feature_names = tfidf.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Sort by score
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [kw for kw, score in keyword_scores if score > 0][:limit]
            
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {e}, falling back to simple extraction")
            # Fallback to simple keyword extraction
            return list(set(filtered_tokens))[:limit]

    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities with custom skill patterns"""
        doc = self.nlp(text)
        
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'programming_languages': [],
            'frameworks': [],
            'tools': [],
            'certifications': [],
            'general_skills': []
        }
        
        # Extract standard named entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities['persons'].append(ent.text)
            elif ent.label_ in ["ORG", "COMPANY"]:
                entities['organizations'].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities['locations'].append(ent.text)
        
        # Extract technical skills using patterns
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill = match.group().strip()
                    if skill and skill not in entities[category]:
                        entities[category].append(skill)
        
        # Extract general skills using noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3 and chunk.text.lower() not in [
                'experience', 'work', 'company', 'team', 'project', 'year', 'years'
            ]:
                entities['general_skills'].append(chunk.text)
        
        # Remove duplicates and clean up
        for category in entities:
            entities[category] = list(set(entities[category]))
        
        return entities

    def calculate_semantic_similarity(self, resume_text: str, jd_text: str) -> Dict[str, float]:
        """Calculate semantic similarity between resume and job description"""
        if not self.sentence_model:
            return {"error": "Sentence transformer model not available"}
        
        try:
            # Get embeddings
            resume_embedding = self.sentence_model.encode([resume_text])
            jd_embedding = self.sentence_model.encode([jd_text])
            
            # Calculate similarity
            similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
            
            return {
                "overall_similarity": float(similarity),
                "similarity_score": int(similarity * 100),
                "interpretation": self._interpret_similarity(similarity)
            }
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return {"error": str(e)}

    def analyze_section_alignment(self, resume_sections: Dict[str, str], jd_text: str) -> Dict[str, Any]:
        """Analyze how well each resume section aligns with job requirements"""
        if not self.sentence_model:
            return {"error": "Sentence transformer model not available"}
        
        alignments = {}
        
        try:
            jd_embedding = self.sentence_model.encode([jd_text])
            
            for section_name, section_text in resume_sections.items():
                if section_text.strip():
                    section_embedding = self.sentence_model.encode([section_text])
                    similarity = cosine_similarity(section_embedding, jd_embedding)[0][0]
                    
                    alignments[section_name] = {
                        "similarity_score": float(similarity),
                        "score_percentage": int(similarity * 100),
                        "alignment_level": self._get_alignment_level(similarity),
                        "word_count": len(section_text.split())
                    }
            
            return alignments
        except Exception as e:
            logger.error(f"Error analyzing section alignment: {e}")
            return {"error": str(e)}

    def _interpret_similarity(self, similarity: float) -> str:
        """Interpret similarity score"""
        if similarity >= 0.8:
            return "Excellent match"
        elif similarity >= 0.6:
            return "Good match"
        elif similarity >= 0.4:
            return "Moderate match"
        elif similarity >= 0.2:
            return "Weak match"
        else:
            return "Poor match"

    def _get_alignment_level(self, similarity: float) -> str:
        """Get alignment level description"""
        if similarity >= 0.7:
            return "Strong"
        elif similarity >= 0.5:
            return "Moderate"
        elif similarity >= 0.3:
            return "Weak"
        else:
            return "Poor"

# Global instance for backward compatibility
_nlp_service = NLPService()

# Backward compatibility functions
def extract_sections(text: str) -> Dict[str, str]:
    """Extract resume sections using enhanced patterns"""
    return _nlp_service.extract_sections(text)

def extract_keywords_for_jd(text: str, limit: int = 50) -> List[str]:
    """Extract keywords from job description"""
    return _nlp_service.extract_keywords_for_jd(text, limit)

def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities with custom skill patterns"""
    return _nlp_service.extract_named_entities(text)

def calculate_semantic_similarity(resume_text: str, jd_text: str) -> Dict[str, float]:
    """Calculate semantic similarity between resume and job description"""
    return _nlp_service.calculate_semantic_similarity(resume_text, jd_text)

def analyze_section_alignment(resume_sections: Dict[str, str], jd_text: str) -> Dict[str, Any]:
    """Analyze how well each resume section aligns with job requirements"""
    return _nlp_service.analyze_section_alignment(resume_sections, jd_text)
