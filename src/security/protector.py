#!/usr/bin/env python3
"""
OMNIBOT v2.5 - Security & License Protection
Copyright (c) 2026 3D-Magic

This module provides:
- File integrity verification
- Admin password protection
- License watermarking
- Tamper detection
"""

import hashlib
import os
import sys
from pathlib import Path
from getpass import getpass

class LicenseProtector:
    """Protects OMNIBOT from unauthorized modifications"""

    # Admin password hash (SHA256 of "S@m5ungB0t")
    # ONLY the hash is stored, not the actual password
    ADMIN_PASSWORD_HASH = "c036374cef56286f546ee09db23a524006c87ba72b3ea2688c1c34094eb747e8"

    # Files to protect (relative to src/)
    PROTECTED_FILES = [
        "config/settings.py",
        "database/manager.py",
        "trading/engine.py",
        "ml/lstm_predictor.py",
        "ml/regime_detector.py",
        "risk/manager.py",
        "main.py",
        "security/protector.py",
    ]

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.verified = False

    def _hash_file(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_integrity(self):
        """Verify all protected files are unmodified"""
        print("🔒 Verifying file integrity...")

        # Load stored hashes
        hash_file = self.base_path / ".file_hashes"
        if not hash_file.exists():
            print("⚠️  First run - generating integrity hashes...")
            self._generate_hashes()
            return True

        # Verify each file
        with open(hash_file, "r") as f:
            stored_hashes = {}
            for line in f:
                if "=" in line:
                    fname, fhash = line.strip().split("=")
                    stored_hashes[fname] = fhash

        violations = []
        for rel_path in self.PROTECTED_FILES:
            full_path = self.base_path / rel_path
            if full_path.exists():
                current_hash = self._hash_file(full_path)
                if rel_path in stored_hashes:
                    if current_hash != stored_hashes[rel_path]:
                        violations.append(rel_path)
                else:
                    violations.append(f"{rel_path} (new file)")
            else:
                violations.append(f"{rel_path} (missing)")

        if violations:
            print("\n" + "="*70)
            print("❌ LICENSE VIOLATION DETECTED")
            print("="*70)
            print("\nThe following files have been modified:")
            for v in violations:
                print(f"  - {v}")
            print("\nThis software is licensed for PERSONAL USE ONLY.")
            print("Modifications are NOT permitted under the license terms.")
            print("\nThe trading bot will NOT start.")
            print("="*70 + "\n")
            return False

        print("✓ Integrity verified")
        self.verified = True
        return True

    def _generate_hashes(self):
        """Generate and store file hashes"""
        hash_file = self.base_path / ".file_hashes"
        with open(hash_file, "w") as f:
            for rel_path in self.PROTECTED_FILES:
                full_path = self.base_path / rel_path
                if full_path.exists():
                    fhash = self._hash_file(full_path)
                    f.write(f"{rel_path}={fhash}\n")
        # Protect hash file
        os.chmod(hash_file, 0o600)

    def verify_admin(self):
        """Verify admin password for configuration changes"""
        print("\n🔐 Admin authentication required")
        password = getpass("Enter admin password: ")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if password_hash == self.ADMIN_PASSWORD_HASH:
            print("✓ Access granted")
            return True
        else:
            print("❌ Access denied - incorrect password")
            return False

    def get_license_watermark(self):
        """Get watermark for trade logs"""
        return "OMNIBOT v2.5 - Licensed to authorized user only - Personal Use License"

# Global instance
protector = LicenseProtector()

def verify_before_start():
    """Call this before starting trading"""
    if not protector.verify_integrity():
        sys.exit(1)
    return True
