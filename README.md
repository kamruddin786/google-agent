# Google ADK Agent with Financial Advisor

A multi-agent application built with Google ADK and LiteLLM (Ollama), featuring a general-purpose assistant and a specialized financial advisor sub-agent for Indian stock and mutual fund analysis.

## Project Structure

```
requirements.txt
simple_agent/
    __init__.py
    config.py                      # Centralized model configuration
    agent.py                       # Root agent with web search & time tools
    .env                           # Environment variables (TAVILY_API_KEY)
    financial_advisor/
        __init__.py
        advisor_agent.py           # Financial advisor sub-agent definition
        stock_tools.py             # Indian stock tools (NSE/BSE via yfinance)
        mf_tools.py                # Indian mutual fund tools (AMFI via mftool)
        analysis_tools.py          # Risk/return analysis (CAGR, Sharpe, volatility)
```

## Features

- **Root Agent** -- General-purpose assistant with web search (Tavily) and current time tools
- **Financial Advisor Sub-Agent** -- Specialized agent for Indian markets with 7 tools:
  - Stock fundamentals, historical prices, and financial statements (NSE/BSE)
  - Mutual fund search, NAV details, and historical NAV (AMFI)
  - Investment analysis: CAGR, annualized volatility, Sharpe ratio, max drawdown
  - Financial news search via Tavily (expense ratios, sector allocation, analyst opinions)
- **Multi-Agent Routing** -- Root agent automatically delegates financial queries to the financial advisor
- **Centralized Config** -- Change the LLM model for all agents from a single file (`config.py`)
- **Local LLM** -- Runs entirely on local Ollama models via LiteLLM (no cloud API costs)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/kamruddin786/google-agent.git
```

2. Navigate to the project directory:

```bash
cd google-agent
```

3. Create and activate a Python virtual environment:

```bash
python -m venv .adk
```

- On Windows:

```bash
.adk\Scripts\activate
```

- On macOS/Linux:

```bash
source .adk/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Add a `.env` file inside the `simple_agent/` directory:

```env
TAVILY_API_KEY=your_tavily_api_key_here
```

6. Make sure Ollama is running with the required model:

```bash
ollama pull llama3.1:latest
```

## Changing the LLM Model

Edit `simple_agent/config.py` and update `MODEL_NAME`:

```python
MODEL_NAME = "ollama_chat/llama3.1:latest"
```

Other Ollama model examples:
- `ollama_chat/ministral-3:8b`
- `ollama_chat/mistral-nemo:12b`
- `ollama_chat/qwen2.5:14b`

## Usage

Run the agent web interface:

```bash
adk web
```

### Example Queries

**General:**
- "What is the latest news about AI?"
- "What time is it?"

**Stocks (Indian market):**
- "Tell me about Reliance Industries stock"
- "Show me TCS stock fundamentals and financials"
- "Analyze the risk and return of INFY stock"

**Mutual Funds (Indian):**
- "Search for SBI small cap mutual fund"
- "Show me details of Axis Bluechip Fund"
- "Compare HDFC and ICICI large cap funds"

## Data Sources

| Data | Source | Cost |
|------|--------|------|
| Indian stocks (NSE/BSE) | yfinance | Free, no API key |
| Indian mutual funds (AMFI) | mftool | Free, no API key |
| Risk/return metrics | Calculated (pandas/numpy) | Free |
| Financial news & supplementary data | Tavily | API key required |

## Requirements

- Python 3.12 or higher
- Ollama running locally
- Tavily API key (for web search)

## Author

Kamruddin

---

**Disclaimer:** The financial advisor agent is for educational and informational purposes only. It does not constitute financial advice or investment recommendation. Past performance is not indicative of future results.
