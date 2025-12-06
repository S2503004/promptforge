
# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os, random
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PromptForge API")

MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'mock')
HF_MODEL = os.getenv('HF_MODEL', 'sshleifer/distilbart-cnn-6-6')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./promptforge.db')

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)

class PromptMetric(Base):
    __tablename__ = 'prompt_metrics'
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String)
    prompt = Column(String)
    output = Column(String)
    metrics = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    experiment_group = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

TEMPLATES = {
    "summarize_v1": "Summarize the following text in {tone} tone and <= {length} words:\n\n{text}",
    "qa_v1": "Given the context below, answer the question concisely. Context:\n{context}\nQuestion:{question}"
}

def render_template(tid, vars):
    tpl = TEMPLATES.get(tid, "")
    try:
        return tpl.format(**vars)
    except Exception:
        return tpl

def mock_model_generate(prompt: str) -> str:
    choices = [
        "Concise summary: This is an example output.",
        "Answer: The main point is X.",
        "Result: Model produced a plausible completion."
    ]
    return random.choice(choices)

def openai_generate(prompt: str, max_tokens: int = 150) -> str:
    try:
        import openai
    except Exception as e:
        raise HTTPException(status_code=500, detail="OpenAI SDK not installed")
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    openai.api_key = OPENAI_API_KEY
    resp = openai.Completion.create(engine=os.getenv('OPENAI_ENGINE', 'text-davinci-003'), prompt=prompt, max_tokens=max_tokens)
    return resp.choices[0].text.strip()

def hf_generate(prompt: str) -> str:
    # Note: local HF models require significant resources. Use HF Inference API for lightweight testing.
    from transformers import pipeline
    global _hf_pipe
    try:
        _hf_pipe
    except NameError:
        _hf_pipe = pipeline("summarization", model=HF_MODEL)
    out = _hf_pipe(prompt, max_length=150, truncation=True)
    if isinstance(out, list):
        return out[0].get('summary_text', str(out))
    return str(out)

def generate_inference(prompt: str) -> str:
    if MODEL_PROVIDER == 'openai':
        return openai_generate(prompt)
    elif MODEL_PROVIDER == 'hf':
        return hf_generate(prompt)
    else:
        return mock_model_generate(prompt)

def evaluate_prompt(prompt: str, output: str) -> Dict[str, float]:
    length_penalty = max(0, len(output.split()) / 100.0)
    relevance = random.uniform(0.6, 0.95)
    clarity = random.uniform(0.5, 0.98)
    return {"length_penalty": length_penalty, "relevance": relevance, "clarity": clarity}

class PromptRequest(BaseModel):
    template_id: str
    variables: Dict[str, Any] = {}
    experiment_group: Optional[str] = None

class PromptResponse(BaseModel):
    prompt: str
    model_output: str
    metrics: Dict[str, float]
    saved_id: Optional[int] = None

@app.post("/generate", response_model=PromptResponse)
def generate(req: PromptRequest):
    prompt = render_template(req.template_id, req.variables)
    out = generate_inference(prompt)
    metrics = evaluate_prompt(prompt, out)
    db = SessionLocal()
    pm = PromptMetric(template_id=req.template_id, prompt=prompt, output=out, metrics=metrics, experiment_group=req.experiment_group)
    db.add(pm)
    db.commit()
    db.refresh(pm)
    db.close()
    return {"prompt": prompt, "model_output": out, "metrics": metrics, "saved_id": pm.id}

@app.get("/templates")
def templates():
    return {"templates": list(TEMPLATES.keys())}

@app.get("/metrics/{template_id}")
def metrics(template_id: str, group: Optional[str] = None):
    db = SessionLocal()
    q = db.query(PromptMetric).filter(PromptMetric.template_id == template_id)
    if group:
        q = q.filter(PromptMetric.experiment_group == group)
    results = q.order_by(PromptMetric.timestamp.desc()).limit(100).all()
    db.close()
    return {"count": len(results), "results": [{ "id": r.id, "prompt": r.prompt, "output": r.output, "metrics": r.metrics, "experiment_group": r.experiment_group, "timestamp": r.timestamp.isoformat() } for r in results]}
