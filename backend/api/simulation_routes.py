"""
Simulation API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/simulation", tags=["simulation"])


class SimulationCommand(BaseModel):
    """Command for simulation control"""
    action: str
    params: Optional[Dict[str, Any]] = None


class ForceApplication(BaseModel):
    """Apply force to an object"""
    object_id: str
    force: List[float]


class AgentCommand(BaseModel):
    """Command for an agent"""
    agent_id: str
    command: str
    params: Dict[str, Any]


@router.post("/{context_id}/start")
async def start_simulation(context_id: str):
    """Start the simulation for a scene"""
    from backend.main import orchestrator

    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")

    context = orchestrator.active_contexts[context_id]

    # Initialize simulator if not exists
    if not hasattr(context, 'simulator'):
        from backend.simulation.simulator import Simulator
        context.simulator = Simulator()
        context.simulator.initialize({
            "objects": context.objects,
            "agents": []
        })
    
    context.simulator.start()
    
    return {
        "status": "started",
        "context_id": context_id,
        "simulation_time": context.simulator.simulation_time
    }


@router.post("/{context_id}/stop")
async def stop_simulation(context_id: str):
    """Stop the simulation"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if hasattr(context, 'simulator'):
        context.simulator.stop()
        return {
            "status": "stopped",
            "context_id": context_id
        }
    
    raise HTTPException(status_code=400, detail="No active simulation")


@router.post("/{context_id}/step")
async def step_simulation(context_id: str):
    """Advance simulation by one step"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if not hasattr(context, 'simulator'):
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    updates = context.simulator.step()
    
    return {
        "context_id": context_id,
        "updates": updates
    }


@router.get("/{context_id}/state")
async def get_simulation_state(context_id: str):
    """Get current simulation state"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if not hasattr(context, 'simulator'):
        return {"error": "Simulation not initialized"}
    
    return context.simulator.get_state()


@router.post("/{context_id}/force")
async def apply_force(context_id: str, force_data: ForceApplication):
    """Apply a force to an object"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if not hasattr(context, 'simulator'):
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    context.simulator.apply_force(force_data.object_id, force_data.force)
    
    return {
        "status": "force_applied",
        "object_id": force_data.object_id
    }


@router.post("/{context_id}/agent")
async def command_agent(context_id: str, cmd: AgentCommand):
    """Send a command to an agent"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if not hasattr(context, 'simulator'):
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    result = context.simulator.command_agent(cmd.agent_id, cmd.command, cmd.params)
    
    return result


@router.post("/{context_id}/reset")
async def reset_simulation(context_id: str):
    """Reset the simulation"""
    from main import orchestrator
    
    if not orchestrator or context_id not in orchestrator.active_contexts:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    context = orchestrator.active_contexts[context_id]
    
    if hasattr(context, 'simulator'):
        context.simulator.reset()
        return {"status": "reset", "context_id": context_id}
    
    raise HTTPException(status_code=400, detail="No simulation to reset")
