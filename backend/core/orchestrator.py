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
            has_text = text_analysis and not text_analysis.get("error")
            has_image = image_analysis and not image_analysis.get("error")

            print(f"[ACTION_PLAN] Has text: {has_text}, Has image: {has_image}")

            # Analyze intent from text
            if has_text:
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
                                # Merge image attributes with text attributes
                                merged_attrs = self._merge_attributes(
                                    entity.get("attributes", {}),
                                    image_analysis
                                )
                                plan.append({
                                    "action": "generate_object",
                                    "object_type": entity.get("value"),
                                    "attributes": merged_attrs
                                })
                            elif entity.get("type") == "environment":
                                plan.append({
                                    "action": "generate_environment",
                                    "environment_type": entity.get("value")
                                })
                    else:
                        # No entities found, create a default object with image attributes
                        print(f"[ACTION_PLAN] No entities found in text, using default object with image attributes")
                        image_attrs = self._extract_image_attributes(image_analysis)
                        plan.append({
                            "action": "generate_object",
                            "object_type": "cube",
                            "attributes": {**attributes, **image_attrs}
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

            # Handle image-only input (no text)
            elif has_image:
                print(f"[ACTION_PLAN] Image analysis available but no text command")
                # Create objects based on image analysis
                image_attrs = self._extract_image_attributes(image_analysis)
                print(f"[ACTION_PLAN] Image attributes extracted: {image_attrs}")

                # Create a sphere or geometric shape based on image complexity
                complexity = image_analysis.get("complexity", 0.5)
                if complexity > 0.5:
                    object_type = "sphere"
                else:
                    object_type = "cube"

                plan.append({
                    "action": "generate_object",
                    "object_type": object_type,
                    "attributes": image_attrs,
                    "source": "image_analysis"
                })

            # Enhance with image data if both text and image exist
            if has_image and has_text:
                print(f"[ACTION_PLAN] Enhancing plan with image styling")
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

    def _extract_image_attributes(self, image_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract useful attributes from image analysis"""
        attributes = {}

        # Extract dominant color
        dominant_colors = image_analysis.get("dominant_colors", [])
        if dominant_colors:
            # Convert RGB to color name
            color_rgb = dominant_colors[0]
            if isinstance(color_rgb, list) and len(color_rgb) >= 3:
                color_name = self._rgb_to_color_name(color_rgb)
                if color_name:
                    attributes["color"] = color_name

        # Extract style information
        style = image_analysis.get("style", {})
        if style and not style.get("error"):
            if style.get("style_type"):
                attributes["style"] = style.get("style_type")
            if style.get("mood"):
                attributes["mood"] = style.get("mood")

        # Add complexity-based size hint
        complexity = image_analysis.get("complexity", 0.5)
        if complexity > 0.7:
            attributes["complexity"] = "high"
        elif complexity < 0.3:
            attributes["complexity"] = "low"

        return attributes

    def _merge_attributes(
        self,
        text_attributes: Dict[str, Any],
        image_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge text-based and image-based attributes"""
        merged = text_attributes.copy()

        # Add image attributes only if not already specified in text
        image_attrs = self._extract_image_attributes(image_analysis)
        for key, value in image_attrs.items():
            if key not in merged:
                merged[key] = value

        return merged

    def _rgb_to_color_name(self, rgb: List[int]) -> Optional[str]:
        """Convert RGB values to color names"""
        if len(rgb) < 3:
            return None

        r, g, b = rgb[0], rgb[1], rgb[2]

        # Simple color name mapping based on RGB values
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 128, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (128, 128, 128)
        }

        # Find closest color
        min_distance = float('inf')
        closest_color = None

        for color_name, (cr, cg, cb) in color_map.items():
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name

        # Only return color if it's reasonably close
        if min_distance < 100:
            return closest_color

        return None
    
    async def _execute_action_plan(
        self,
        action_plan: List[Dict[str, Any]],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Execute the planned actions"""
        print(f"[EXECUTOR] Executing {len(action_plan)} actions")
        results = []

        for i, action in enumerate(action_plan):
            action_type = action.get("action", "unknown")
            print(f"[EXECUTOR] Action {i+1}/{len(action_plan)}: {action_type}")

            try:
                if action_type == "generate_object":
                    result = await self._generate_object(action, context)
                    results.append(result)
                    print(f"[EXECUTOR]   ✓ Generated object: {action.get('object_type')}")

                elif action_type == "generate_environment":
                    result = await self._generate_environment(action, context)
                    results.append(result)
                    print(f"[EXECUTOR]   ✓ Generated environment")

                elif action_type == "modify_scene":
                    result = await self._modify_scene(action, context)
                    results.append(result)
                    print(f"[EXECUTOR]   ✓ Modified scene")

                elif action_type == "delete_objects":
                    result = await self._delete_objects(action, context)
                    results.append(result)
                    print(f"[EXECUTOR]   ✓ Deleted objects")

                else:
                    print(f"[EXECUTOR]   ⚠️ Unknown action type: {action_type}")
                    results.append({
                        "status": "error",
                        "action": action_type,
                        "error": f"Unknown action type: {action_type}"
                    })

            except Exception as e:
                print(f"[EXECUTOR]   ❌ Error executing {action_type}: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "status": "error",
                    "action": action_type,
                    "error": str(e)
                })

        success_count = len([r for r in results if r.get("status") == "success"])
        print(f"[EXECUTOR] Execution complete. {success_count}/{len(results)} successful")

        return {
            "actions_executed": len(results),
            "results": results,
            "success": success_count > 0
        }
    
    async def _generate_object(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Generate a 3D object"""
        import traceback

        object_type = action.get("object_type", "cube")
        attributes = action.get("attributes", {})

        print(f"[GENERATOR] Generating object: {object_type}, attributes: {attributes}")

        try:
            # Use text-to-3D generator
            if self.text_to_3d:
                try:
                    print(f"[GENERATOR] Calling text_to_3d.generate...")
                    object_data = await self.text_to_3d.generate(
                        prompt=f"a {object_type}",
                        attributes=attributes
                    )
                    print(f"[GENERATOR] Generated object data received")

                    # Add to context
                    context.objects.append(object_data)
                    print(f"[GENERATOR] Added object to context. Total objects: {len(context.objects)}")

                    return {
                        "status": "success",
                        "object": object_data
                    }
                except Exception as gen_error:
                    print(f"⚠️ [GENERATOR] Error in text_to_3d.generate: {gen_error}")
                    traceback.print_exc()
                    raise

            print(f"⚠️ [GENERATOR] text_to_3d generator not available")
            return {
                "status": "error",
                "message": "3D generator not available"
            }
        except Exception as e:
            print(f"❌ [GENERATOR] Error generating object: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": str(e),
                "object_type": object_type
            }
    
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

    async def _delete_objects(
        self,
        action: Dict[str, Any],
        context: SceneContext
    ) -> Dict[str, Any]:
        """Delete objects from the scene"""
        try:
            targets = action.get("targets", [])
            deleted_count = 0

            # If no targets specified, delete all objects
            if not targets:
                deleted_count = len(context.objects)
                context.objects = []
                return {
                    "status": "success",
                    "deleted_count": deleted_count,
                    "message": f"Deleted all {deleted_count} objects"
                }

            # Delete specific targets by index or name
            for target in targets:
                if isinstance(target, int):
                    # Delete by index
                    if 0 <= target < len(context.objects):
                        context.objects.pop(target)
                        deleted_count += 1
                elif isinstance(target, dict):
                    # Delete by matching attributes
                    target_value = target.get("value", "")
                    context.objects = [obj for obj in context.objects if obj.get("type") != target_value]
                    deleted_count += 1
                elif isinstance(target, str):
                    # Delete by object type or id
                    context.objects = [obj for obj in context.objects if obj.get("type") != target and obj.get("id") != target]
                    deleted_count += 1

            return {
                "status": "success",
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} object(s)"
            }
        except Exception as e:
            print(f"Error deleting objects: {e}")
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
