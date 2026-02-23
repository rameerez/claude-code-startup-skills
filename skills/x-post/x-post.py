#!/usr/bin/env python3
"""
CLI tool for posting to X (Twitter) using the xdk Python SDK.
Supports text posts, image posts, and video posts.

Usage:
    python x-post.py post "Hello world"
    python x-post.py post "Check this out" --media /path/to/image.jpg
    python x-post.py post "Watch this" --media /path/to/video.mp4
    python x-post.py me
"""

import argparse
import json
import os
import sys
import time
import mimetypes
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(SCRIPT_DIR, "x.key")

MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
MEDIA_UPLOAD_V2_URL = "https://api.x.com/2/media/upload"

def load_credentials():
    if not os.path.exists(KEY_FILE):
        print(f"Error: credentials file not found at {KEY_FILE}", file=sys.stderr)
        print("Create x.key with:", file=sys.stderr)
        print(json.dumps({
            "api_key": "YOUR_API_KEY",
            "api_secret": "YOUR_API_SECRET",
            "access_token": "YOUR_ACCESS_TOKEN",
            "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    with open(KEY_FILE) as f:
        return json.load(f)


def get_client(creds):
    from xdk import Client
    return Client(
        api_key=creds["api_key"],
        api_secret=creds["api_secret"],
        access_token=creds["access_token"],
        access_token_secret=creds["access_token_secret"]
    )


def get_oauth1_session(creds):
    """Create a requests session with OAuth 1.0a for media upload."""
    from requests_oauthlib import OAuth1
    auth = OAuth1(
        creds["api_key"],
        creds["api_secret"],
        creds["access_token"],
        creds["access_token_secret"]
    )
    session = requests.Session()
    session.auth = auth
    return session


def detect_media_type(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith("video"):
        return "video", mime
    elif mime and mime.startswith("image"):
        if mime == "image/gif":
            return "gif", mime
        return "image", mime
    else:
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".mp4", ".mov", ".avi", ".webm"):
            return "video", f"video/{ext[1:]}"
        return "image", mime or "image/jpeg"


def upload_image(session, filepath):
    """Upload an image using v1.1 media upload (simple)."""
    media_type = mimetypes.guess_type(filepath)[0] or "image/jpeg"
    with open(filepath, "rb") as f:
        files = {"media_data": None, "media": f}
        resp = session.post(MEDIA_UPLOAD_URL, files={"media": (os.path.basename(filepath), f, media_type)})
    if resp.status_code not in (200, 201, 202):
        print(f"Image upload failed: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    media_id = resp.json()["media_id_string"]
    print(f"Image uploaded: media_id={media_id}")
    return media_id


def upload_video(session, filepath):
    """Upload a video using chunked media upload (INIT/APPEND/FINALIZE)."""
    file_size = os.path.getsize(filepath)
    media_type = mimetypes.guess_type(filepath)[0] or "video/mp4"

    # INIT
    resp = session.post(MEDIA_UPLOAD_URL, data={
        "command": "INIT",
        "media_type": media_type,
        "total_bytes": file_size,
        "media_category": "tweet_video"
    })
    if resp.status_code not in (200, 201, 202):
        print(f"Video INIT failed: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    media_id = resp.json()["media_id_string"]
    print(f"Video INIT: media_id={media_id}, size={file_size / 1024 / 1024:.1f}MB")

    # APPEND (4MB chunks)
    segment = 0
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(4 * 1024 * 1024)
            if not chunk:
                break
            resp = session.post(MEDIA_UPLOAD_URL,
                data={"command": "APPEND", "media_id": media_id, "segment_index": segment},
                files={"media": ("chunk", chunk, "application/octet-stream")}
            )
            if resp.status_code not in (200, 201, 202, 204):
                print(f"Video APPEND failed at segment {segment}: {resp.status_code} {resp.text}", file=sys.stderr)
                sys.exit(1)
            segment += 1
            uploaded = min(f.tell(), file_size)
            print(f"  Uploaded {uploaded / 1024 / 1024:.1f}MB / {file_size / 1024 / 1024:.1f}MB")
    print(f"Video APPEND complete: {segment} segments")

    # FINALIZE
    resp = session.post(MEDIA_UPLOAD_URL, data={
        "command": "FINALIZE",
        "media_id": media_id
    })
    if resp.status_code not in (200, 201, 202):
        print(f"Video FINALIZE failed: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    processing_info = result.get("processing_info")

    # Wait for processing
    while processing_info and processing_info.get("state") not in ("succeeded", None):
        state = processing_info["state"]
        if state == "failed":
            print(f"Video processing failed: {processing_info}", file=sys.stderr)
            sys.exit(1)
        wait = processing_info.get("check_after_secs", 5)
        print(f"  Processing... ({state}, checking in {wait}s)")
        time.sleep(wait)
        resp = session.get(MEDIA_UPLOAD_URL, params={"command": "STATUS", "media_id": media_id})
        processing_info = resp.json().get("processing_info")

    print(f"Video ready: media_id={media_id}")
    return media_id


def cmd_post(args):
    creds = load_credentials()
    client = get_client(creds)

    body = {"text": args.text}

    if args.media:
        session = get_oauth1_session(creds)
        kind, mime = detect_media_type(args.media)

        if not os.path.exists(args.media):
            print(f"Error: file not found: {args.media}", file=sys.stderr)
            sys.exit(1)

        if kind == "video":
            media_id = upload_video(session, args.media)
        else:
            media_id = upload_image(session, args.media)

        body["media"] = {"media_ids": [media_id]}

    # Post
    response = client.posts.create(body=body)

    if hasattr(response, 'data') and response.data:
        data = response.data
        post_id = data.get("id", "unknown")
        print(f"\nPosted successfully!")
        print(f"  https://x.com/i/status/{post_id}")
        print(f"  Text: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
        if args.media:
            print(f"  Media: {os.path.basename(args.media)} ({kind})")
    else:
        print(f"Response: {response}")


def cmd_me(args):
    creds = load_credentials()
    client = get_client(creds)
    response = client.users.find_my_user(user_fields=["public_metrics", "description"])
    if hasattr(response, 'data') and response.data:
        d = response.data
        print(f"@{d.get('username', '?')} — {d.get('name', '?')}")
        metrics = d.get("public_metrics", {})
        print(f"  Followers: {metrics.get('followers_count', '?')}")
        print(f"  Following: {metrics.get('following_count', '?')}")
        print(f"  Posts: {metrics.get('tweet_count', '?')}")
    else:
        print(f"Response: {response}")


def main():
    parser = argparse.ArgumentParser(description="Post to X from the command line")
    subparsers = parser.add_subparsers(dest="command")

    post_parser = subparsers.add_parser("post", help="Post a tweet")
    post_parser.add_argument("text", help="Tweet text")
    post_parser.add_argument("--media", help="Path to image or video file")
    post_parser.set_defaults(func=cmd_post)

    me_parser = subparsers.add_parser("me", help="Show your profile info")
    me_parser.set_defaults(func=cmd_me)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
