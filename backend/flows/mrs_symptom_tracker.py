from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class Record:
    """Individual symptom record with MRS score and assessment status"""
    mrs_score: Optional[int] = None
    is_addressed: bool = False
    
    def to_dict(self) -> Dict[str, any]:
        """Convert record to dictionary format"""
        return {
            'mrs_score': self.mrs_score,
            'is_addressed': self.is_addressed
        }

class MRSTracker:
    """
    Tracks MRS (Menopause Rating Scale) symptoms across three domains.
    Manages symptom assessment progress and scoring.
    """
    
    def __init__(self):
        """Initialize tracker with all MRS symptoms"""
        self.mrs_symptoms = {
            "somatic": ["hot_flashes", "heart_discomfort", "sleep_problems", "joint_muscle_discomfort"],
            "psychological": ["depressive_mood", "irritability", "anxiety", "mental_exhaustion"], 
            "urogenital": ["sexual_problems", "bladder_problems", "vaginal_dryness"]
        }
        
        self.records: Dict[str, Dict[str, Record]] = {}
        self._initialize_records()
    
    def _initialize_records(self):
        """Initialize all symptom records with default values"""
        for domain, symptoms in self.mrs_symptoms.items():
            self.records[domain] = {}
            for symptom in symptoms:
                self.records[domain][symptom] = Record()
    
    def get_missing_symptoms(self, domain: Optional[str] = None) -> List[str]:
        """
        Get list of symptoms that haven't been addressed yet.
        
        Args:
            domain: Optional domain filter (somatic/psychological/urogenital)
            
        Returns:
            List of unaddressed symptom names
        """
        missing = []
        
        if domain:
            for symptom_name, record in self.records[domain].items():
                if not record.is_addressed:
                    missing.append(symptom_name)
        else:
            for domain_records in self.records.values():
                for symptom_name, record in domain_records.items():
                    if not record.is_addressed:
                        missing.append(symptom_name)
        
        return missing
    
    def get_bundle_question_symptoms(self, max_symptoms: int = 2) -> Tuple[List[str], str]:
        """
        Get 1-2 symptoms from same domain for bundle questioning.
        
        Args:
            max_symptoms: Maximum number of symptoms to bundle
            
        Returns:
            Tuple of (symptom_list, domain_name)
        """
        # Priority order: somatic > psychological > urogenital
        priority_domains = ["somatic", "psychological", "urogenital"]
        
        for domain in priority_domains:
            missing_in_domain = self.get_missing_symptoms(domain)
            if missing_in_domain:
                bundle = missing_in_domain[:max_symptoms]
                return bundle, domain
        
        return [], ""
    
    def is_assessment_complete(self) -> bool:
        """Check if all symptoms have been addressed"""
        for domain_records in self.records.values():
            for record in domain_records.values():
                if not record.is_addressed:
                    return False
        return True
    
    def update_records(self, last_asked_symptoms: List[str], symptoms_scored: List[Dict[str, any]] = []):
        """
        Update symptom records based on user interaction.
        
        Args:
            last_asked_symptoms: List of symptoms that were asked about
            symptoms_scored: List of symptoms with scores in format [{"symptom": "name", "mrs_score": int}]
        """
        def find_symptom_domain(symptom_name: str) -> str:
            """Find which domain a symptom belongs to"""
            for domain, domain_records in self.records.items():
                if symptom_name in domain_records:
                    return domain
            return ""  # This should never happen with predefined symptoms
        
        # Update symptoms with explicit scores
        scored_symptom_names = []
        for scored_item in symptoms_scored:
            symptom_name = scored_item["symptom"]
            score = scored_item["mrs_score"]
            
            domain = find_symptom_domain(symptom_name)
            self.records[domain][symptom_name].mrs_score = score
            self.records[domain][symptom_name].is_addressed = True
            scored_symptom_names.append(symptom_name)
        
        # Update asked symptoms without scores (set to 0)
        for symptom in last_asked_symptoms:
            if symptom not in scored_symptom_names:
                domain = find_symptom_domain(symptom)
                self.records[domain][symptom].mrs_score = 0
                self.records[domain][symptom].is_addressed = True
    
    def get_assessment_progress(self) -> Dict[str, any]:
        """
        Get detailed assessment progress statistics.
        
        Returns:
            Dictionary with total and per-domain progress metrics
        """
        total_symptoms = sum(len(domain_records) for domain_records in self.records.values())
        addressed_symptoms = 0
        scored_symptoms = 0
        
        for domain_records in self.records.values():
            for record in domain_records.values():
                if record.is_addressed:
                    addressed_symptoms += 1
                if record.mrs_score is not None:
                    scored_symptoms += 1
        
        progress_by_domain = {}
        for domain, domain_records in self.records.items():
            domain_total = len(domain_records)
            domain_addressed = sum(1 for record in domain_records.values() if record.is_addressed)
            progress_by_domain[domain] = {
                'addressed': domain_addressed,
                'total': domain_total,
                'percentage': (domain_addressed / domain_total) * 100 if domain_total > 0 else 0
            }
        
        return {
            'total_progress': {
                'addressed': addressed_symptoms,
                'scored': scored_symptoms,
                'total': total_symptoms,
                'percentage': (addressed_symptoms / total_symptoms) * 100 if total_symptoms > 0 else 0
            },
            'domain_progress': progress_by_domain,
            'is_complete': self.is_assessment_complete()
        }
    
    def get_records_by_domain(self, domain: str) -> Dict[str, Record]:
        """Get all symptom records for a specific domain"""
        return self.records.get(domain, {})
    
    def to_dict(self) -> Dict[str, any]:
        """Export complete records table to dictionary format"""
        result = {}
        for domain, domain_records in self.records.items():
            result[domain] = {}
            for symptom_name, record in domain_records.items():
                result[domain][symptom_name] = record.to_dict()
        return result
    
    def from_dict(self, data: Dict[str, any]):
        """
        Import records table from dictionary format.
        
        Args:
            data: Dictionary in same format as to_dict() output
        """
        for domain, domain_data in data.items():
            if domain in self.records:
                for symptom_name, record_data in domain_data.items():
                    if symptom_name in self.records[domain]:
                        self.records[domain][symptom_name].mrs_score = record_data.get('mrs_score')
                        self.records[domain][symptom_name].is_addressed = record_data.get('is_addressed', False)