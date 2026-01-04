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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
async def process_text(request: TextRequest):
    """
    Process text-only commands
    """
    from main import orchestrator
    import traceback

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        result = await orchestrator.process_request(
            text=request.text,
            context_id=request.context_id
        )
        return result
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"ERROR in process_text: {error_msg}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Processing error: {error_msg}")


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
