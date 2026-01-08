"""
Text-to-3D Generation Module

Generates 3D models from natural language descriptions.
"""
from typing import Dict, Any, Optional
import uuid
import json
import math


class TextTo3DGenerator:
    """
    Generates 3D models from text descriptions
    
    Note: This is a simplified implementation. In production, this would
    integrate with models like DreamFusion, Magic3D, or Shap-E.
    """
    
    def __init__(self):
        self.model_loaded = False
        self.primitive_shapes = {
            "cube": self._generate_cube,
            "sphere": self._generate_sphere,
            "cylinder": self._generate_cylinder,
            "cone": self._generate_cone,
            "plane": self._generate_plane
        }
        
    async def initialize(self):
        """Initialize the 3D generation model"""
        # In production, this would load actual ML models
        self.model_loaded = True
        print("✓ Text-to-3D Generator ready (using procedural fallback)")
    
    async def generate(
        self,
        prompt: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a 3D model from text

        Args:
            prompt: Text description of the object
            attributes: Additional attributes (color, size, material)

        Returns:
            3D model data in a structured format
        """
        print(f"[3D_GEN] Generating 3D model from prompt: {prompt}")

        try:
            if attributes is None:
                attributes = {}

            # Extract object type from prompt
            object_type = self._extract_object_type(prompt)
            print(f"[3D_GEN] Extracted object type: {object_type}")

            # Generate based on type
            if object_type in self.primitive_shapes:
                print(f"[3D_GEN] Using primitive shape generator for: {object_type}")
                model_data = self.primitive_shapes[object_type](attributes)
            elif object_type == "complex":
                # For complex objects (including from images), use specialized handling
                print(f"[3D_GEN] Using complex object generator for image-based request")
                model_data = self._generate_complex_object(prompt, attributes)
            else:
                # For other complex objects, create a placeholder
                print(f"[3D_GEN] Using complex object generator for: {object_type}")
                model_data = self._generate_complex_object(prompt, attributes)

            # Add metadata
            model_data.update({
                "id": str(uuid.uuid4()),
                "prompt": prompt,
                "type": object_type,
                "generated_by": "text_to_3d"
            })

            print(f"[3D_GEN] 3D model generated successfully")
            return model_data

        except Exception as e:
            print(f"❌ [3D_GEN] Error generating 3D model: {e}")
            import traceback
            traceback.print_exc()

            # Return a fallback cube
            return {
                "id": str(uuid.uuid4()),
                "prompt": prompt,
                "type": "cube",
                "generated_by": "text_to_3d_fallback",
                "error": str(e),
                "geometry": {
                    "type": "BoxGeometry",
                    "parameters": {
                        "width": 2.0,
                        "height": 2.0,
                        "depth": 2.0
                    }
                },
                "material": {
                    "type": "MeshStandardMaterial",
                    "color": "#0000ff",
                    "metalness": 0.3,
                    "roughness": 0.7
                },
                "position": [0, 1, 0]
            }
    
    def _extract_object_type(self, prompt: str) -> str:
        """Extract the main object type from the prompt"""
        prompt_lower = prompt.lower()
        
        for shape in self.primitive_shapes.keys():
            if shape in prompt_lower:
                return shape
        
        # Check for common objects
        if any(word in prompt_lower for word in ["tree", "forest"]):
            return "tree"
        elif any(word in prompt_lower for word in ["car", "vehicle"]):
            return "car"
        elif any(word in prompt_lower for word in ["house", "building"]):
            return "building"
        
        return "cube"  # Default
    
    def _generate_cube(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cube"""
        size = self._parse_size(attributes.get("size", "medium"))

        # Try to use hex color first (from images), fall back to color name
        color = attributes.get("hex_color") or self._parse_color(attributes.get("color", "gray"))

        return {
            "geometry": {
                "type": "BoxGeometry",
                "parameters": {
                    "width": size,
                    "height": size,
                    "depth": size
                }
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color,
                "metalness": 0.3,
                "roughness": 0.7
            },
            "position": [0, size / 2, 0]
        }
    
    def _generate_sphere(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a sphere"""
        size = self._parse_size(attributes.get("size", "medium"))
        color = self._parse_color(attributes.get("color", "gray"))
        
        return {
            "geometry": {
                "type": "SphereGeometry",
                "parameters": {
                    "radius": size / 2,
                    "widthSegments": 32,
                    "heightSegments": 32
                }
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color,
                "metalness": 0.2,
                "roughness": 0.8
            },
            "position": [0, size / 2, 0]
        }
    
    def _generate_cylinder(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cylinder"""
        size = self._parse_size(attributes.get("size", "medium"))
        color = self._parse_color(attributes.get("color", "gray"))
        
        return {
            "geometry": {
                "type": "CylinderGeometry",
                "parameters": {
                    "radiusTop": size / 2,
                    "radiusBottom": size / 2,
                    "height": size * 2,
                    "radialSegments": 32
                }
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color
            },
            "position": [0, size, 0]
        }
    
    def _generate_cone(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cone"""
        size = self._parse_size(attributes.get("size", "medium"))
        color = self._parse_color(attributes.get("color", "gray"))
        
        return {
            "geometry": {
                "type": "ConeGeometry",
                "parameters": {
                    "radius": size / 2,
                    "height": size * 1.5,
                    "radialSegments": 32
                }
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color
            },
            "position": [0, size * 0.75, 0]
        }
    
    def _generate_plane(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a plane (ground)"""
        size = self._parse_size(attributes.get("size", "large"))
        color = self._parse_color(attributes.get("color", "#228B22"))

        return {
            "geometry": {
                "type": "PlaneGeometry",
                "parameters": {
                    "width": size * 10,
                    "height": size * 10
                }
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color,
                "roughness": 0.9
            },
            "position": [0, 0, 0],
            "rotation": [-math.pi / 2, 0, 0]
        }
    
    def _generate_complex_object(
        self,
        prompt: str,
        attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate placeholder for complex objects"""
        # In production, this would use actual 3D generation models
        # For now, create a composite of primitives based on the prompt

        size = self._parse_size(attributes.get("size", "medium"))
        color = self._parse_color(attributes.get("color", "#4a5568"))  # default to gray

        prompt_lower = prompt.lower() if prompt else ""

        # Determine dominant colors from attributes
        dominant_colors = attributes.get("dominant_colors", [])
        if dominant_colors and isinstance(dominant_colors, list) and len(dominant_colors) > 0:
            # Try to use the dominant color from image
            rgb = dominant_colors[0]
            if isinstance(rgb, list) and len(rgb) >= 3:
                color = f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"

        # Create a more interesting composite based on what's in the image
        # For suits/armor/robots: tall humanoid shape
        if any(word in prompt_lower for word in ["suit", "armor", "robot", "character", "ironman", "iron man"]):
            return {
                "geometry": {
                    "type": "Group",
                    "children": [
                        # Head
                        {
                            **self._generate_sphere({"size": size * 0.6, "color": color}),
                            "position": [0, size * 1.4, 0]
                        },
                        # Torso
                        {
                            **self._generate_cube({"size": size * 0.8, "color": color}),
                            "position": [0, size * 0.7, 0]
                        },
                        # Left arm
                        {
                            **self._generate_cylinder({"size": size * 0.4, "color": color}),
                            "position": [-size * 0.6, size * 0.8, 0]
                        },
                        # Right arm
                        {
                            **self._generate_cylinder({"size": size * 0.4, "color": color}),
                            "position": [size * 0.6, size * 0.8, 0]
                        },
                        # Left leg
                        {
                            **self._generate_cylinder({"size": size * 0.5, "color": color}),
                            "position": [-size * 0.3, size * 0.2, 0]
                        },
                        # Right leg
                        {
                            **self._generate_cylinder({"size": size * 0.5, "color": color}),
                            "position": [size * 0.3, size * 0.2, 0]
                        }
                    ]
                },
                "material": {
                    "type": "MeshStandardMaterial",
                    "color": color,
                    "metalness": 0.6,  # Make it look more metallic for armor/suit
                    "roughness": 0.3
                },
                "position": [0, 0, 0],
                "note": f"3D model based on: {prompt}"
            }

        # For other complex objects, create a simple placeholder
        return {
            "geometry": {
                "type": "Group",
                "children": [
                    self._generate_cube({"size": size, "color": color})
                ]
            },
            "material": {
                "type": "MeshStandardMaterial",
                "color": color
            },
            "position": [0, 0, 0],
            "note": f"Placeholder for: {prompt}"
        }
    
    def _parse_size(self, size_str: str) -> float:
        """Convert size string to numeric value"""
        size_map = {
            "tiny": 0.5,
            "small": 1.0,
            "medium": 2.0,
            "large": 4.0,
            "huge": 8.0
        }
        return size_map.get(size_str.lower(), 2.0)
    
    def _parse_color(self, color: str) -> str:
        """Convert color name to hex code"""
        color_map = {
            "red": "#ff0000",
            "blue": "#0000ff",
            "green": "#00ff00",
            "yellow": "#ffff00",
            "white": "#ffffff",
            "black": "#000000",
            "gray": "#808080",
            "purple": "#800080",
            "orange": "#ffa500",
            "brown": "#8B4513"
        }
        
        # If already a hex code, return as is
        if color.startswith("#"):
            return color
        
        return color_map.get(color.lower(), "#808080")
