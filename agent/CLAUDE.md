# GPT20 Agent - Claude Documentation

## Project Overview

This is an AI agent built with the Strands framework that autonomously maintains a curated list of 20 stocks (GPT20 index). The agent analyzes market conditions, evaluates stock performance, and updates the index with reasoning for each selection.

## Architecture

### Core Components

- **Agent Framework**: Built on Strands AI framework with OpenAI GPT-4o
- **Custom Tools**: File operations for reading/writing the GPT20 index
- **Template System**: Markdown-based prompts and system instructions
- **Automated Execution**: Can run via cron for regular updates

### File Structure

```
agent/
├── src/
│   ├── main.py              # Entry point and agent orchestration
│   ├── config.py            # Configuration (API keys, model settings)
│   └── tools/               # Custom tools module
│       ├── __init__.py      # Tool exports (read_index, write_index, get_index_info)
│       └── templates.py     # Template loading and file operations
├── md/
│   ├── prompts/             # Agent prompts and system instructions
│   │   ├── SYSTEM.md        # System prompt defining agent behavior
│   │   └── UPDATE_PROMPT.md # Instructions for updating the index
│   └── indices/             # Output directory
│       └── GPT20.md         # The maintained stock index
└── README.md                # Setup and usage instructions
```

## Key Features

### Autonomous Operation
- Agent reads current index state using custom tools
- Analyzes market conditions and stock fundamentals
- Makes informed decisions about stock additions/removals
- Writes updated index with timestamps and reasoning

### Custom Tools Integration
- `@tool` decorated functions integrate with Strands framework
- `read_index()` - Reads current index file
- `write_index()` - Saves updated index content
- `get_index_info()` - Provides file metadata
- `current_time()` - Gets current timestamp for updates

### Template-Driven Prompts
- Modular prompt system using markdown templates
- Easy to modify agent behavior without code changes
- Separates business logic from prompt engineering

## Technical Implementation

### Agent Tools Pattern
The project demonstrates how to create custom tools for the Strands framework:

```python
@tool
def read_index(index_name: str) -> dict:
    """Read an index file for updating."""
    # Implementation handles file I/O
    return {"content": content, "exists": exists, "message": msg}
```

### Prompt Engineering
Uses structured prompts that:
- Define clear objectives and constraints
- Specify output format requirements
- Provide context about available tools
- Guide the agent through multi-step processes

### Configuration Management
Centralized config with environment variable support:
- OpenAI API key management
- Model selection (GPT-4o)
- Index file naming conventions

## Development Notes

### Design Decisions
1. **Tool-based architecture**: Agent uses tools for all file operations rather than direct file access
2. **Template separation**: Prompts are external markdown files, not hardcoded strings
3. **Modular tools**: Tools are organized as a proper Python module for scalability
4. **Minimal dependencies**: Uses Strands framework and standard library where possible

### Future Extensions
- Add market data fetching tools (APIs for stock prices, news)
- Implement backtesting tools for strategy validation
- Create risk analysis tools for portfolio evaluation
- Add notification tools for significant changes

### Lessons Learned
- Custom tools must use `@tool` decorator to integrate with Strands
- File operations benefit from being wrapped as agent tools
- Template-based prompts are more maintainable than inline strings
- Proper module organization makes tools reusable and testable

## Usage Patterns

### Manual Execution
```bash
export OPENAI_API_KEY="your-key"
python3 -m src.main
```

### Automated Scheduling
```bash
# Cron job for weekday market close updates
30 16 * * 1-5 cd /path/to/agent && python3 -m src.main
```

### Development Workflow
1. Modify prompts in `md/prompts/` for behavior changes
2. Add new tools in `src/tools/__init__.py`
3. Update configuration in `src/config.py`
4. Test with manual execution before scheduling

## Performance Characteristics

- **Execution Time**: ~30-60 seconds per update
- **API Costs**: ~$0.10-0.50 per run (depending on analysis depth)
- **File Size**: GPT20.md typically 2-5KB
- **Dependencies**: Minimal - Strands framework + OpenAI client

This architecture provides a solid foundation for AI agents that need to maintain structured data files with autonomous decision-making capabilities.
