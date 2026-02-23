# Startup Skills for Claude Code

A [Claude Code](https://claude.ai/code) plugin with skills for building and running software startups, SaaS, apps, and businesses.

## Skills

| Skill | Description |
|-------|-------------|
| [`compress-images`](skills/compress-images/) | Compress images to WebP for SEO-optimized page performance |
| [`customer-empathy`](skills/customer-empathy/) | Deep-dive into customer empathy and user journey thinking |
| [`download-video`](skills/download-video/) | Download videos from social media URLs (X, YouTube, TikTok, etc.) using yt-dlp |
| [`transcribe-video`](skills/transcribe-video/) | Generate subtitles (SRT/VTT) and transcripts from video/audio using AWS Transcribe |
| [`x-post`](skills/x-post/) | Post to X (Twitter) from the command line — text, images, and video |

## Installation

### Option 1: Install as a plugin

```bash
# Add this repo as a marketplace
claude plugin marketplace add rameerez/claude-code-startup-skills

# Install the plugin (available across all projects)
claude plugin install startup-skills@rameerez-claude-code-startup-skills
```

Skills are namespaced when installed as a plugin:

```
/startup-skills:compress-images ./path/to/images/
```

### Option 2: Symlink for personal use

For personal use across all projects, symlink to your personal skills directory:

```bash
# Symlink all skills globally
ln -s ~/GitHub/claude-code-startup-skills/skills ~/.claude/skills
```

This makes skills available without namespacing:

```
/compress-images ./path/to/images/
```

### Option 3: Copy to a single project

Copy individual skills into a project's `.claude/skills/` directory:

```bash
cp -r skills/compress-images /path/to/project/.claude/skills/
```

## Usage

Once installed, invoke any skill with a slash command:

```
/compress-images ./images/
/download-video https://x.com/user/status/123
/transcribe-video ./video.mp4
/x-post "Hello world!"
/customer-empathy
```

## Contributing

PRs welcome. Each skill should:

1. Live in its own folder under `skills/`
2. Have a `SKILL.md` file with frontmatter (`name`, `description`)
3. Include clear step-by-step instructions for the agent

## License

MIT
