import anyio.to_thread
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from smolagents import CodeAgent, InferenceClientModel
from deepengineer.deepsearch.main_agent import main_search


app = FastAPI()


class AgentRequest(BaseModel):
    task: str


@app.post("/deepsearch")
async def run_agent(request: AgentRequest):
    task = request.task
    # Run the agent synchronously in a background thread
    result = await anyio.to_thread.run_sync(main_search, task)
    return JSONResponse(content={"result": result})
