"""
Core Orchestration Engine - The "Brain" of Jarvis

This module coordinates all AI modules and manages the overall system state.
"""
from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass, field
from datetime import datetime

from nlp.processor import NLPProcessor
from cv.processor import ComputerVisionProcessor
from generation.text_to_3d import TextTo3DGenerator
from generation.scene_builder import SceneBuilder


@dataclass
class SceneContext:
    """Maintains the state of the current 3D environment"""
    scene_id: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    lighting: Dict[str, Any] = field(default_factory=dict)
    camera: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_to_history(self, action: str, details: Dict[str, Any]):
        """Add an action to the history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })


class JarvisOrchestrator:
    """
    Central orchestration engine that coordinates all AI modules
    """
    
    def __init__(self):
        self.nlp_processor: Optional[NLPProcessor] = None
        self.cv_processor: Optional[ComputerVisionProcessor] = None
        self.text_to_3d: Optional[TextTo3DGenerator] = None
        self.scene_builder: Optional[SceneBuilder] = None
        
        self.active_contexts: Dict[str, SceneContext] = {}
        self.knowledge_base: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize all AI modules"""
        try:
            print("📚 Initializing NLP Processor...")
            self.nlp_processor = NLPProcessor()
            await self.nlp_processor.initialize()
        except Exception as e:
            print(f"⚠️ Warning: NLP Processor initialization failed: {e}")
            self.nlp_processor = NLPProcessor()

        try:
            print("👁️ Initializing Computer Vision Processor...")
            self.cv_processor = ComputerVisionProcessor()
            await self.cv_processor.initialize()
        except Exception as e:
            print(f"⚠️ Warning: CV Processor initialization failed: {e}")
            self.cv_processor = ComputerVisionProcessor()

        try:
            print("🎨 Initializing 3D Generators...")
            self.text_to_3d = TextTo3DGenerator()
            await self.text_to_3d.initialize()
        except Exception as e:
            print(f"⚠️ Warning: 3D Generator initialization failed: {e}")
            self.text_to_3d = TextTo3DGenerator()

        try:
            print("🏗️ Initializing Scene Builder...")
            self.scene_builder = SceneBuilder()
        except Exception as e:
            print(f"⚠️ Warning: Scene Builder initialization failed: {e}")
            self.scene_builder = None

        # Load knowledge base
        self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """Load pre-defined knowledge about 3D assets and properties"""
        self.knowledge_base = {
            "materials": ["wood", "metal", "glass", "plastic", "stone", "fabric"],
            "colors": ["red", "blue", "green", "yellow", "white", "black"],
            "shapes": ["cube", "sphere", "cylinder", "cone", "plane"],
            "environments": ["forest", "city", "interior", "desert", "ocean"],
            "lighting": ["morning", "noon", "sunset", "night", "studio"]
        }
    
    async def process_request(
        self, 
        text: Optional[str] = None,
        image_path: Optional[str] = None,
        video_url: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user requests
        
        Args:
            text: Natural language command
            image_path: Path to uploaded image
            video_url: YouTube or video URL
            context_id: Existing scene context ID
            
        Returns:
            Response with generated 3D content and metadata
        """
        # Get or create context
        if context_id and context_id in self.active_contexts:
            context = self.active_contexts[context_id]
        else:
            import uuid
            context_id = str(uuid.uuid4())
            context = SceneContext(scene_id=context_id)
            self.active_contexts[context_id] = context
        
        # Process multimodal inputs
        processed_data = await self._process_multimodal_inputs(
            text=text,
            image_path=image_path,
            video_url=video_url
        )
        
        # Integrate information and plan actions
        action_plan = await self._create_action_plan(processed_data, context)
        
        # Execute action plan
        result = await self._execute_action_plan(action_plan, context)
        
        # Update context history
        context.add_to_history("user_request", {
            "text": text,
            "has_image": image_path is not None,
            "has_video": video_url is not None
        })
        
        return {
            "context_id": context_id,
            "result": result,
            "scene": self._serialize_context(context)
        }
    
    async def _process_multimodal_inputs(
        self,
        text: Optional[str],
        image_path: Optional[str],
        video_url: Optional[str]
    ) -> Dict[str, Any]:
        """Process all input modalities"""
        results = {
            "text_analysis": None,
            "image_analysis": None,
            "video_analysis": None
        }
        
        # Process text
        if text and self.nlp_processor:
            results["text_analysis"] = await self.nlp_processor.process(text)
        
        # Process image
        if image_path and self.cv_processor:
            results["image_analysis"] = await self.cv_processor.process_image(image_path)
        
        # Process video
        if video_url and self.cv_processor:
            results["video_analysis"] = await self.cv_processor.process_video(video_url)
        
        return results
    
    async def _create_action_plan(
        self, 
        processed_data: Dict[str, Any],
        context: SceneContext
    ) -> List[Dict[str, Any]]:
        """
        Create a sequence of actions based on processed inputs
        """
        plan = []
        
        text_analysis = processed_data.get("text_analysis", {})
        image_analysis = processed_data.get("image_analysis", {})
        
        # Analyze intent from text
        if text_analysis:
            intent = text_analysis.get("intent", "create")
            entities = text_analysis.get("entities", [])
            
            if intent == "create":
                # Plan for creating new objects
                for entity in entities:
                    if entity.get("type") == "object":
                        plan.append({
                            "action": "generate_object",
                            "object_type": entity.get("value"),
                            "attributes": entity.get("attributes", {})
                        })
                    elif entity.get("type") == "environment":
                        plan.append({
                            "action": "generate_environment",
                            "environment_type": entity.get("value")
                        })
            
            elif intent == "modify":
                # Plan for modifying existing objects
                plan.append({
                    "action": "modify_scene",
                    "modifications": text_analysis.get("modifications", {})
                })
            
            elif intent == "delete":
                # Plan for deleting objects
                plan.append({
                    "action": "delete_objects",
                    "targets": entities
                })
        
        # Enhance with image data
        if image_analysis:
            detected_objects = image_analysis.get("objects", [])
            if detected_objects:
                plan.append({
                    "action": "reference_image",
                    "objects": detected_objects,
                    "style": image_analysis.get("style", {})
                })
        
        return plan
    
    async def _execute_action_plan(
        self,
        action_plan: List[Dict[str, Any]],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Execute the planned actions"""
        results = []
        
        for action in action_plan:
            action_type = action.get("action")
            
            if action_type == "generate_object":
                result = await self._generate_object(action, context)
                results.append(result)
            
            elif action_type == "generate_environment":
                result = await self._generate_environment(action, context)
                results.append(result)
            
            elif action_type == "modify_scene":
                result = await self._modify_scene(action, context)
                results.append(result)
        
        return {
            "actions_executed": len(results),
            "results": results
        }
    
    async def _generate_object(
        self, 
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Generate a 3D object"""
        object_type = action.get("object_type", "cube")
        attributes = action.get("attributes", {})
        
        # Use text-to-3D generator
        if self.text_to_3d:
            object_data = await self.text_to_3d.generate(
                prompt=f"a {object_type}",
                attributes=attributes
            )
            
            # Add to context
            context.objects.append(object_data)
            
            return {
                "status": "success",
                "object": object_data
            }
        
        return {"status": "error", "message": "3D generator not available"}
    
    async def _generate_environment(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Generate an environment"""
        env_type = action.get("environment_type", "basic")
        
        if self.scene_builder:
            env_data = await self.scene_builder.create_environment(env_type)
            context.environment = env_data
            
            return {
                "status": "success",
                "environment": env_data
            }
        
        return {"status": "error", "message": "Scene builder not available"}
    
    async def _modify_scene(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Modify existing scene elements"""
        modifications = action.get("modifications", {})
        
        # Apply modifications to context
        for key, value in modifications.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        return {
            "status": "success",
            "modifications": modifications
        }
    
    def _serialize_context(self, context: SceneContext) -> Dict[str, Any]:
        """Convert context to JSON-serializable format"""
        return {
            "scene_id": context.scene_id,
            "objects": context.objects,
            "environment": context.environment,
            "lighting": context.lighting,
            "camera": context.camera,
            "created_at": context.created_at.isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up resources...")
        self.active_contexts.clear()
