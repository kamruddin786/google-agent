# Google ADK Simple Agent

This project provides a simple agent implementation using Python and Pydantic, designed to work with the Google ADK framework.

## Project Structure

```
reuirements.txt
simple-agent/
    __init__.py
    agent.py
    __pycache__/
```

## Features
- Simple agent logic in `simple-agent/agent.py`
- Pydantic-based model validation
- Easy integration with Google ADK

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd google-adk
   ```
3. (Recommended) Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
5. Install dependencies:
   ```bash
   pip install -r reuirements.txt
   ```

6. Add a `.env` file in the project root to store environment variables:
   - Create a file named `.env` in the root directory.
   - Add your Tavily API key:
     ```env
     TAVILY_API_KEY=your_tavily_api_key_here
     ```
   - Replace `your_tavily_api_key_here` with your actual Tavily API key.

## Usage
- Run the agent or web interface using:
  ```bash
  adk web
  ```

## Requirements
- Python 3.12 or higher
- Pydantic
- Google ADK

## Author
Kamruddin

---
For more details, see the code in `simple-agent/agent.py`.
