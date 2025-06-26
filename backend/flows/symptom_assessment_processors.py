from typing import Any, Dict, List
import json
import re
from backend.utils.template_loader import template_loader, format_template
from backend.utils import openai_client
from .mrs_symptom_tracker import MRSTracker

class MRSCollector:
    def __init__(self, tracker: MRSTracker) -> None:
        self.tracker = tracker
        self.previous_question: str = ""
        self.last_asked_symptoms: List[str] = []

    def collect(self, user_input: str) -> Dict[str, Any]:
        prompt_template = template_loader.load_prompt_template(
            "mrs_response_analyzer"
        )
        if not prompt_template:
            return self._error("Prompt template loading failed")
        prompt = format_template(
            prompt_template,
            user_input=user_input,
            previous_question=self.previous_question,
        )
        model_output = openai_client.call_model_with_prompt(prompt)
        if not model_output:
            return self._error("LLM calling failed")
        try:
            json_text = re.search(r'\{.*\}', model_output, re.DOTALL).group(0)
            return json.loads(json_text)
        except Exception:
            return self._error("LLM output parsing failed")

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "symptom_updates": [],
            "action_type": "error",
            "next_message": f"Error: {message}",
        }


class MRSScorer:
    def __init__(self, tracker: MRSTracker) -> None:
        self.tracker = tracker

    def score(self) -> Dict[str, Any]:
        prompt_template = template_loader.load_prompt_template(
            "mrs_score_calculator"
        )
        if not prompt_template:
            return self._error("Prompt template loading failed")
        prompt = format_template(
            prompt_template,
            user_records=json.dumps(self.tracker.to_dict(), ensure_ascii=False),
        )
        model_output = openai_client.call_model_with_prompt(prompt)
        if not model_output:
            return self._error("LLM calling failed")
        try:
            json_text = re.search(r'\{.*\}', model_output, re.DOTALL).group(0)
            return json.loads(json_text)
        except Exception:
            return self._error("LLM output parsing failed")

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "total_score": 0,
            "interpretation": f"Error: {message}"
        }
