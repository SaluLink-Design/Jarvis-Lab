"""
API Routes for Jarvis Backend
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import uuid

router = APIRouter()


class TextRequest(BaseModel):
    """Request model for text-only commands"""
    text: str
    context_id: Optional[str] = None


class SceneRequest(BaseModel):
    """Request model for scene queries"""
    context_id: str


@router.post("/process")
async def process_request(
    text: Optional[str] = Form(None),
    context_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None)
):
    """
    Main endpoint for processing multimodal requests

    Accepts:
    - text: Natural language command
    - context_id: Existing scene context ID
    - image: Uploaded image file
    - video_url: YouTube or video URL
    """
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Handle image upload
    image_path = None
    if image:
        # Save uploaded file
        file_ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        image_path = os.path.join("uploads", filename)
        
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
    
    # Process the request
    try:
        result = await orchestrator.process_request(
            text=text,
            image_path=image_path,
            video_url=video_url,
            context_id=context_id
        )

        # Check if the orchestrator returned an error status
        if result.get("status") == "error":
            print(f"⚠️ Orchestrator returned error status")
            return result

        return result
    except Exception as e:
        import traceback
        from datetime import datetime
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"ERROR in process_request: {error_msg}")
        print(f"Traceback: {error_trace}")

        # Return error as a valid JSON response
        return {
            "context_id": str(uuid.uuid4()),
            "result": {
                "actions_executed": 0,
                "results": [],
                "success": False,
                "error": error_msg
            },
            "scene": {
                "scene_id": str(uuid.uuid4()),
                "objects": [],
                "environment": {},
                "lighting": {},
                "camera": {},
                "created_at": datetime.now().isoformat()
            },
            "status": "error",
            "message": f"Endpoint error: {error_msg}"
        }


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is responding",
        "endpoint": "/api/test"
    }


@router.post("/text")
async def process_text(request: TextRequest):
    """
    Process text-only commands
    """
    import traceback
    from datetime import datetime
    import sys

    error_response_template = {
        "context_id": str(uuid.uuid4()),
        "result": {
            "actions_executed": 0,
            "results": [],
            "success": False,
            "error": None
        },
        "scene": {
            "scene_id": str(uuid.uuid4()),
            "objects": [],
            "environment": {},
            "lighting": {},
            "camera": {},
            "created_at": datetime.now().isoformat()
        },
        "status": "error",
        "message": None
    }

    try:
        from main import orchestrator

        print(f"\n{'='*80}")
        print(f"[TEXT ENDPOINT] Received request")
        print(f"Text: {request.text[:100] if request.text else 'None'}...")
        print(f"Context ID: {request.context_id}")
        print(f"Orchestrator available: {orchestrator is not None}")
        print(f"{'='*80}\n")

        if not orchestrator:
            print("❌ Orchestrator is None!")
            error_response = error_response_template.copy()
            error_response["status"] = "error"
            error_response["message"] = "Orchestrator not initialized on server"
            error_response["result"]["error"] = "Orchestrator not initialized"
            return error_response

        print(f"✓ Orchestrator modules:")
        print(f"  - NLP: {orchestrator.nlp_processor is not None}")
        print(f"  - CV: {orchestrator.cv_processor is not None}")
        print(f"  - Text-to-3D: {orchestrator.text_to_3d is not None}")
        print(f"  - Scene Builder: {orchestrator.scene_builder is not None}")

        # Call orchestrator with proper async handling
        print(f"[TEXT ENDPOINT] Calling orchestrator.process_request...")
        try:
            result = await orchestrator.process_request(
                text=request.text,
                context_id=request.context_id
            )
            print(f"[TEXT ENDPOINT] Orchestrator returned successfully")
        except Exception as proc_error:
            print(f"❌ Orchestrator.process_request failed: {str(proc_error)}")
            print(traceback.format_exc())
            error_response = error_response_template.copy()
            error_response["status"] = "error"
            error_response["message"] = f"Processing error: {str(proc_error)}"
            error_response["result"]["error"] = str(proc_error)
            return error_response

        # Check response status
        if result.get("status") == "error":
            print(f"⚠️ Orchestrator returned error status: {result.get('message', 'Unknown error')}")
            return result

        print(f"✅ Successfully processed request. Context ID: {result.get('context_id', 'unknown')}")
        print(f"Objects created: {len(result.get('scene', {}).get('objects', []))}")
        return result

    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()

        print(f"\n{'='*80}")
        print(f"❌ CRITICAL ERROR in process_text endpoint")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {error_msg}")
        print(f"Full traceback:")
        print(error_trace)
        print(f"{'='*80}\n")

        # Make sure we return a valid response
        error_response = error_response_template.copy()
        error_response["status"] = "error"
        error_response["message"] = f"Server error: {error_msg}"
        error_response["result"]["error"] = error_msg
        return error_response


@router.get("/scene/{context_id}")
async def get_scene(context_id: str):
    """
    Get current scene state
    """
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    if context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    return orchestrator._serialize_context(context)


@router.delete("/scene/{context_id}")
async def delete_scene(context_id: str):
    """
    Delete a scene context
    """
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    if context_id in orchestrator.active_contexts:
        del orchestrator.active_contexts[context_id]
        return {"status": "deleted", "context_id": context_id}
    
    raise HTTPException(status_code=404, detail="Scene not found")


@router.get("/scenes")
async def list_scenes():
    """
    List all active scene contexts
    """
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    scenes = []
    for context_id, context in orchestrator.active_contexts.items():
        scenes.append({
            "context_id": context_id,
            "created_at": context.created_at.isoformat(),
            "object_count": len(context.objects),
            "has_environment": bool(context.environment)
        })
    
    return {"scenes": scenes, "count": len(scenes)}
