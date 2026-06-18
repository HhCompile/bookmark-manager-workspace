#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark Manager 一键启动脚本
支持 macOS/Linux/Windows
"""

import os
import sys
import subprocess
import signal
import time
import platform
from pathlib import Path

# 配置
BACKEND_DIR = "bookmark-manager-admin"
FRONTEND_DIR = "bookmark-manager-web"
BACKEND_PORT = 9001
FRONTEND_PORT = 3000

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

# Windows 不支持 ANSI 颜色
if platform.system() == "Windows":
    for attr in dir(Colors):
        if not attr.startswith('_'):
            setattr(Colors, attr, '')

processes = []

def log(msg, color=Colors.END):
    print(f"{color}{msg}{Colors.END}")

def cleanup(signum=None, frame=None):
    """清理所有子进程"""
    log("\n正在关闭服务...", Colors.YELLOW)
    
    for proc in processes:
        if proc.poll() is None:  # 进程仍在运行
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    
    log("所有服务已关闭", Colors.GREEN)
    sys.exit(0)

# 注册信号处理
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def start_backend():
    """启动后端服务"""
    log("启动后端服务...", Colors.BLUE)
    
    backend_path = Path(BACKEND_DIR).resolve()
    if not backend_path.exists():
        log(f"错误: 找不到后端目录 {BACKEND_DIR}", Colors.RED)
        return None
    
    # 构建命令
    cmd = ["python3", "run.py"]
    if platform.system() == "Windows":
        cmd = ["python", "run.py"]
    
    # 检查虚拟环境
    venv_paths = [
        backend_path / "venv_new" / "bin" / "activate",
        backend_path / "venv" / "bin" / "activate",
        backend_path / "venv_new" / "Scripts" / "activate.bat",
        backend_path / "venv" / "Scripts" / "activate.bat",
    ]
    
    env = os.environ.copy()
    for venv in venv_paths:
        if venv.exists():
            log(f"检测到虚拟环境: {venv.parent.name}", Colors.YELLOW)
            # 在 Unix 系统上使用 source 激活
            if platform.system() != "Windows":
                cmd = ["bash", "-c", f"source '{venv}' && python3 run.py"]
            break
    
    proc = subprocess.Popen(
        cmd,
        cwd=backend_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    return proc

def start_frontend():
    """启动前端服务"""
    log("启动前端服务...", Colors.BLUE)
    
    frontend_path = Path(FRONTEND_DIR).resolve()
    if not frontend_path.exists():
        log(f"错误: 找不到前端目录 {FRONTEND_DIR}", Colors.RED)
        return None
    
    # 检查 pnpm
    pnpm_cmd = "pnpm"
    npm_cmd = "npm"
    
    try:
        subprocess.run([pnpm_cmd, "--version"], capture_output=True, check=True)
        cmd = [pnpm_cmd, "dev"]
        log("使用 pnpm 启动前端", Colors.YELLOW)
    except (subprocess.CalledProcessError, FileNotFoundError):
        cmd = [npm_cmd, "run", "dev"]
        log("使用 npm 启动前端", Colors.YELLOW)
    
    proc = subprocess.Popen(
        cmd,
        cwd=frontend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    return proc

def stream_output(proc, prefix, color):
    """流式输出进程日志"""
    for line in proc.stdout:
        print(f"{color}[{prefix}]{Colors.END} {line.rstrip()}")

def main():
    log("=" * 37, Colors.GREEN)
    log("  Bookmark Manager 一键启动脚本", Colors.GREEN)
    log("=" * 37, Colors.GREEN)
    print()
    
    # 启动后端
    backend_proc = start_backend()
    if backend_proc:
        processes.append(backend_proc)
        log(f"后端服务已启动 (PID: {backend_proc.pid})", Colors.GREEN)
        log("等待后端初始化...", Colors.YELLOW)
        time.sleep(3)
    
    # 启动前端
    frontend_proc = start_frontend()
    if frontend_proc:
        processes.append(frontend_proc)
        log(f"前端服务已启动 (PID: {frontend_proc.pid})", Colors.GREEN)
    
    print()
    log("=" * 37, Colors.GREEN)
    log("  所有服务已启动！", Colors.GREEN)
    log("=" * 37, Colors.GREEN)
    print()
    log(f"前端地址: http://localhost:{FRONTEND_PORT}", Colors.BLUE)
    log(f"后端地址: http://localhost:{BACKEND_PORT}", Colors.BLUE)
    print()
    log("按 Ctrl+C 停止所有服务", Colors.YELLOW)
    print()
    
    # 同时监控两个进程的输出
    import threading
    
    if backend_proc:
        t1 = threading.Thread(target=stream_output, args=(backend_proc, "后端", Colors.BLUE))
        t1.daemon = True
        t1.start()
    
    if frontend_proc:
        t2 = threading.Thread(target=stream_output, args=(frontend_proc, "前端", Colors.GREEN))
        t2.daemon = True
        t2.start()
    
    # 等待进程结束
    try:
        while processes:
            for proc in processes[:]:
                if proc.poll() is not None:  # 进程已结束
                    processes.remove(proc)
            time.sleep(0.5)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
