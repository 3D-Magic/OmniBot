"""
OmniBot v2.6.1 Sentinel - Auto Updater
Handles weekend auto-updates - Your requirement
"""

import os
import time
import threading
import subprocess
from datetime import datetime

class AutoUpdater:
    def __init__(self, settings):
        self.settings = settings
        self.update_available = False
        self.running = False

    def start(self):
        if not self.settings.AUTO_UPDATE_ENABLED:
            return
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("[UPDATER] Auto-update monitor started")

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            time.sleep(self.settings.UPDATE_CHECK_INTERVAL_HOURS * 3600)
            if self._is_weekend() and self.settings.UPDATE_ON_WEEKEND:
                print("[UPDATER] Weekend detected - checking for updates")
                self.check_and_update()

    def _is_weekend(self):
        return datetime.now().weekday() >= 5

    def check_and_update(self):
        try:
            import urllib.request
            import json
            import ssl

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            api_url = f"https://api.github.com/repos/{self.settings.GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(api_url, headers={"User-Agent": "OmniBot-Updater"})

            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                data = json.loads(response.read().decode())
                latest = data.get("tag_name", "v2.6.1")
                current = "v2.6.1"

                if self._version_compare(latest, current) > 0:
                    print(f"[UPDATER] Update available: {latest}")
                    self.apply_update()

        except Exception as e:
            print(f"[UPDATER] Check failed: {e}")

    def _version_compare(self, v1, v2):
        def normalize(v):
            return [int(x) for x in v.replace("v", "").split(".")]
        try:
            n1, n2 = normalize(v1), normalize(v2)
            for i in range(max(len(n1), len(n2))):
                x1 = n1[i] if i < len(n1) else 0
                x2 = n2[i] if i < len(n2) else 0
                if x1 > x2: return 1
                elif x1 < x2: return -1
            return 0
        except:
            return 0

    def apply_update(self):
        print("[UPDATER] Applying update...")
        script = """#!/bin/bash
cd ~/OmniBot-v2.6.1
echo "[UPDATE] Downloading..."
wget -q https://github.com/3D-Magic/OmniBot-Testing/archive/refs/heads/V2.6.1-Omnibot_Sentinal.zip -O /tmp/update.zip
unzip -q -o /tmp/update.zip -d /tmp/
cp -r /tmp/OmniBot-Testing-V2.6.1-Omnibot_Sentinal/* .
rm -rf /tmp/OmniBot-Testing-V2.6.1-Omnibot_Sentinal /tmp/update.zip
echo "[UPDATE] Restarting..."
./scripts/omnibot.sh restart --ngrok
"""
        with open("/tmp/omnibot_update.sh", "w") as f:
            f.write(script)
        os.chmod("/tmp/omnibot_update.sh", 0o755)
        subprocess.Popen(["bash", "/tmp/omnibot_update.sh"])

    def force_update(self):
        self.apply_update()
