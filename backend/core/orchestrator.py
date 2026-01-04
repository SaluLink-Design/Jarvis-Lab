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
        print("🚀 Initializing Jarvis Orchestrator...")

        try:
            print("📚 Initializing NLP Processor...")
            self.nlp_processor = NLPProcessor()
            if hasattr(self.nlp_processor, 'initialize'):
                await self.nlp_processor.initialize()
            print("✅ NLP Processor ready")
        except Exception as e:
            print(f"⚠️ NLP Processor initialization failed: {e}")
            self.nlp_processor = NLPProcessor()

        try:
            print("👁️ Initializing Computer Vision Processor...")
            self.cv_processor = ComputerVisionProcessor()
            if hasattr(self.cv_processor, 'initialize'):
                await self.cv_processor.initialize()
            print("✅ CV Processor ready")
        except Exception as e:
            print(f"⚠️ CV Processor initialization failed: {e}")
            self.cv_processor = ComputerVisionProcessor()

        try:
            print("🎨 Initializing 3D Generators...")
            self.text_to_3d = TextTo3DGenerator()
            if hasattr(self.text_to_3d, 'initialize'):
                await self.text_to_3d.initialize()
            print("✅ 3D Generator ready")
        except Exception as e:
            print(f"⚠️ 3D Generator initialization failed: {e}")
            self.text_to_3d = TextTo3DGenerator()

        try:
            print("🏗️ Initializing Scene Builder...")
            self.scene_builder = SceneBuilder()
            print("✅ Scene Builder ready")
        except Exception as e:
            print(f"⚠️ Scene Builder initialization failed: {e}")
            self.scene_builder = SceneBuilder()

        self._load_knowledge_base()
        print("✅ Jarvis Orchestrator initialized successfully")
        
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
        import uuid
        import traceback

        print(f"\n[ORCHESTRATOR] Processing request")
        print(f"  Text: {text[:50] if text else 'None'}...")
        print(f"  Context ID: {context_id}")

        try:
            # Get or create context
            if context_id and context_id in self.active_contexts:
                context = self.active_contexts[context_id]
                print(f"[ORCHESTRATOR] Using existing context: {context_id}")
            else:
                context_id = str(uuid.uuid4())
                context = SceneContext(scene_id=context_id)
                self.active_contexts[context_id] = context
                print(f"[ORCHESTRATOR] Created new context: {context_id}")

            try:
                # Process multimodal inputs
                print(f"[ORCHESTRATOR] Processing multimodal inputs...")
                processed_data = await self._process_multimodal_inputs(
                    text=text,
                    image_path=image_path,
                    video_url=video_url
                )
                print(f"[ORCHESTRATOR] Multimodal processing complete")
            except Exception as e:
                print(f"⚠️ [ORCHESTRATOR] Multimodal processing error: {e}")
                traceback.print_exc()
                processed_data = {
                    "text_analysis": None,
                    "image_analysis": None,
                    "video_analysis": None
                }

            try:
                # Integrate information and plan actions
                print(f"[ORCHESTRATOR] Creating action plan...")
                action_plan = await self._create_action_plan(processed_data, context)
                print(f"[ORCHESTRATOR] Action plan created with {len(action_plan)} actions")
            except Exception as e:
                print(f"⚠️ [ORCHESTRATOR] Action plan creation error: {e}")
                traceback.print_exc()
                # Fallback: create a simple default action
                action_plan = [{
                    "action": "generate_object",
                    "object_type": "cube",
                    "attributes": {"color": "blue"}
                }]

            try:
                # Execute action plan
                print(f"[ORCHESTRATOR] Executing action plan...")
                result = await self._execute_action_plan(action_plan, context)
                print(f"[ORCHESTRATOR] Action plan executed. Success: {result.get('success', False)}")
            except Exception as e:
                print(f"⚠️ [ORCHESTRATOR] Action plan execution error: {e}")
                traceback.print_exc()
                result = {
                    "actions_executed": 0,
                    "results": [],
                    "success": False,
                    "error": str(e)
                }

            # Update context history
            context.add_to_history("user_request", {
                "text": text,
                "has_image": image_path is not None,
                "has_video": video_url is not None
            })

            response = {
                "context_id": context_id,
                "result": result,
                "scene": self._serialize_context(context),
                "status": "success" if result.get("success", False) else "partial"
            }
            print(f"[ORCHESTRATOR] Request processing complete. Status: {response['status']}")
            return response

        except Exception as e:
            print(f"\n❌ [ORCHESTRATOR] CRITICAL ERROR in process_request: {e}")
            print(traceback.format_exc())

            # Return a valid fallback response instead of raising
            fallback_context_id = context_id or str(uuid.uuid4())
            fallback_response = {
                "context_id": fallback_context_id,
                "result": {
                    "actions_executed": 0,
                    "results": [],
                    "success": False,
                    "error": str(e)
                },
                "scene": {
                    "scene_id": fallback_context_id,
                    "objects": [],
                    "environment": {},
                    "lighting": {},
                    "camera": {},
                    "created_at": datetime.now().isoformat()
                },
                "status": "error",
                "message": f"Processing error: {str(e)}"
            }
            print(f"[ORCHESTRATOR] Returning error response")
            return fallback_response
    
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
            try:
                results["text_analysis"] = await self.nlp_processor.process(text)
            except Exception as e:
                print(f"Error processing text: {e}")
                results["text_analysis"] = {
                    "intent": "create",
                    "entities": [],
                    "attributes": {},
                    "raw_text": text,
                    "error": str(e)
                }

        # Process image
        if image_path and self.cv_processor:
            try:
                results["image_analysis"] = await self.cv_processor.process_image(image_path)
            except Exception as e:
                print(f"Error processing image: {e}")
                results["image_analysis"] = {"error": str(e)}

        # Process video
        if video_url and self.cv_processor:
            try:
                results["video_analysis"] = await self.cv_processor.process_video(video_url)
            except Exception as e:
                print(f"Error processing video: {e}")
                results["video_analysis"] = {"error": str(e)}

        return results
    
    async def _create_action_plan(
        self,
        processed_data: Dict[str, Any],
        context: SceneContext
    ) -> List[Dict[str, Any]]:
        """
        Create a sequence of actions based on processed inputs
        """
        print(f"[ACTION_PLAN] Creating action plan from processed data")
        plan = []

        try:
            text_analysis = processed_data.get("text_analysis") or {}
            image_analysis = processed_data.get("image_analysis") or {}

            # Analyze intent from text
            if text_analysis and not text_analysis.get("error"):
                print(f"[ACTION_PLAN] Text analysis available")
                intent = text_analysis.get("intent", "create")
                entities = text_analysis.get("entities", [])
                attributes = text_analysis.get("attributes", {})
                print(f"[ACTION_PLAN] Intent: {intent}, Entities: {len(entities)}, Attributes: {attributes}")

                if intent == "create":
                    # Plan for creating new objects
                    if entities:
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
                    else:
                        # No entities found, create a default object
                        print(f"[ACTION_PLAN] No entities found, using default cube")
                        plan.append({
                            "action": "generate_object",
                            "object_type": "cube",
                            "attributes": attributes
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
            if image_analysis and not image_analysis.get("error"):
                print(f"[ACTION_PLAN] Image analysis available")
                detected_objects = image_analysis.get("objects", [])
                if detected_objects:
                    plan.append({
                        "action": "reference_image",
                        "objects": detected_objects,
                        "style": image_analysis.get("style", {})
                    })

            # If no plan was created, add a default action
            if not plan:
                print(f"[ACTION_PLAN] No plan created, using default cube")
                plan.append({
                    "action": "generate_object",
                    "object_type": "cube",
                    "attributes": {"color": "blue"}
                })

            print(f"[ACTION_PLAN] Plan created with {len(plan)} actions: {[p['action'] for p in plan]}")
            return plan

        except Exception as e:
            print(f"⚠️ [ACTION_PLAN] Error in action plan creation: {e}")
            import traceback
            traceback.print_exc()
            # Return a default plan
            return [{
                "action": "generate_object",
                "object_type": "cube",
                "attributes": {"color": "blue"}
            }]
    
    async def _execute_action_plan(
        self,
        action_plan: List[Dict[str, Any]],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Execute the planned actions"""
        results = []

        for action in action_plan:
            try:
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

            except Exception as e:
                print(f"Error executing action {action_type}: {e}")
                results.append({
                    "status": "error",
                    "action": action_type,
                    "error": str(e)
                })

        return {
            "actions_executed": len(results),
            "results": results,
            "success": any(r.get("status") == "success" for r in results)
        }
    
    async def _generate_object(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Generate a 3D object"""
        try:
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
        except Exception as e:
            print(f"Error generating object: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _generate_environment(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Generate an environment"""
        try:
            env_type = action.get("environment_type", "basic")

            if self.scene_builder:
                env_data = await self.scene_builder.create_environment(env_type)
                context.environment = env_data

                return {
                    "status": "success",
                    "environment": env_data
                }

            return {"status": "error", "message": "Scene builder not available"}
        except Exception as e:
            print(f"Error generating environment: {e}")
            return {"status": "error", "message": str(e)}

    async def _modify_scene(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Modify existing scene elements"""
        try:
            modifications = action.get("modifications", {})

            # Apply modifications to context
            for key, value in modifications.items():
                if hasattr(context, key):
                    setattr(context, key, value)

            return {
                "status": "success",
                "modifications": modifications
            }
        except Exception as e:
            print(f"Error modifying scene: {e}")
            return {"status": "error", "message": str(e)}
    
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
