"""
Agent CRUD Router

Manages AI agents, each with optional per-agent LLM provider selection.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreateRequest, AgentResponse, AgentUpdateRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """List all agents."""
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    agents = result.scalars().all()
    return [AgentResponse.model_validate(a) for a in agents]


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    req: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new agent with optional per-agent LLM configuration."""
    agent = Agent(
        name=req.name,
        description=req.description,
        llm_provider=req.llm_provider,
        llm_model=req.llm_model,
        system_prompt=req.system_prompt,
        language=req.language,
        voice=req.voice,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    logger.info("Created agent: %s (id=%d, provider=%s)", agent.name, agent.id, agent.llm_provider or "global")
    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    req: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update an agent, including its per-agent LLM provider/model."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if req.name is not None:
        agent.name = req.name
    if req.description is not None:
        agent.description = req.description
    if req.llm_provider is not None:
        agent.llm_provider = req.llm_provider if req.llm_provider else None
    if req.llm_model is not None:
        agent.llm_model = req.llm_model if req.llm_model else None
    if req.system_prompt is not None:
        agent.system_prompt = req.system_prompt
    if req.language is not None:
        agent.language = req.language
    if req.voice is not None:
        agent.voice = req.voice
    if req.is_active is not None:
        agent.is_active = req.is_active

    await db.flush()
    await db.refresh(agent)

    logger.info("Updated agent: %s (id=%d)", agent.name, agent.id)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.flush()

    logger.info("Deleted agent: %s (id=%d)", agent.name, agent_id)
    return {"message": f"Agent '{agent.name}' deleted"}
