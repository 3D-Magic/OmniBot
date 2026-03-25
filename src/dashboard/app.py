"""
OMNIBOT Dashboard - Flask Application
Fixed for ngrok/external access
"""

import os
import sys
import logging
from pathlib import Path
from functools import wraps
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import DASHBOARD, EXTERNAL_ACCESS, VERSION, VERSION_NAME

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'omnibot-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False

# Initialize SocketIO with allow_unsafe_werkzeug for ngrok
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Global state
bot_status = {
    'running': False,
    'mode': 'idle',
    'portfolio_value': 0.0,
    'positions': [],
    'last_update': None,
    'ngrok_url': None,
    'version': VERSION,
    'version_name': VERSION_NAME
}

# Auth decorator with fix for missing auth_required key
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Fixed: Use .get() with default value
        if DASHBOARD.get('auth_required', True):
            if 'logged_in' not in session:
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    return render_template('index.html', 
                         version=VERSION, 
                         version_name=VERSION_NAME,
                         ngrok_url=bot_status.get('ngrok_url'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == DASHBOARD.get('password', 'admin'):
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/api/status')
@login_required
def api_status():
    return jsonify(bot_status)


@app.route('/api/start', methods=['POST'])
@login_required
def api_start():
    bot_status['running'] = True
    bot_status['mode'] = 'trading'
    bot_status['last_update'] = datetime.now().isoformat()
    socketio.emit('status_update', bot_status)
    return jsonify({'success': True, 'status': bot_status})


@app.route('/api/stop', methods=['POST'])
@login_required
def api_stop():
    bot_status['running'] = False
    bot_status['mode'] = 'idle'
    bot_status['last_update'] = datetime.now().isoformat()
    socketio.emit('status_update', bot_status)
    return jsonify({'success': True, 'status': bot_status})


@app.route('/api/ngrok/start', methods=['POST'])
@login_required
def api_ngrok_start():
    try:
        from pyngrok import ngrok
        port = DASHBOARD.get('port', 8081)
        public_url = ngrok.connect(port, "http")
        bot_status['ngrok_url'] = public_url
        EXTERNAL_ACCESS['enabled'] = True
        socketio.emit('ngrok_update', {'url': public_url, 'status': 'connected'})
        return jsonify({'success': True, 'url': public_url})
    except Exception as e:
        logger.error(f"Ngrok start error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ngrok/stop', methods=['POST'])
@login_required
def api_ngrok_stop():
    try:
        from pyngrok import ngrok
        ngrok.kill()
        bot_status['ngrok_url'] = None
        EXTERNAL_ACCESS['enabled'] = False
        socketio.emit('ngrok_update', {'url': None, 'status': 'disconnected'})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ngrok stop error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@socketio.on('connect')
def handle_connect():
    emit('status_update', bot_status)


@socketio.on('disconnect')
def handle_disconnect():
    pass


def run_dashboard(enable_ngrok=False):
    """Run the dashboard server"""
    port = DASHBOARD.get('port', 8081)
    host = DASHBOARD.get('host', '0.0.0.0')
    debug = DASHBOARD.get('debug', False)

    # Start ngrok if requested
    if enable_ngrok:
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(port, "http")
            bot_status['ngrok_url'] = public_url
            logger.info(f"Ngrok tunnel: {public_url}")
            print(f"🌐 External URL: {public_url}")
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            print(f"⚠️  Ngrok failed: {e}")

    print(f"🚀 Dashboard running on http://{host}:{port}")

    # Fixed: Added allow_unsafe_werkzeug for external access
    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=debug,
        allow_unsafe_werkzeug=True  # Required for ngrok/external access
    )


if __name__ == '__main__':
    run_dashboard()
