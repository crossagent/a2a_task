# -*- coding: utf-8 -*-
"""
Main entry point for the AI Workflow Automation application.

FastAPI web application with WebSocket support for streaming responses.
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from google.genai.types import Content, Part

# 导入 FastAPI 相关库
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 导入 ADK 相关库
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

# 导入自定义组件
from src.core.runner_setup import setup_runner, session_service
from src.agent import root_agent
# TODO: Import WorkflowPlan model when needed
# from src.models.workflow_plan import WorkflowPlan, WorkflowStep

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
APP_NAME = "ai_workflow_automator"
DEFAULT_MODEL = "gemini-2.5-flash"  # Or choose another like "openai/gpt-4o" if keys are set

# 创建 FastAPI 应用
app = FastAPI(title="AI Workflow Automator API")

# 设置静态文件目录（如果存在）
STATIC_DIR = Path("static")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def start_agent_session(session_id: str):
    """启动一个代理会话，使用现有的 session_service"""
    
    # 创建会话，使用从 runner_setup 导入的 session_service
    user_id = session_id  # 使用相同的 ID 简化
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    
    # 创建 Runner，使用 setup_runner 从 runner_setup
    runner = setup_runner(root_agent=root_agent, app_name=APP_NAME)
    
    # 设置响应模式为 TEXT
    run_config = RunConfig(response_modalities=["TEXT"])
    
    # 为此会话创建 LiveRequestQueue
    live_request_queue = LiveRequestQueue()
    
    # 启动代理会话
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    """代理到客户端的通信"""
    while True:
        async for event in live_events:
            # 回合完成
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
                print("[TURN COMPLETE]")
                
            # 中断
            if event.interrupted:
                await websocket.send_text(json.dumps({"interrupted": True}))
                print("[INTERRUPTED]")
                
            # 读取 Content 和它的第一个 Part
            part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part or not event.partial:
                continue
                
            # 获取文本
            text = event.content and event.content.parts and event.content.parts[0].text
            if not text:
                continue
                
            # 将文本发送给客户端
            await websocket.send_text(json.dumps({"message": text}))
            print(f"[AGENT TO CLIENT]: {text}")
            await asyncio.sleep(0)

async def client_to_agent_messaging(websocket, live_request_queue):
    """客户端到代理的通信"""
    while True:
        text = await websocket.receive_text()
        content = Content(role="user", parts=[Part.from_text(text=text)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {text}")
        await asyncio.sleep(0)

# FastAPI 路由

@app.get("/")
async def root():
    """提供 index.html"""
    if (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    return {"message": "AI Workflow Automator API is running",
            "info": "Connect via WebSocket at /ws/{session_id}"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """客户端 WebSocket 端点"""
    
    # 等待客户端连接
    await websocket.accept()
    print(f"Client #{session_id} connected")
    
    # 启动代理会话
    session_id_str = str(session_id)
    live_events, live_request_queue = start_agent_session(session_id_str)
    
    # 启动任务
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    
    try:
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 断开连接
        print(f"Client #{session_id} disconnected")

# 保留原始的命令行应用函数
async def run_cli():
    """以命令行界面运行应用程序"""
    print("--- Initializing AI Workflow Automator (CLI Mode) ---")
    
    # 使用已创建的 root_agent
    # 设置 Runner
    runner = setup_runner(root_agent=root_agent, app_name=APP_NAME)
    
    # 设置用户和会话
    user_id = "cli_user"
    session_id = "cli_session"
    
    # 创建或获取会话
    try:
        session = session_service.get_session(APP_NAME, user_id, session_id)
        print(f"Resumed existing session: {session_id}")
    except KeyError:
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        print(f"Created new session: {session_id}")
    print(f"Initial Session State: {session.state}")
    
    # 基本交互循环
    print("\n--- Starting Interaction (type 'quit' to exit) ---")
    while True:
        user_input = input(">>> User: ")
        if user_input.lower() == 'quit':
            break
            
        # 准备用户消息
        user_message = Content(role='user', parts=[Part(text=user_input)])
        
        final_response_text = "Agent did not produce a final response."
        try:
            # 运行协调器
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
                if event.actions and event.actions.escalate:
                    print(f"<<< Agent needs input (Escalated): {event.content.parts[0].text if event.content else 'No message.'}")
                    continue
                    
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.error_message:
                        final_response_text = f"Agent Error: {event.error_message}"
                    print(f"<<< Agent: {final_response_text}")
                    break
                    
        except Exception as e:
            print(f"An error occurred during agent execution: {e}")

# 入口点
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Workflow Automator")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of web server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    
    args = parser.parse_args()
    
    if args.cli:
        # CLI 模式
        asyncio.run(run_cli())
    else:
        # Web 服务器模式
        print(f"Starting server at http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
