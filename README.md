# MCP Research Server

A FastMCP server for searching and extracting research papers from arXiv.

## Local Development

This project uses `uv` for dependency management:

```bash
uv run research_server.py
```

## Deployment on Render.io

Render.io doesn't support `uv` natively, so this project includes:
- `requirements.txt`: Generated from pyproject.toml using `uv pip compile`
- `render.yaml`: Render deployment configuration
- `runtime.txt`: Specifies Python version for Render

To deploy:
1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. The service will automatically:
   - Use Python 3.11.11
   - Install dependencies from requirements.txt
   - Start the server on port provided by Render

When you update pyproject.toml dependencies, remember to regenerate requirements.txt:
```bash
uv pip compile pyproject.toml --no-emit-find-links > requirements.txt
```