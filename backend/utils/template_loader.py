"""
Template and System Message Loader
"""
import os
import yaml
import json
from typing import Optional

class TemplateLoader:
    def __init__(self, base_path: str = "backend"):
        self.base_path = base_path
        self.prompt_templates = {}
    
    def load_prompt_template(self, name: str) -> Optional[str]:
        if name in self.prompt_templates:
            return self.prompt_templates[name]
        
        try:
            file_path = os.path.join(self.base_path, "prompts", f"{name}.yaml")
            if not os.path.exists(file_path):
                print(f"Template not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                template_data = yaml.safe_load(file)

                # 提取唯一顶层键（例如 response_analysis_prompt）
                if isinstance(template_data, dict) and len(template_data) == 1:
                    inner_block = next(iter(template_data.values()))
                    if isinstance(inner_block, dict) and "template" in inner_block:
                        template = inner_block["template"]
                        self.prompt_templates[name] = template
                        return template
                
        except Exception as e:
            print(f"Error loading template {name}: {e}")
            return None

def format_template(template: str, **kwargs) -> str:
    for k, v in kwargs.items():
        if isinstance(v, (list, dict)):
            v = json.dumps(v, ensure_ascii=False)
        template = template.replace("{" + k + "}", str(v))
    return template

template_loader = TemplateLoader()