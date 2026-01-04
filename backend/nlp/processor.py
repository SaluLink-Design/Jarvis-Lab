"""
Natural Language Processing Module

Handles text understanding, intent classification, entity extraction,
and semantic parsing for 3D scene generation.
"""
from typing import Dict, Any, List, Optional
import os
import re

# Try to import OpenAI, use fallback if unavailable
try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    print("⚠️ Warning: OpenAI library not available, using rule-based NLP")
    HAS_OPENAI = False
    AsyncOpenAI = None


class NLPProcessor:
    """
    Processes natural language inputs to extract intents, entities,
    and structured commands for 3D generation.
    """
    
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.system_prompt = """You are Jarvis, an AI assistant specialized in understanding 
3D scene creation commands. Your job is to analyze user requests and extract:
1. Intent (create, modify, delete, query, etc.)
2. Objects to be created/modified
3. Attributes (color, size, material, position)
4. Relationships between objects
5. Environmental settings (lighting, weather, time of day)

Return your analysis in a structured JSON format."""
        
    async def initialize(self):
        """Initialize the NLP models"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and HAS_OPENAI:
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                print("✓ OpenAI NLP processor initialized")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize OpenAI: {e}")
                self.client = None
        else:
            if not HAS_OPENAI:
                print("⚠️ Warning: OpenAI library not available, using rule-based NLP")
            elif not api_key:
                print("⚠️ Warning: OPENAI_API_KEY not set, using rule-based NLP")
    
    async def process(self, text: str) -> Dict[str, Any]:
        """
        Process natural language input
        
        Args:
            text: User's natural language command
            
        Returns:
            Structured analysis of the input
        """
        if self.client:
            return await self._process_with_llm(text)
        else:
            return await self._process_with_rules(text)
    
    async def _process_with_llm(self, text: str) -> Dict[str, Any]:
        """Process using OpenAI GPT"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze this command: {text}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract intent and entities
            result = self._parse_llm_response(content, text)
            return result
            
        except Exception as e:
            print(f"❌ LLM processing error: {e}")
            return await self._process_with_rules(text)
    
    def _parse_llm_response(self, response: str, original_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        # Default structure
        result = {
            "intent": "create",
            "entities": [],
            "attributes": {},
            "relationships": [],
            "raw_text": original_text,
            "llm_response": response
        }
        
        # Try to extract JSON from response
        import json
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                result.update(parsed)
        except:
            pass
        
        return result
    
    async def _process_with_rules(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based processing"""
        text_lower = text.lower()
        
        # Detect intent
        intent = "create"
        if any(word in text_lower for word in ["delete", "remove", "clear"]):
            intent = "delete"
        elif any(word in text_lower for word in ["change", "modify", "update", "make"]):
            intent = "modify"
        elif any(word in text_lower for word in ["what", "show", "how many", "?"]):
            intent = "query"
        
        # Extract entities
        entities = []
        
        # Common 3D objects
        objects = ["cube", "sphere", "cylinder", "cone", "plane", "car", "tree", "house", 
                  "chair", "table", "building", "forest", "mountain", "river", "sky"]
        for obj in objects:
            if obj in text_lower:
                entities.append({
                    "type": "object",
                    "value": obj,
                    "attributes": self._extract_attributes(text_lower, obj)
                })
        
        # Extract colors
        colors = ["red", "blue", "green", "yellow", "white", "black", "purple", "orange"]
        attributes = {}
        for color in colors:
            if color in text_lower:
                attributes["color"] = color
        
        # Extract sizes
        sizes = ["small", "large", "big", "tiny", "huge", "medium"]
        for size in sizes:
            if size in text_lower:
                attributes["size"] = size
        
        # Extract materials
        materials = ["wood", "wooden", "metal", "metallic", "glass", "plastic", "stone"]
        for material in materials:
            if material in text_lower:
                attributes["material"] = material.replace("en", "")  # wooden -> wood
        
        return {
            "intent": intent,
            "entities": entities,
            "attributes": attributes,
            "relationships": [],
            "raw_text": text,
            "method": "rule_based"
        }
    
    def _extract_attributes(self, text: str, object_name: str) -> Dict[str, Any]:
        """Extract attributes for a specific object"""
        attributes = {}
        
        # Find words around the object name
        pattern = r'(\w+)\s+' + object_name + r'|\b' + object_name + r'\s+(\w+)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            words = [w for w in match.groups() if w]
            for word in words:
                if word in ["red", "blue", "green", "yellow"]:
                    attributes["color"] = word
                elif word in ["small", "large", "big"]:
                    attributes["size"] = word
                elif word in ["wooden", "metal", "glass"]:
                    attributes["material"] = word
        
        return attributes
