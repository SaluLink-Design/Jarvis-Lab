"""
Computer Vision Processor

Handles image and video analysis for 3D content generation.
"""
from typing import Dict, Any, List, Optional
import asyncio

# Try to import CV dependencies, use graceful fallback if unavailable
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    print("⚠️ Warning: OpenCV (cv2) not available, using fallback CV processor")
    HAS_CV2 = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    print("⚠️ Warning: NumPy not available")
    HAS_NUMPY = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    print("⚠️ Warning: PIL not available")
    HAS_PIL = False


class ComputerVisionProcessor:
    """
    Processes images and videos to extract visual features for 3D generation
    """
    
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Initialize CV models"""
        self.initialized = True
        print("✓ Computer Vision Processor ready")
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an uploaded image

        Args:
            image_path: Path to the image file

        Returns:
            Extracted visual features and detected objects
        """
        print(f"\n[CV_PROCESSOR] Starting image analysis")
        print(f"  Image path: {image_path}")

        # First, try PIL as it's more reliable for different image formats
        if HAS_PIL:
            try:
                print(f"[CV_PROCESSOR] Using PIL to load image...")
                from PIL import Image as PILImage
                img_pil = PILImage.open(image_path)
                width, height = img_pil.size
                print(f"[CV_PROCESSOR] PIL loaded successfully: {width}x{height}")

                # Convert to RGB if needed
                if img_pil.mode != 'RGB':
                    img_pil = img_pil.convert('RGB')

                # Try to extract colors using PIL
                dominant_colors = self._extract_colors_from_pil(img_pil)

                # Use PIL for basic analysis
                result = {
                    "dimensions": {"width": width, "height": height},
                    "dominant_colors": dominant_colors,
                    "complexity": 0.5,  # Default medium complexity
                    "depth_estimate": {"method": "pil_analysis", "avg_depth": 0.5},
                    "objects": [],
                    "style": {"style_type": "image", "mood": "neutral"},
                    "loaded_by": "PIL"
                }
                print(f"[CV_PROCESSOR] PIL analysis complete")
                return result
            except Exception as e:
                print(f"[CV_PROCESSOR] PIL analysis failed: {e}")
                # Fall through to CV2

        # Fall back to CV2 if available
        if HAS_CV2:
            try:
                print(f"[CV_PROCESSOR] Using OpenCV (cv2) to load image...")
                img = cv2.imread(image_path)
                if img is None:
                    print(f"[CV_PROCESSOR] OpenCV failed to load image, trying alternative methods")
                    return {"error": "Could not load image with OpenCV"}

                # Convert to RGB
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Basic analysis
                height, width = img.shape[:2]
                print(f"[CV_PROCESSOR] OpenCV loaded: {width}x{height}")

                # Detect dominant colors
                dominant_colors = self._extract_dominant_colors(img_rgb)

                # Simple edge detection for complexity
                edges = cv2.Canny(img, 100, 200)
                complexity = np.sum(edges > 0) / (height * width)

                # Estimate depth (simplified)
                depth_info = self._estimate_depth(img_rgb)

                result = {
                    "dimensions": {"width": width, "height": height},
                    "dominant_colors": dominant_colors,
                    "complexity": float(complexity),
                    "depth_estimate": depth_info,
                    "objects": [],
                    "style": self._analyze_style(img_rgb),
                    "loaded_by": "OpenCV"
                }
                print(f"[CV_PROCESSOR] OpenCV analysis complete")
                return result

            except Exception as e:
                print(f"[CV_PROCESSOR] OpenCV analysis failed: {e}")
                import traceback
                traceback.print_exc()
                return {"error": str(e)}

        # Minimal fallback if nothing is available
        print(f"[CV_PROCESSOR] No image processing libraries available")
        return {
            "dimensions": {"width": 0, "height": 0},
            "dominant_colors": [],
            "complexity": 0.5,
            "depth_estimate": {},
            "objects": [],
            "style": {"style_type": "unknown"},
            "warning": "No image processing libraries available - using defaults"
        }
    
    async def process_video(self, video_url: str) -> Dict[str, Any]:
        """
        Analyze a video (YouTube or local)
        
        Args:
            video_url: URL or path to video
            
        Returns:
            Extracted temporal features and motion data
        """
        return {
            "frames_analyzed": 0,
            "motion_detected": False,
            "key_moments": [],
            "objects_tracked": [],
            "error": "Video processing not yet implemented"
        }
    
    def _extract_colors_from_pil(self, pil_img) -> List[List[int]]:
        """Extract dominant colors from PIL image"""
        try:
            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')

            # Resize for faster processing
            pil_img.thumbnail((100, 100))

            # Get the image data
            pixels = list(pil_img.getdata())

            if not pixels:
                return []

            # Simple color extraction - get unique colors
            unique_colors = {}
            for pixel in pixels:
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    rgb = tuple(pixel[:3])
                    unique_colors[rgb] = unique_colors.get(rgb, 0) + 1

            # Get top 5 most common colors
            sorted_colors = sorted(unique_colors.items(), key=lambda x: x[1], reverse=True)
            top_colors = [list(color[0]) for color in sorted_colors[:5]]

            return top_colors
        except Exception as e:
            print(f"[CV_PROCESSOR] Error extracting colors from PIL: {e}")
            return []

    def _extract_dominant_colors(self, img, k: int = 5) -> List[List[int]]:
        """Extract dominant colors using k-means clustering"""
        if not HAS_NUMPY:
            return []

        try:
            # Reshape image to be a list of pixels
            pixels = img.reshape(-1, 3)

            # Sample for performance
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]

            # Simple color extraction (could use k-means for better results)
            unique_colors = np.unique(pixels, axis=0)

            # Return top 5 most common
            colors = unique_colors[:min(k, len(unique_colors))]
            return [color.tolist() for color in colors]
        except Exception as e:
            print(f"[CV_PROCESSOR] Error in color extraction: {e}")
            return []
    
    def _estimate_depth(self, img) -> Dict[str, Any]:
        """Simplified depth estimation"""
        if not HAS_CV2 or not HAS_NUMPY:
            return {"method": "unavailable", "avg_depth": 0.0}

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Use intensity as rough depth proxy
        avg_intensity = np.mean(gray)

        return {
            "method": "intensity_proxy",
            "avg_depth": float(avg_intensity / 255.0),
            "has_depth_variation": float(np.std(gray) / 128.0)
        }
    
    def _analyze_style(self, img) -> Dict[str, Any]:
        """Analyze artistic/visual style"""
        if not HAS_CV2 or not HAS_NUMPY:
            return {"style_type": "unknown"}

        # Simple style analysis based on color distribution and edges
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # Saturation analysis
        saturation = hsv[:, :, 1]
        avg_saturation = np.mean(saturation)

        # Brightness
        brightness = hsv[:, :, 2]
        avg_brightness = np.mean(brightness)

        style = "realistic"
        if avg_saturation < 50:
            style = "grayscale" if avg_saturation < 20 else "muted"
        elif avg_saturation > 150:
            style = "vibrant"

        return {
            "style_type": style,
            "saturation": float(avg_saturation),
            "brightness": float(avg_brightness),
            "mood": "bright" if avg_brightness > 150 else "dark"
        }
