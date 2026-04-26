# collector/collect_yt.py
# ========================
# Downloads comments from a YouTube video using the YouTube Data API.
# Output: a JSONL file saved to data/raw/ with one comment per line.
#
# Each line looks like:
#   {"id": "abc123", "text": "comment text", "author": "username", "date": "2024-01-01"}
#
# HOW TO USE:
#   1. Get a YouTube Data API key from https://console.cloud.google.com
#   2. Add it to your .env file: YOUTUBE_API_KEY=your-key
#   3. Run: python collector/collect_yt.py --video-id VIDEO_ID --out data/raw/comments.jsonl
#
