# 🐾 Termagatchi

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![UV](https://img.shields.io/badge/built%20with-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Textual](https://img.shields.io/badge/powered%20by-textual-cyan.svg)](https://github.com/Textualize/textual)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Termagatchi** - Your AI-powered virtual terminal pet that lives in your command line! Feed it, play with it, and watch it grow through interactive conversations powered by advanced language models.

![Termagatchi Demo](https://via.placeholder.com/800x400/1a1a2e/ffd700?text=🐾+Termagatchi+-+Your+AI+Terminal+Pet)

## ✨ Features

- 🤖 **AI-Powered Conversations** - Chat with your virtual pet using Google Gemini, OpenAI, or local models
- 🎮 **Interactive Gameplay** - Feed, clean, play with, and care for your digital companion
- 📊 **Real-time Stats** - Monitor hunger, happiness, energy, hygiene, affection, and health
- 🎨 **Beautiful Terminal UI** - Modern, responsive interface built with Textual
- 💾 **Persistent Saves** - Your pet remembers your interactions across sessions
- 🔧 **Extensible Architecture** - Easy to add new AI providers and game mechanics
- 🚀 **Fast & Lightweight** - Runs entirely in your terminal with minimal dependencies

## 🚀 Quick Start

### Option 1: Run with UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/alliecatowo/termagatchi.git
cd termagatchi

# Run immediately (creates virtual environment automatically)
uv run termagatchi run
```

### Option 2: Install System-wide

```bash
# Clone the repository
git clone https://github.com/alliecatowo/termagatchi.git
cd termagatchi

# Install dependencies
uv sync

# Install the CLI tool globally
uv tool install --editable .

# Now you can run it from anywhere!
termagatchi run
```

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **UV package manager** (recommended) or **pip**
- **Git** for cloning the repository

### Method 1: Development Installation (UV)

```bash
# Clone and setup
git clone https://github.com/alliecatowo/termagatchi.git
cd termagatchi
uv sync

# Run in development mode
uv run termagatchi run
```

### Method 2: System Installation

```bash
# Install for system-wide use
uv tool install --editable .

# Or with pip (not recommended)
pip install -e .
```

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/yourusername/termagatchi.git
cd termagatchi

### Method 3: From PyPI (Future)

```bash
pip install termagatchi
```

## 🎯 Usage

### Basic Commands

```bash
# Start the game
termagatchi run

# Get help
termagatchi --help

# View configuration options
termagatchi config --help
```

### In-Game Commands

Once the game is running, use these commands:

- **Chat**: Just type normally to talk to your pet
- **`/feed [item]`** - Feed your pet (e.g., `/feed kibble`)
- **`/clean [item]`** - Clean your pet
- **`/play [item]`** - Play with your pet
- **`/pet`** - Pet your companion
- **`/sleep [on|off]`** - Control sleep state
- **`/status`** - View detailed stats
- **`/save`** - Save your progress
- **`/quit`** - Exit the game

### Configuration

Create a `~/.termagatchi/config.toml` file:

```toml
[lm]
provider = "google"  # or "openai", "anthropic", "ollama"
model = "gemini-2.5-flash"
timeout_s = 10
max_retries = 3
temperature = 0.7
max_tokens = 100

# Optional: API keys (set via environment variables)
# GOOGLE_API_KEY = "your_key_here"
# OPENAI_API_KEY = "your_key_here"
```

Or set environment variables:
```bash
export GOOGLE_API_KEY="your_api_key_here"
export LLM_PROVIDER="google"
export LLM_MODEL="gemini-2.5-flash"
```

## 🔧 Configuration

### AI Providers

Termagatchi supports multiple AI providers:

| Provider | Models | Setup |
|----------|--------|-------|
| **Google Gemini** | `gemini-2.5-flash`, `gemini-pro` | `GOOGLE_API_KEY` |
| **OpenAI** | `gpt-4`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3-opus`, `claude-3-sonnet` | `ANTHROPIC_API_KEY` |
| **Ollama** | Local models | `OLLAMA_API_BASE=http://localhost:11434/v1` |

### Game Settings

Customize gameplay in `~/.termagatchi/config.toml`:

```toml
[game]
# Stat decay rates (per tick)
hunger_decay = 1.0
hygiene_decay = 0.5
energy_decay_awake = 0.5
energy_recovery_sleeping = 1.0

# Thresholds for mood effects
low_hunger_threshold = 40.0
critical_hunger_threshold = 20.0

# Autosave interval
autosave_interval_s = 30
tick_interval_s = 60
```

## 🎮 Gameplay

### Pet Care System

Your Termagatchi has six core stats that decay over time:

- **🍖 Hunger** - Feed regularly to keep satisfied
- **😊 Happiness** - Play and interact to maintain
- **⚡ Energy** - Sleep when tired, active when rested
- **🧼 Hygiene** - Clean to stay fresh
- **❤️ Affection** - Pet and care for bonding
- **💚 Health** - Overall well-being affected by neglect

### Activities

- **Feed**: Restore hunger with various food items
- **Clean**: Improve hygiene with different cleaning methods
- **Play**: Boost happiness with toys and games
- **Sleep**: Recover energy and process experiences
- **Pet**: Increase affection and happiness

### AI Conversations

Your pet's personality and responses are powered by advanced language models. It will:
- Remember previous interactions
- React to your care (or lack thereof)
- Express emotions based on its current state
- Engage in meaningful conversations

## 🛠️ Development

### Project Structure

```
termagatchi/
├── src/termagatchi/
│   ├── ai/           # AI client and schema definitions
│   ├── engine/       # Game logic and state management
│   ├── widgets/      # Textual UI components
│   ├── themes/       # CSS styling
│   └── app.py        # Main application
├── tests/            # Test suite
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_engine.py
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/alliecatowo/termagatchi.git
cd termagatchi

# Install development dependencies
uv sync --dev

# Make your changes
# ...

# Run tests
uv run pytest

# Submit a PR!
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Textualize** for the amazing [Textual](https://github.com/Textualize/textual) framework
- **Astral** for the fast [UV](https://github.com/astral-sh/uv) package manager
- **Google** for [Gemini](https://ai.google.dev/) AI models
- **OpenAI** for language model research and APIs

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/alliecatowo/termagatchi/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/alliecatowo/termagatchi/discussions)
- 📧 **Email**: support@termagatchi.dev

---

<div align="center">
  <p><strong>Built with ❤️ for terminal enthusiasts everywhere</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>
