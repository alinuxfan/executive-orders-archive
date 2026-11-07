#!/usr/bin/env python3
"""
Cloudflare R2 Synchronization Tool for SQLite Database
Provides single-command backup and restore of `data/orders.sqlite`
via Cloudflare R2 (S3-compatible, zero egress cost).

Usage:
  python scripts/r2_sync.py status
  python scripts/r2_sync.py upload [--force]
  python scripts/r2_sync.py download [--force]
"""

import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "orders.sqlite"

def get_r2_config():
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket_name = os.environ.get("R2_BUCKET_NAME", "executive-orders-archive")
    endpoint_url = os.environ.get("R2_ENDPOINT_URL")

    if account_id and not endpoint_url:
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    return {
        "account_id": account_id,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "is_configured": bool(access_key and secret_key and (endpoint_url or account_id))
    }

def get_s3_client(config):
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("Note: 'boto3' is not installed. To use Cloudflare R2 sync, install with:")
        print("  pip install boto3")
        return None

    return boto3.client(
        "s3",
        endpoint_url=config["endpoint_url"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
        config=Config(signature_version="s3v4")
    )

def check_status():
    config = get_r2_config()
    print("=== Cloudflare R2 Sync Status ===")
    print(f"Bucket: {config['bucket_name']}")
    print(f"Configured: {'Yes' if config['is_configured'] else 'No (set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)'}")
    
    if DB_PATH.exists():
        size_mb = DB_PATH.stat().st_size / (1024 * 1024)
        print(f"Local Database: {DB_PATH.name} ({size_mb:.2f} MB)")
    else:
        print(f"Local Database: NOT FOUND at {DB_PATH}")

    if not config["is_configured"]:
        return 0

    client = get_s3_client(config)
    if not client:
        return 0

    try:
        head = client.head_object(Bucket=config["bucket_name"], Key="orders.sqlite")
        remote_size_mb = head["ContentLength"] / (1024 * 1024)
        last_modified = head["LastModified"]
        print(f"Remote R2 Database: orders.sqlite ({remote_size_mb:.2f} MB, modified {last_modified})")
    except Exception as e:
        print(f"Remote R2 Database: Not found or unreachable ({e})")

    return 0

def upload(force=False):
    config = get_r2_config()
    if not config["is_configured"]:
        print("Notice: R2 credentials not configured. Skipping remote upload.")
        return 0

    if not DB_PATH.exists():
        print(f"Error: Local database {DB_PATH} not found.")
        return 1

    client = get_s3_client(config)
    if not client:
        return 0

    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"Uploading {DB_PATH.name} ({size_mb:.2f} MB) to R2 bucket '{config['bucket_name']}'...")
    try:
        client.upload_file(str(DB_PATH), config["bucket_name"], "orders.sqlite")
        print("Upload successful!")
        return 0
    except Exception as e:
        print(f"Upload failed: {e}")
        return 1

def download(force=False):
    config = get_r2_config()
    if not config["is_configured"]:
        print("Notice: R2 credentials not configured. Skipping remote download.")
        return 0

    client = get_s3_client(config)
    if not client:
        return 0

    if DB_PATH.exists() and not force:
        print(f"Local database exists at {DB_PATH}. Use --force to overwrite from R2.")
        return 0

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading orders.sqlite from R2 bucket '{config['bucket_name']}' to {DB_PATH}...")
    try:
        client.download_file(config["bucket_name"], "orders.sqlite", str(DB_PATH))
        print("Download successful!")
        return 0
    except Exception as e:
        print(f"Download failed: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Cloudflare R2 SQLite Sync Tool")
    parser.add_argument("action", choices=["status", "upload", "download"], help="Action to perform")
    parser.add_argument("--force", action="store_true", help="Force overwrite during download")
    args = parser.parse_args()

    if args.action == "status":
        sys.exit(check_status())
    elif args.action == "upload":
        sys.exit(upload(force=args.force))
    elif args.action == "download":
        sys.exit(download(force=args.force))

if __name__ == "__main__":
    main()
