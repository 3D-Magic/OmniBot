#!/bin/bash

BOT_DIR="$HOME/OmniBot-v2.6.1"
SESSION_NAME="omnibot"

start_bot() {
    echo "🤖 Starting OmniBot v2.6.1 Sentinel..."
    cd "$BOT_DIR" || exit 1
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null
    tmux new-session -d -s "$SESSION_NAME"
    tmux send-keys -t "$SESSION_NAME" "cd $BOT_DIR && python3 src/main.py --mode aggressive" C-m
    sleep 3
    tmux split-window -t "$SESSION_NAME"
    tmux send-keys -t "$SESSION_NAME" "ngrok http 8081" C-m
    sleep 2
    echo "✅ OmniBot started!"
    echo "📊 Dashboard: http://localhost:8081"
    echo "🌐 Fetching ngrok URL..."
    sleep 3
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | cut -d'"' -f4)
    [ -n "$NGROK_URL" ] && echo "$NGROK_URL"
    echo ""
    echo "Commands:"
    echo "  View logs:  tmux attach -t $SESSION_NAME"
    echo "  Stop:       ./scripts/omnibot.sh stop"
}

stop_bot() {
    echo "🛑 Stopping OmniBot..."
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null
    pkill -9 python3 2>/dev/null
    pkill ngrok 2>/dev/null
    echo "✅ OmniBot stopped"
}

restart_bot() {
    stop_bot
    sleep 2
    start_bot
}

get_url() {
    curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | cut -d'"' -f4
}

case "$1" in
    start) start_bot ;;
    stop) stop_bot ;;
    restart) restart_bot ;;
    url) get_url ;;
    status) 
        if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo "✅ OmniBot is running"
            get_url
        else
            echo "❌ OmniBot is not running"
        fi ;;
    *) echo "Usage: ./omnibot.sh {start|stop|restart|url|status}"; exit 1 ;;
esac
