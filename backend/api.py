import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel
from backend.inference import chat
from monitor.logger import log_request, get_qps
import pynvml
from config import API_KEY, API_PORT

app = FastAPI(title="小豆包 API")
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



def verify_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


class ChatRequest(BaseModel):
    messages: list
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9


@app.post("/chat", dependencies=[Depends(verify_key)])
@limiter.limit("20/minute")
async def chat_endpoint(request: Request, req: ChatRequest):
    start = time.time()
    try:
        response = chat(
            req.messages,
            req.max_new_tokens,
            req.temperature,
            req.top_p
        )
        latency = time.time() - start
        log_request(latency)
        return {"response": response, "latency": round(latency, 2)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "qps": round(get_qps(), 3)}


@app.get("/monitor")
async def monitor(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_used = round(mem.used / 1024**3, 2)
        gpu_total = round(mem.total / 1024**3, 2)
    except Exception:
        gpu_used, gpu_total = -1, -1
    return {
        "gpu_used_gb": gpu_used,
        "gpu_total_gb": gpu_total,
        "qps": round(get_qps(), 3),
    }