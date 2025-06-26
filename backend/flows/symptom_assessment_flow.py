from typing import Any, Dict, Optional
import json
from backend.utils.template_loader import template_loader, format_template
from backend.utils import openai_client
from .mrs_symptom_tracker import MRSTracker
from .symptom_assessment_processors import MRSCollector, MRSScorer

class MRSFlow:
    def __init__(self):
        self.tracker = MRSTracker()
        self.collector = MRSCollector(self.tracker)
        self.scorer = MRSScorer(self.tracker)
        self.pending_zero_confirmation = False
        self.pending_exit_confirmation = False
        self.original_question = ""

    def process_input(self, user_input: str) -> Dict[str, Any]:
        if self.pending_zero_confirmation:
            return self._handle_zero_confirmation(user_input)
        if self.pending_exit_confirmation:
            return self._handle_exit_confirmation(user_input)

        parsed = self.collector.collect(user_input)
        scored_symptoms = parsed.get("symptoms_scored", [])
        self.tracker.update_records(self.collector.last_asked_symptoms, scored_symptoms)
        action_type = parsed.get("action_type", "")
        next_message = parsed.get("next_message", "")

        if action_type == "emergency_exit":
            return self._exit_flow()
        if action_type == "exit_intent":
            self.pending_exit_confirmation = True
            self.original_question = user_input
            return {
                "status": "exit_confirmation_pending",
                "message": next_message,
                "flow": "symptom_assessment",
            }
        if action_type == "severity_unclear":
            return {
                "status": "clarification_needed",
                "message": next_message,
                "flow": "symptom_assessment",
            }
        if action_type == "severity_clear":
            return self._ask_next_question(next_message)
        return {
            "status": "error",
            "message": f"Error: {next_message}",
            "flow": "symptom_assessment",
        }

    def _handle_zero_confirmation(self, user_input: str) -> Dict[str, Any]:
        if user_input.strip().lower() in {"yes", "y"}:
            self.pending_zero_confirmation = False
            return self._score_and_respond()
        return self._ask_next_question()

    def _handle_exit_confirmation(self, user_input: str) -> Dict[str, Any]:
        self.pending_exit_confirmation = False
        response = user_input.strip().lower()
        if response in {"yes", "y"}:
            return self._exit_flow(self.original_question)
        if response in {"no", "n"}:
            message = f"Great, let's continue. {self.collector.previous_question}"
            return {
                "status": "continue_assessment",
                "message": message.strip(),
                "flow": "symptom_assessment",
            }
        return self._ask_next_question()


    def _ask_next_question(self, next_message: Optional[str] = None) -> Dict[str, Any]:
        if self.tracker.is_assessment_complete():
            return self._check_zero_before_score()
        target_symptoms, _ = self.tracker.get_bundle_question_symptoms(max_symptoms=2)
        if not target_symptoms:
            return self._check_zero_before_score()
        prompt_template = template_loader.load_prompt_template(
            "mrs_question_generator"
        )
        if not prompt_template:
            return self._error("Prompt template loading failed")
        prompt = format_template(prompt_template, target_symptoms=target_symptoms)
        model_out = openai_client.call_model_with_prompt(prompt)
        if not model_out:
            return self._error("LLM calling failed")
        try:
            next_question = json.loads(model_out)["next_question"]
        except Exception:
            return self._error("LLM output parsing failed")
        self.collector.previous_question = next_question
        self.collector.last_asked_symptoms = target_symptoms
        return {
            "status": "asking_next_symptom",
            "message": (next_message + " " + next_question).strip(),
            "flow": "symptom_assessment",
        }

    def _check_zero_before_score(self) -> Dict[str, Any]:
        zero_symptoms = [
            s
            for d in self.tracker.records.values()
            for s, r in d.items()
            if r.mrs_score == 0
        ]
        if zero_symptoms:
            self.pending_zero_confirmation = True
            readable = ", ".join(s.replace("_", " ") for s in zero_symptoms)
            return {
                "status": "zero_confirmation_pending",
                "message": (
                    f"Assessment completed! Before calculating your score, I assumed you don't have these symptoms: {readable}. "
                    "Is this accurate? (yes) If not, please share any updates and I’ll make adjustments."
                ),
                "flow": "symptom_assessment",
            }
        return self._score_and_respond()

    def _score_and_respond(self) -> Dict[str, Any]:
        score_data = self.scorer.score()
        total_score = score_data["total_score"]
        interpretation = score_data["interpretation"]
        self.__init__()
        return {
            "status": "scoring_completed_and_exited",
            "message": f"{interpretation} (Session finished. Assessment exited.)",
            "flow": "symptom_assessment",
            "mrs_score": total_score,
        }

    def _exit_flow(self, original_question: Optional[str] = None) -> Dict[str, Any]:
        self.__init__()
        return {
            "status": "exit_confirmed",
            "message": "Assessment ended. Is there anything else you'd like to talk about?",
            "flow": "symptom_assessment",
            "original_question": original_question,
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": f"Error: {message}",
            "flow": "symptom_assessment",
        }
