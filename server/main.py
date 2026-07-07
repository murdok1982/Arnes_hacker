import asyncio
import json
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from core.orchestrator import Orchestrator
from core.llm_factory import get_available_models, detect_hardware, suggest_model
from core.tool_registry import tool_registry, TOOL_REGISTRY

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8080"))
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "server" / "templates"
STATIC_DIR = BASE_DIR / "static"

orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Arnes Hacker v2", lifespan=lifespan)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = TEMPLATES_DIR / "terminal.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text("utf-8"))
    return HTMLResponse("<h1>Arnes Hacker v2</h1><p>Terminal not found</p>")


@app.get("/api/status")
async def status():
    models = await get_available_models()
    hardware = detect_hardware()
    return {
        "ollama_running": len(models) > 0,
        "models": models,
        "suggested_model": suggest_model(hardware),
        "current_model": orchestrator.suggested_model,
        "hardware": hardware,
        "tools_available": tool_registry.available_count,
        "tools_total": tool_registry.total,
        "tools_missing": tool_registry.missing_critical(),
        "sessions": [
            {"id": s["id"], "mission": s["mission"][:80], "status": s["status"], "created": s["created_at"]}
            for s in orchestrator.session_manager.get_recent_sessions(10)
        ],
    }


@app.get("/api/models")
async def list_models():
    models = await get_available_models()
    hardware = detect_hardware()
    return {"models": models, "hardware": hardware, "suggested": suggest_model(hardware), "current": orchestrator.suggested_model}


@app.post("/api/models/select")
async def select_model(data: dict):
    model = data.get("model", "")
    if model:
        orchestrator.suggested_model = model
        if orchestrator.llm:
            await orchestrator.init_llm(model)
    return {"status": "ok", "model": model}


@app.get("/api/sessions")
async def list_sessions():
    return {"sessions": orchestrator.session_manager.get_recent_sessions(30)}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = orchestrator.session_manager.get_session(session_id)
    if not session:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    logs = orchestrator.session_manager.get_logs(session_id)
    results = orchestrator.session_manager.get_results(session_id)
    return {"session": session, "logs": logs, "results": results}


@app.get("/api/sessions/{session_id}/export")
async def export_session(session_id: str):
    session = orchestrator.session_manager.get_session(session_id)
    if not session:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    data = orchestrator.session_manager.export_session_json(session_id)
    return JSONResponse(content=data, headers={"Content-Disposition": f'attachment; filename="mission_{session_id}.json"'})


@app.get("/api/tools")
async def list_tools():
    return {
        "tools": [
            {"name": t.name, "description": t.description, "category": t.category, "available": t.available()}
            for t in TOOL_REGISTRY
        ],
        "available_count": tool_registry.available_count,
        "total": tool_registry.total,
        "missing_critical": tool_registry.missing_critical(),
    }


@app.get("/api/hardware")
async def hardware_info():
    hw = detect_hardware()
    return {"hardware": hw, "suggested_model": suggest_model(hw), "current_model": orchestrator.suggested_model}


@app.get("/api/credentials")
async def list_credentials(session_id: str = ""):
    if session_id:
        return {"credentials": orchestrator.session_manager.get_credentials(session_id)}
    return {"credentials": orchestrator.session_manager.get_credentials()}


@app.get("/api/targets")
async def list_targets(session_id: str = ""):
    if session_id:
        return {"targets": orchestrator.session_manager.get_targets(session_id)}
    return {"targets": orchestrator.session_manager.get_targets()}


@app.get("/api/playbooks")
async def list_playbooks():
    return {"playbooks": orchestrator.session_manager.get_playbooks()}


@app.post("/api/playbooks")
async def add_playbook(data: dict):
    orchestrator.session_manager.add_playbook(
        name=data.get("name", ""),
        description=data.get("description", ""),
        agents=data.get("agents", ""),
        prompt_template=data.get("prompt_template", ""),
    )
    return {"status": "ok"}


@app.post("/api/credentials")
async def add_credential(data: dict):
    orchestrator.session_manager.add_credential(
        session_id=data.get("session_id", ""),
        target=data.get("target", ""),
        username=data.get("username", ""),
        password=data.get("password", ""),
        hash_value=data.get("hash", ""),
        service=data.get("service", ""),
        source=data.get("source", "manual"),
    )
    return {"status": "ok"}


@app.post("/api/targets")
async def add_target(data: dict):
    orchestrator.session_manager.add_target(
        session_id=data.get("session_id", ""),
        target=data.get("target", ""),
        hostname=data.get("hostname", ""),
        ports=data.get("ports", ""),
        os=data.get("os", ""),
        services=data.get("services", ""),
    )
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send(msg: dict):
        try:
            await websocket.send_text(json.dumps(msg, ensure_ascii=False))
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            action = msg.get("action", "")

            if action == "mission":
                mission = msg.get("mission", "")
                model = msg.get("model", orchestrator.suggested_model)
                agent = msg.get("agent", "auto")

                if agent and agent != "auto":
                    gen = orchestrator.run_single_agent_stream(agent, mission, model)
                else:
                    gen = orchestrator.run_mission_stream(mission, model)

                async for event in gen:
                    await send(event)
                await send({"type": "ws_done"})

            elif action == "shell":
                command = msg.get("command", "")
                session_id = msg.get("session_id", orchestrator.current_session_id or "")
                if not session_id:
                    session_id = orchestrator.session_manager.create_session(f"[shell] {command[:50]}")
                    orchestrator.current_session_id = session_id
                result = await orchestrator.execute_shell(command, session_id)
                await send({
                    "type": "shell_result",
                    "command": command,
                    "stdout": result.stdout[:5000],
                    "stderr": result.stderr[:1000],
                    "exit_code": result.exit_code,
                    "success": result.success,
                    "session_id": session_id,
                })

            elif action == "stop":
                orchestrator.stop()
                await send({"type": "system", "content": "Mision abortada"})

            elif action == "check_ollama":
                models = await get_available_models()
                await send({"type": "ollama_status", "running": len(models) > 0, "models": models})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await send({"type": "error", "content": str(e)})
        except Exception:
            pass


def main():
    import uvicorn
    print(f"\n  ARNES HACKER v2.0")
    print(f"  ─────────────────")
    print(f"  Servidor: http://{HOST}:{PORT}")
    print(f"  Terminal: http://{HOST}:{PORT}/")
    print(f"  API:      http://{HOST}:{PORT}/api/status")
    print()
    uvicorn.run("server.main:app", host=HOST, port=PORT, reload=False, log_level="warning")


if __name__ == "__main__":
    main()
