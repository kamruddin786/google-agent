"""
Mutual fund tools for Indian schemes using mftool (AMFI data) and Tavily web search.

Scheme codes are numeric identifiers used by AMFI to uniquely identify
mutual fund schemes. Examples:
  - 119597: Axis Bluechip Fund - Direct Plan - Growth
  - 120503: SBI Small Cap Fund - Direct Plan - Growth
"""

import os

from mftool import Mftool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

mf = Mftool()

_tavily_client = None


def _get_tavily():
    """Lazy-initialise the Tavily client so the API key is read at call time."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is not set in the environment.")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def search_mutual_fund(query: str) -> dict:
    """Searches for Indian mutual fund schemes by name or fund house.

    Args:
        query: A search term such as a fund name, fund house, or category.
               Examples: 'axis bluechip', 'SBI small cap', 'ICICI prudential',
               'HDFC equity', 'mirae asset large cap'.

    Returns:
        A dictionary with matching scheme names and their AMFI scheme codes.
        Use the scheme code with get_mf_details() to fetch detailed data.
    """
    try:
        # Get all available schemes and filter by query
        all_schemes = mf.get_scheme_codes()

        if not all_schemes:
            return {"error": "Unable to fetch scheme list from AMFI."}

        query_lower = query.lower()
        query_terms = query_lower.split()

        matches = {}
        for code, name in all_schemes.items():
            name_lower = name.lower()
            if all(term in name_lower for term in query_terms):
                matches[code] = name

        if not matches:
            return {
                "message": f"No mutual fund schemes found matching '{query}'.",
                "suggestion": "Try broader terms like the fund house name (e.g. 'axis', 'sbi', 'hdfc') or category (e.g. 'bluechip', 'small cap', 'flexi cap').",
            }

        # Limit results to 20 for readability
        limited = dict(list(matches.items())[:20])
        return {
            "query": query,
            "total_matches": len(matches),
            "showing": len(limited),
            "schemes": limited,
            "note": "Use the scheme code (numeric key) with get_mf_details to fetch NAV and details.",
        }
    except Exception as e:
        return {"error": f"Failed to search mutual funds: {str(e)}"}


def get_mf_details(scheme_code: str) -> dict:
    """Fetches current NAV, scheme info, and recent NAV history for a mutual fund.

    Args:
        scheme_code: The AMFI scheme code (numeric string).
                     Examples: '119597', '120503'.
                     Use search_mutual_fund() to find scheme codes.

    Returns:
        A dictionary with scheme name, current NAV, fund house, scheme type/category,
        and the last 30 historical NAV entries.
    """
    try:
        # Get current scheme quote
        quote = mf.get_scheme_quote(scheme_code)

        if not quote or "error" in str(quote).lower():
            return {"error": f"No data found for scheme code '{scheme_code}'. Verify the code using search_mutual_fund()."}

        result = {
            "scheme_code": scheme_code,
            "scheme_name": quote.get("scheme_name", "N/A"),
            "fund_house": quote.get("fund_house", "N/A"),
            "scheme_type": quote.get("scheme_type", "N/A"),
            "scheme_category": quote.get("scheme_category", "N/A"),
            "nav": quote.get("nav", "N/A"),
            "nav_date": quote.get("date", "N/A"),
        }

        # Fetch historical NAV data
        try:
            history = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
            if history is not None and not history.empty:
                # Show last 30 entries
                recent = history.tail(30)
                nav_history = []
                for date_val, row in recent.iterrows():
                    nav_history.append({
                        "date": str(date_val),
                        "nav": str(row.get("nav", "N/A")),
                    })
                result["recent_nav_history"] = nav_history
                result["total_nav_records"] = len(history)
            else:
                result["recent_nav_history"] = "No historical data available."
        except Exception:
            result["recent_nav_history"] = "Could not fetch historical NAV data."

        return result
    except Exception as e:
        return {"error": f"Failed to fetch details for scheme '{scheme_code}': {str(e)}"}


def search_financial_news(query: str) -> dict:
    """Searches the web for financial news, market analysis, and investment information.

    Use this tool to find information not available from structured APIs, such as:
    - Mutual fund expense ratios, sector allocation, top holdings
    - Latest market news and analyst opinions
    - Fund manager details and AUM
    - Stock-specific news and events

    Args:
        query: A search query focused on financial/investment topics.
               Examples: 'SBI small cap fund expense ratio sector allocation',
               'Reliance Industries latest quarterly results 2026',
               'best performing large cap mutual funds India 2026'.

    Returns:
        A list of search results with titles, URLs, and content snippets.
    """
    try:
        tavily = _get_tavily()
        response = tavily.search(
            query=query,
            search_depth="advanced",
            include_domains=[
                "moneycontrol.com", "valueresearchonline.com",
                "economictimes.indiatimes.com", "livemint.com",
                "screener.in", "tickertape.in", "morningstar.in",
                "amfiindia.com", "mutualfundindia.com",
            ],
        )
        results = response.get("results", [])

        if not results:
            return {"message": f"No financial news found for '{query}'."}

        cleaned = []
        for r in results[:8]:
            cleaned.append({
                "title": r.get("title", "N/A"),
                "url": r.get("url", "N/A"),
                "content": (r.get("content") or "")[:400],
            })

        return {
            "query": query,
            "results_count": len(cleaned),
            "results": cleaned,
        }
    except Exception as e:
        return {"error": f"Financial news search failed: {str(e)}"}
