#!/usr/bin/env python3
"""
OMNIBOT v2.5.1 - Automated Weekend Update Module
Checks for updates when market is closed and auto-updates
"""
import os
import sys
import subprocess
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, '/home/biqu/omnibot/src')

# Setup logging
log_dir = Path('/home/biqu/omnibot/logs')
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutoUpdate')


class AutoUpdater:
    """Automated update system for OmniBot"""

    def __init__(self):
        self.repo_path = '/home/biqu/omnibot'
        self.backup_dir = Path(self.repo_path) / 'backups'
        self.env_file = Path(self.repo_path) / '.env'
        self.last_check_file = Path(self.repo_path) / '.last_update_check'

    def is_market_closed(self) -> bool:
        """Check if US stock market is closed"""
        now = datetime.now()

        # Weekend check (Saturday=5, Sunday=6 in Python's weekday())
        if now.weekday() >= 5:  # Saturday or Sunday
            return True

        # US Market hours: 9:30 AM - 4:00 PM ET
        # Simplified check - market closed outside these hours
        hour = now.hour
        minute = now.minute
        current_time = hour + minute / 60

        # Rough ET conversion (adjust for your timezone)
        # This is simplified - assumes Pi is on local time
        market_open = 9.5   # 9:30 AM
        market_close = 16.0  # 4:00 PM

        if current_time < market_open or current_time > market_close:
            return True

        return False

    def should_check_update(self) -> bool:
        """Check if enough time has passed since last check"""
        if not self.last_check_file.exists():
            return True

        last_check = datetime.fromtimestamp(self.last_check_file.stat().st_mtime)
        now = datetime.now()

        # Check every 30 minutes on weekends, every 4 hours on weekdays
        if self.is_market_closed():
            interval = timedelta(minutes=30)
        else:
            interval = timedelta(hours=4)

        return (now - last_check) > interval

    def backup_env(self):
        """Backup .env file with API keys"""
        if self.env_file.exists():
            backup_path = self.backup_dir / f'.env.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            self.backup_dir.mkdir(exist_ok=True)

            # Copy file
            with open(self.env_file, 'r') as f:
                content = f.read()
            with open(backup_path, 'w') as f:
                f.write(content)

            logger.info(f"Backed up .env to {backup_path}")
            return backup_path
        return None

    def check_for_updates(self) -> bool:
        """Check if updates are available on GitHub"""
        try:
            os.chdir(self.repo_path)

            # Fetch latest from origin
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.warning(f"Git fetch failed: {result.stderr}")
                return False

            # Check if local is behind origin
            result = subprocess.run(
                ['git', 'rev-list', 'HEAD..origin/main', '--count'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                commits_behind = int(result.stdout.strip())
                if commits_behind > 0:
                    logger.info(f"Updates available: {commits_behind} commits behind")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False

    def perform_update(self) -> bool:
        """Perform the actual update"""
        try:
            logger.info("Starting automated update...")

            # 1. Backup .env
            env_backup = self.backup_env()

            # 2. Pull latest code
            os.chdir(self.repo_path)
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Git pull failed: {result.stderr}")
                return False

            logger.info(f"Git pull successful: {result.stdout}")

            # 3. Restore .env if it was overwritten
            if env_backup and self.env_file.exists():
                # Check if .env was modified (git might have overwritten it)
                with open(self.env_file, 'r') as f:
                    current_content = f.read()

                # If keys are missing, restore from backup
                if 'ALPACA_API_KEY_ENC' not in current_content or "=''" in current_content:
                    logger.info("Restoring .env from backup")
                    with open(env_backup, 'r') as f:
                        backup_content = f.read()
                    with open(self.env_file, 'w') as f:
                        f.write(backup_content)

            # 4. Update Python dependencies
            venv_python = Path(self.repo_path) / 'venv' / 'bin' / 'python'
            pip_path = Path(self.repo_path) / 'venv' / 'bin' / 'pip'

            if pip_path.exists():
                result = subprocess.run(
                    [str(pip_path), 'install', '-r', 'requirements.txt', '-q'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info("Dependencies updated")
                else:
                    logger.warning(f"Dependency update warning: {result.stderr}")

            # 5. Restart service
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'omnibot-v2.5.service'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Service restarted successfully")
            else:
                logger.error(f"Service restart failed: {result.stderr}")
                return False

            logger.info("✓ Update completed successfully")
            return True

        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

    def run(self):
        """Main update check loop - called by trading engine"""
        try:
            # Update last check time
            self.last_check_file.touch()

            # Only update when market is closed
            if not self.is_market_closed():
                return  # Skip - market is open, don't update

            logger.info("Market closed - checking for updates...")

            # Check if updates available
            if self.check_for_updates():
                logger.info("Updates found - performing auto-update...")
                self.perform_update()
            else:
                logger.debug("No updates available")

        except Exception as e:
            logger.error(f"Auto-update error: {e}")


def run_auto_update():
    """Entry point for auto-update"""
    updater = AutoUpdater()
    updater.run()


if __name__ == "__main__":
    run_auto_update()
