# Brainrot

Brainrot is an automated YouTube Shorts factory built for creators who want to publish high-volume, AI-narrated short-form content with minimal manual effort. It takes a batch of written scripts, converts each one into spoken audio using a local text-to-speech model, overlays that audio onto a random clip from a master vertical video, burns in synchronized captions, and queues the finished videos for upload — all without human intervention between steps. Once your scripts are loaded, the pipeline runs end-to-end and posts directly to your YouTube channel.

## Tools

- **Kokoro**: Local neural text-to-speech model that generates the voice narration entirely on-device.
- **FFmpeg**: Handles all video encoding, audio muxing, and hardware-accelerated export under the hood.
- **MoviePy**: Orchestrates clip trimming, subtitle compositing, and final video assembly.
- **Gemini**: Generates YouTube titles, descriptions, and tags from each script before upload.
- **YouTube Data API**: Authenticates and publishes finished videos directly to your channel.

## Features

- **Batch script processing**: Reads a queue of text scripts and works through them one by one, so you can load dozens of pieces of content at once and walk away.

- **AI voice narration**: Converts each script into natural-sounding speech using a local neural text-to-speech model, keeping audio generation fast and offline.

- **Random clip selection**: Picks a random segment from a long master video for each short, ensuring no two uploads look identical even when using the same source footage.

- **Burned-in subtitles**: Generates timed captions from the script and composites them directly onto the video frame, styled for short-form readability.

- **AI-generated titles and descriptions**: Sends each script to a generative AI model to produce a YouTube-optimized title, description, and tag set before upload.

- **Automated YouTube upload**: Authenticates with the YouTube API and uploads every finished video in the queue as a public Short, then deletes the local file and logs the upload.

## Script Pipeline

- Each paragraph in your script file becomes one independent video.
- The queue drains automatically; add new scripts anytime and they'll be picked up on the next run.
- Scripts are archived locally so metadata can be generated accurately at upload time.

## Audio Generation

- Speech is synthesized on-device — no API costs or rate limits.
- Audio length determines the video duration automatically.

## Video Composition

- A random segment of the master footage is chosen each time so no two Shorts look the same.
- Captions are split into short word groups and timed evenly across the audio.

## YouTube Publishing

- Authenticates once via OAuth and reuses the session for all queued videos.
- Titles and descriptions are enriched with hashtags before submission.
- Uploaded videos are deleted locally and logged automatically.
