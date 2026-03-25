from flask import Flask, jsonify, request, render_template_string
import subprocess
import threading
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OmniBot v2.6.1 Sentinel</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; margin: 0; padding: 20px; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .status-badge { background: #00ff88; color: black; padding: 8px 16px; border-radius: 20px; font-weight: bold; }
        .controls { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; margin-bottom: 20px; }
        .mode-btn { padding: 12px 24px; margin: 5px; border: 2px solid rgba(255,255,255,0.3); border-radius: 8px; cursor: pointer; background: rgba(255,255,255,0.1); color: white; font-size: 14px; transition: all 0.3s; }
        .mode-btn:hover { background: rgba(255,255,255,0.3); }
        .mode-btn.active { background: #00d4ff; color: black; border-color: #00d4ff; font-weight: bold; }
        .update-btn { padding: 14px 28px; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); border: none; border-radius: 8px; color: black; font-weight: bold; cursor: pointer; margin: 5px; font-size: 14px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .stat-card { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; }
        .stat-card h3 { margin: 0 0 10px 0; color: #aaa; font-size: 14px; text-transform: uppercase; }
        .stat-card h2 { margin: 0; font-size: 32px; font-weight: bold; }
        .positive { color: #00ff88; }
        .negative { color: #ff4757; }
        #status { margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; min-height: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 OmniBot v2.6.1 Sentinel</h1>
            <span class="status-badge">● RUNNING</span>
        </div>
        <div class="controls">
            <h3 style="margin-top: 0;">Trading Mode</h3>
            <button class="mode-btn" onclick="setMode('conservative')">Conservative</button>
            <button class="mode-btn" onclick="setMode('moderate')">Moderate</button>
            <button class="mode-btn active" onclick="setMode('aggressive')">Aggressive</button>
            <button class="mode-btn" onclick="setMode('hft')">HFT Scalper</button>
            <button class="mode-btn" onclick="setMode('sentinel')">Sentinel</button>
            <br><br>
            <button class="update-btn" onclick="checkUpdate()">🔍 Check for Updates</button>
            <button class="update-btn" onclick="restartBot()">🔄 Restart Bot</button>
            <div id="status">Ready</div>
        </div>
        <div class="stats">
            <div class="stat-card">
                <h3>Total Portfolio Value</h3>
                <h2>$100,000.00</h2>
                <p class="positive">▲ +17.5% all time</p>
            </div>
            <div class="stat-card">
                <h3>Today's P&L</h3>
                <h2 class="positive">+$1,250.00</h2>
                <p class="positive">▲ +1.25% today</p>
            </div>
            <div class="stat-card">
                <h3>Active Positions</h3>
                <h2>5</h2>
                <p>Open trades</p>
            </div>
            <div class="stat-card">
                <h3>Win Rate</h3>
                <h2>64.2%</h2>
                <p>Last 30 days</p>
            </div>
        </div>
    </div>
    <script>
        let currentMode = 'aggressive';
        function setMode(mode) {
            fetch('/api/mode', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({mode: mode}) })
            .then(r => r.json()).then(data => {
                if(data.success) {
                    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                    event.target.classList.add('active');
                    currentMode = mode;
                    document.getElementById('status').textContent = '✓ Mode set to: ' + mode;
                    document.getElementById('status').style.color = '#00ff88';
                }
            });
        }
        function checkUpdate() {
            document.getElementById('status').textContent = '🔍 Checking...';
            fetch('/api/update/check').then(r => r.json()).then(data => {
                document.getElementById('status').textContent = data.updateAvailable ? '⚠️ Update available: ' + data.latestVersion : '✓ Up to date (v2.6.1)';
                document.getElementById('status').style.color = data.updateAvailable ? '#ff4757' : '#00ff88';
            });
        }
        function restartBot() {
            document.getElementById('status').textContent = '🔄 Restarting...';
            fetch('/api/restart', {method: 'POST'}).then(r => r.json()).then(data => {
                document.getElementById('status').textContent = '✓ Restart initiated';
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/status")
def status():
    return jsonify({"version": "v2.6.1 Sentinel", "mode": "aggressive", "uptime": "Running", "update_available": False})

@app.route("/api/mode", methods=["POST"])
def set_mode():
    mode = request.json.get("mode", "aggressive")
    print(f"[API] Mode changed to: {mode}")
    return jsonify({"success": True, "mode": mode})

@app.route("/api/update/check")
def check_update():
    return jsonify({"updateAvailable": False, "currentVersion": "v2.6.1", "latestVersion": "v2.6.1"})

@app.route("/api/update/apply", methods=["POST"])
def apply_update():
    def update():
        time.sleep(2)
        subprocess.Popen(["bash", "-c", "cd ~/OmniBot-v2.6.1 && ./scripts/omnibot.sh restart --ngrok"])
    threading.Thread(target=update, daemon=True).start()
    return jsonify({"success": True, "message": "Update started"})

@app.route("/api/restart", methods=["POST"])
def restart():
    def do_restart():
        time.sleep(2)
        subprocess.Popen(["bash", "-c", "cd ~/OmniBot-v2.6.1 && ./scripts/omnibot.sh restart --ngrok"])
    threading.Thread(target=do_restart, daemon=True).start()
    return jsonify({"success": True, "message": "Restarting..."})

@app.route("/api/positions")
def get_positions():
    return jsonify({"positions": [{"symbol": "AAPL", "size": 100, "entry": 175.50, "current": 178.25, "pnl": 275.00}, {"symbol": "MSFT", "size": 50, "entry": 330.00, "current": 335.50, "pnl": 275.00}, {"symbol": "NVDA", "size": 25, "entry": 450.00, "current": 465.00, "pnl": 375.00}, {"symbol": "TSLA", "size": 40, "entry": 200.00, "current": 195.00, "pnl": -200.00}, {"symbol": "AMZN", "size": 30, "entry": 140.00, "current": 145.00, "pnl": 150.00}]})

@app.route("/api/portfolio")
def get_portfolio():
    return jsonify({"total_value": 100000.00, "cash": 25000.00, "positions_value": 75000.00, "day_pnl": 1250.00, "day_pnl_pct": 1.25, "total_pnl": 17500.00, "total_pnl_pct": 17.5})

@app.route("/api/strategies")
def get_strategies():
    return jsonify({"strategies": [{"name": "Momentum", "enabled": True, "trades": 45, "win_rate": 62.5, "profit": 5230.50}, {"name": "Mean Reversion", "enabled": True, "trades": 38, "win_rate": 58.0, "profit": 3150.25}, {"name": "Breakout", "enabled": True, "trades": 32, "win_rate": 65.5, "profit": 4125.75}, {"name": "ML Ensemble", "enabled": True, "trades": 28, "win_rate": 71.4, "profit": 2493.50}]})

@app.route("/api/history")
def get_history():
    return jsonify({"history": [{"date": "2026-03-24", "value": 98750.00, "pnl": 450.00}, {"date": "2026-03-23", "value": 98300.00, "pnl": -200.00}, {"date": "2026-03-22", "value": 98500.00, "pnl": 800.00}, {"date": "2026-03-21", "value": 97700.00, "pnl": 300.00}, {"date": "2026-03-20", "value": 97400.00, "pnl": 150.00}]})

@app.route("/api/system")
def get_system():
    return jsonify({"cpu": 15.2, "memory": 45.8, "disk": 32.1, "uptime": "3 days, 4 hours", "version": "v2.6.1 Sentinel"})

def run_dashboard(port=8081):
    print(f"[DASHBOARD] Starting OmniBot v2.6.1 Sentinel on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

if __name__ == "__main__":
    run_dashboard()
