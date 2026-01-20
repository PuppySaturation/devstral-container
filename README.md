# Devstral Container

A container workflow for Mistral's Devstral Vibe CLI pre-installed and ready to use. Complete isolation from your host system while maintaining persistent credentials and workspace access. Optional API logging for cost monitoring and usage analysis.

## Docker Hub

Pre-built images available on Docker Hub:
- [nezhar/devstral-cli](https://hub.docker.com/r/nezhar/devstral-cli) - Main CLI container
- [nezhar/devstral-proxy](https://hub.docker.com/r/nezhar/devstral-proxy) - Optional logging proxy
- [nezhar/devstral-datasette](https://hub.docker.com/r/nezhar/devstral-datasette) - Optional visualization

## Quick Start

### Using the Helper Script (Recommended)

Download and run:

```bash
# Download and install
curl -o ~/.local/bin/devstral-container https://raw.githubusercontent.com/nezhar/devstral-container/main/bin/devstral-container
chmod +x ~/.local/bin/devstral-container

# Run it
devstral-container
```

Make sure `~/.local/bin` is in your PATH, or install system-wide with `sudo`:

```bash
sudo curl -o /usr/local/bin/devstral-container https://raw.githubusercontent.com/nezhar/devstral-container/main/bin/devstral-container
sudo chmod +x /usr/local/bin/devstral-container
```

On first run, you'll be prompted for your Mistral API key from https://console.mistral.ai/. Credentials are stored in `~/.config/devstral-container` and persist across sessions.

### Using Docker Directly

```bash
docker run --rm -it \
  -v "$(pwd):/workspace" \
  -v "$HOME/.config/devstral-container/config:/config" \
  -e "HOME=/config" \
  nezhar/devstral-cli:latest
```

## Features

This containerized setup provides:

- **Isolated Environment** - No dependency conflicts or system clutter
- **Persistent Configuration** - API keys and settings stored in `~/.config/devstral-container`
- **Optional API Logging** - Track requests, responses, token counts, and costs
- **Data Visualization** - Explore logs with Datasette's web interface
- **Easy Updates** - Pull latest images from Docker Hub

## Usage Modes

### Basic Mode (No Logging)

Just run the CLI without any logging:

```bash
devstral-container
```

### With API Logging

Enable the proxy to log all API interactions:

```bash
devstral-container --proxy
```

Logs are saved to `~/.config/devstral-container/proxy/logs.db` as SQLite database.

### With Visualization

Add Datasette to explore your logs at http://localhost:8001:

```bash
devstral-container --datasette
```

### Helper Script Options

```bash
devstral-container --help        # Show all options
devstral-container --version     # Show version info
devstral-container --proxy       # Enable API logging
devstral-container --datasette   # Enable logging + visualization
```

## How It Works

The system consists of three Docker images that work together:

1. **devstral-cli** - Runs Vibe CLI with your workspace mounted and config persisted
2. **devstral-proxy** (optional) - Intercepts Mistral API calls and logs them to SQLite
3. **devstral-datasette** (optional) - Web UI for exploring logged data

The proxy only intercepts Mistral API traffic by overriding the provider configuration, not all HTTPS traffic. This prevents network errors while giving full API visibility.

## Configuration

### Directory Structure

```
~/.config/devstral-container/
├── config/                    # Vibe CLI configuration
│   ├── config.toml            # API keys and preferences
│   └── proxy-provider.toml    # Auto-generated for proxy mode
└── proxy/                     # Proxy data (when enabled)
    └── logs.db                # SQLite database with API logs
```

### Custom Providers

You can configure custom providers by adding files to `~/.config/devstral-container/config/`. For example, to use a local Ollama instance:

## Updating

To get the latest version:

```bash
# Update helper script
curl -o ~/.local/bin/devstral-container https://raw.githubusercontent.com/nezhar/devstral-container/main/bin/devstral-container
```

## Related Projects

This project follows the same pattern as:
- [claude-container](https://github.com/nezhar/claude-container) - Container workflow for Claude Code
- [gemini-container](https://github.com/nezhar/gemini-container) - Container workflow for Gemini CLI

## Contributing

Contributions welcome! Please:
- Report issues at https://github.com/nezhar/devstral-container/issues
- Submit pull requests with improvements
- Share feedback and suggestions
