from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Optional

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

async def fake_data_streamer():
    for chunk in ["This ", "is ", "a ", "**streaming** ", "answer ", "from ", "the ", "`backend`."]:
        yield chunk
        await asyncio.sleep(0.1)

@app.post("/search")
async def search(question: str = Form(...), files: Optional[List[UploadFile]] = File(None)):
    """
    This endpoint receives a question and a list of files.
    It currently returns a streamed response with a fake answer.
    """
    # In a real implementation, you would process the question and files here.
    # For now, we'll just stream a fake response.
    return StreamingResponse(fake_data_streamer(), media_type="text/event-stream")