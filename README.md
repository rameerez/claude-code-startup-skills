# 🚀 Startup skills for Claude Code

A collection of [Claude Code](https://claude.ai/code) skills for building and running software startups, SaaS, apps, and businesses.

These are reusable commands that automate common business-oriented tasks in startup development workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [`compress-images`](skills/compress-images/) | Compress images to WebP for SEO-optimized page performance |
| [`customer-empathy`](skills/customer-empathy/) | Deep-dive into customer empathy and user journey thinking |
| [`download-video`](skills/download-video/) | Download videos from social media URLs (X, YouTube, TikTok, etc.) using yt-dlp |
| [`transcribe-video`](skills/transcribe-video/) | Generate subtitles (SRT/VTT) and transcripts from video/audio files using AWS Transcribe |

## Installation

Copy any skill folder into your project's `.claude/skills/` directory:

```bash
# Copy a single skill
cp -r skills/compress-images /path/to/your/project/.claude/skills/

# Or symlink it
ln -s /path/to/claude-code-startup-skills/skills/compress-images /path/to/your/project/.claude/skills/
```

Make sure your `.gitignore` tracks skills:

```gitignore
.claude/*
!.claude/skills/
```

Then use it in Claude Code:

```
/compress-images ./path/to/images/
```

## Contributing

Feel free to open issues or PRs with new skills. Each skill should:

1. Live in its own folder under `skills/`
2. Have a `SKILL.md` file with proper frontmatter (`name`, `description`, `argument-hint`)
3. Include clear step-by-step instructions for the agent
4. Document real-world results when possible

## License

MIT
