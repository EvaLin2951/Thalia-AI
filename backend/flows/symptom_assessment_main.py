from .symptom_assessment_flow import MRSFlow
from typing import Dict, Any

# ---- 外部兼容性 ----
symptom_assessment_flow = MRSFlow()

def menopause_support_enhanced(user_input: str, history=None) -> Dict[str, Any]:
    return symptom_assessment_flow.process_input(user_input)

def menopause_support(user_input: str, history=None) -> str:
    result = menopause_support_enhanced(user_input, history)
    return result.get("message", "I'm having trouble processing your input.")