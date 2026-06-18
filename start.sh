#!/bin/bash
# 一键启动 Bookmark Manager 前端和后端服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 进程 ID 存储
FRONTEND_PID=""
BACKEND_PID=""

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在关闭服务...${NC}"
    
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${BLUE}关闭前端服务 (PID: $FRONTEND_PID)...${NC}"
        kill "$FRONTEND_PID" 2>/dev/null
        wait "$FRONTEND_PID" 2>/dev/null
    fi
    
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${BLUE}关闭后端服务 (PID: $BACKEND_PID)...${NC}"
        kill "$BACKEND_PID" 2>/dev/null
        wait "$BACKEND_PID" 2>/dev/null
    fi
    
    echo -e "${GREEN}所有服务已关闭${NC}"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Bookmark Manager 一键启动脚本${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# 检查后端虚拟环境
BACKEND_DIR="bookmark-manager-admin"
FRONTEND_DIR="bookmark-manager-web"

# 启动后端服务
echo -e "${BLUE}启动后端服务...${NC}"
cd "$BACKEND_DIR" || exit 1

# 激活虚拟环境（如果存在）
if [ -d "venv_new" ]; then
    echo -e "${YELLOW}检测到虚拟环境，正在激活...${NC}"
    source venv_new/bin/activate
elif [ -d "venv" ]; then
    echo -e "${YELLOW}检测到虚拟环境，正在激活...${NC}"
    source venv/bin/activate
fi

# 后台启动后端
python3 run.py &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo -e "${YELLOW}等待后端初始化...${NC}"
sleep 2

# 启动前端服务
echo -e "${BLUE}启动前端服务...${NC}"
cd "$FRONTEND_DIR" || exit 1

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}未检测到 pnpm，尝试使用 npm...${NC}"
    npm run dev &
else
    pnpm dev &
fi

FRONTEND_PID=$!
cd ..

echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  所有服务已启动！${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}前端地址: http://localhost:3000${NC}"
echo -e "${BLUE}后端地址: http://localhost:9001${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 等待进程
wait
