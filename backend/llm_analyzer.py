import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_mock = False
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash') # Using a fast model
        else:
            self.is_mock = True
            print("WARNING: GEMINI_API_KEY not found. Using Mock LLM Analyzer.")

    def analyze_text(self, text: str) -> tuple[list[float], str, list[str]]:
        """
        Analyzes the text and returns:
        - features: [Technical Realism, Timeline Proximity, Sentiment Exaggeration]
        - summary: A generated paragraph explaining the verdict.
        - keywords: A list of 3-5 relevant keywords extracted from the text.
        """
        if self.is_mock:
            # Simple mock logic based on keyword detection
            text_lower = text.lower()
            exaggeration = 0.5
            realism = 0.5
            timeline = 0.5
            
            if "break encryption" in text_lower or "tomorrow" in text_lower or "revolutionize everything" in text_lower:
                exaggeration = 0.9
                realism = 0.2
                timeline = 0.1
            elif "error correction" in text_lower or "qubits" in text_lower or "years" in text_lower:
                exaggeration = 0.3
                realism = 0.8
                timeline = 0.6
                
            summary = "This is a mock analysis. The provided text discusses Quantum Computing. "
            if exaggeration > 0.6:
                summary += "It contains significant hype and exaggerates near-term capabilities."
            else:
                summary += "It presents a relatively grounded and realistic view of current technology."
                
            return [realism, timeline, exaggeration], summary, ["mock", "quantum", "analysis"]

        # Real LLM call
        prompt = f"""
        You are a Quantum Computing expert analyzing the following text or news claim for hype vs. reality.
        
        Text to analyze: "{text}"
        
        Evaluate the text on three metrics from 0.0 to 1.0:
        1. Technical Realism (0.0 = completely unrealistic/sci-fi, 1.0 = scientifically accurate and grounded)
        2. Timeline Proximity (0.0 = implies it's happening tomorrow when it's decades away, 1.0 = accurate timeline representation)
        3. Sentiment Exaggeration (0.0 = neutral/objective, 1.0 = highly sensationalized and hyped)
        
        Provide a JSON response with the exact following format:
        {{
            "realism": <float>,
            "timeline": <float>,
            "exaggeration": <float>,
            "summary": "<A 2-3 sentence paragraph explaining your reasoning and the final verdict on whether this is hype or reality>",
            "keywords": ["<keyword1>", "<keyword2>", "<keyword3>"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find the JSON part in the response
            resp_text = response.text
            start = resp_text.find('{')
            end = resp_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = resp_text[start:end]
                data = json.loads(json_str)
                features = [
                    float(data.get("realism", 0.5)),
                    float(data.get("timeline", 0.5)),
                    float(data.get("exaggeration", 0.5))
                ]
                summary = data.get("summary", "Analysis completed.")
                keywords = data.get("keywords", [])
                return features, summary, keywords
            else:
                return [0.5, 0.5, 0.5], "Failed to parse LLM response format.", []
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return [0.5, 0.5, 0.5], f"Error during analysis: {e}", []
