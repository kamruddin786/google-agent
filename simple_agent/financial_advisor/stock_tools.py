"""
Stock market tools for Indian equities (NSE/BSE) using yfinance.

Ticker format:
  - NSE stocks: append .NS (e.g. RELIANCE.NS, TCS.NS, INFY.NS)
  - BSE stocks: append .BO (e.g. RELIANCE.BO)
  - Indices: ^NSEI (NIFTY 50), ^BSESN (SENSEX)
"""

from datetime import datetime

import yfinance as yf


def get_stock_info(symbol: str) -> dict:
    """Fetches company info and key fundamentals for an Indian stock.

    Args:
        symbol: NSE/BSE ticker symbol with exchange suffix.
                Examples: 'RELIANCE.NS', 'TCS.NS', 'INFY.BO'.
                Use .NS for NSE, .BO for BSE.

    Returns:
        A dictionary containing company name, sector, industry, market cap,
        P/E ratio, P/B ratio, EPS, dividend yield, 52-week high/low,
        current price, and other key fundamentals.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or info.get("trailingPegRatio") is None and info.get("shortName") is None:
            return {"error": f"No data found for symbol '{symbol}'. Verify the ticker and exchange suffix (.NS for NSE, .BO for BSE)."}

        result = {
            "symbol": symbol,
            "data_fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": info.get("shortName") or info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "currency": info.get("currency", "INR"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", "N/A"),
            "previous_close": info.get("previousClose", "N/A"),
            "open": info.get("open", "N/A"),
            "day_high": info.get("dayHigh", "N/A"),
            "day_low": info.get("dayLow", "N/A"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio_trailing": info.get("trailingPE", "N/A"),
            "pe_ratio_forward": info.get("forwardPE", "N/A"),
            "pb_ratio": info.get("priceToBook", "N/A"),
            "eps_trailing": info.get("trailingEps", "N/A"),
            "eps_forward": info.get("forwardEps", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "book_value": info.get("bookValue", "N/A"),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "return_on_equity": info.get("returnOnEquity", "N/A"),
            "revenue": info.get("totalRevenue", "N/A"),
            "profit_margin": info.get("profitMargins", "N/A"),
            "beta": info.get("beta", "N/A"),
            "average_volume": info.get("averageVolume", "N/A"),
            "description": (info.get("longBusinessSummary") or "N/A")[:500],
        }
        return result
    except Exception as e:
        return {"error": f"Failed to fetch stock info for '{symbol}': {str(e)}"}


def get_stock_history(symbol: str, period: str = "1y") -> dict:
    """Fetches historical OHLCV (Open, High, Low, Close, Volume) price data for a stock.

    Args:
        symbol: NSE/BSE ticker symbol with exchange suffix.
                Examples: 'RELIANCE.NS', 'TCS.NS', 'INFY.BO'.
        period: Time period for historical data.
                Valid values: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'.
                Defaults to '1y'.

    Returns:
        A dictionary with the stock symbol, period, number of data points,
        and a list of recent price records (last 30 entries) with date, open,
        high, low, close, and volume.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            return {"error": f"No historical data found for '{symbol}' with period '{period}'."}

        # Convert to a list of dicts; limit to last 30 rows for readability
        records = []
        for date, row in hist.tail(30).iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        return {
            "symbol": symbol,
            "data_fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "period": period,
            "total_data_points": len(hist),
            "showing_last": len(records),
            "start_date": hist.index[0].strftime("%Y-%m-%d"),
            "end_date": hist.index[-1].strftime("%Y-%m-%d"),
            "recent_prices": records,
        }
    except Exception as e:
        return {"error": f"Failed to fetch history for '{symbol}': {str(e)}"}


def get_stock_financials(symbol: str) -> dict:
    """Fetches key financial statements (income statement and balance sheet) for a stock.

    Args:
        symbol: NSE/BSE ticker symbol with exchange suffix.
                Examples: 'RELIANCE.NS', 'TCS.NS'.

    Returns:
        A dictionary containing recent annual income statement items
        (revenue, net income, EBITDA, etc.) and balance sheet items
        (total assets, total debt, cash, etc.).
    """
    try:
        ticker = yf.Ticker(symbol)

        result = {
            "symbol": symbol,
            "data_fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Income statement (most recent annual)
        income_stmt = ticker.income_stmt
        if income_stmt is not None and not income_stmt.empty:
            latest_col = income_stmt.columns[0]
            period_label = latest_col.strftime("%Y-%m-%d") if hasattr(latest_col, "strftime") else str(latest_col)

            income_data = {}
            key_fields = [
                "Total Revenue", "Gross Profit", "EBITDA", "Operating Income",
                "Net Income", "Basic EPS", "Diluted EPS",
            ]
            for field in key_fields:
                if field in income_stmt.index:
                    val = income_stmt.loc[field, latest_col]
                    income_data[field] = float(val) if val is not None else "N/A"

            result["income_statement"] = {
                "period": period_label,
                "data": income_data,
            }
        else:
            result["income_statement"] = {"data": "N/A"}

        # Balance sheet (most recent annual)
        balance_sheet = ticker.balance_sheet
        if balance_sheet is not None and not balance_sheet.empty:
            latest_col = balance_sheet.columns[0]
            period_label = latest_col.strftime("%Y-%m-%d") if hasattr(latest_col, "strftime") else str(latest_col)

            balance_data = {}
            key_fields = [
                "Total Assets", "Total Liabilities Net Minority Interest",
                "Total Debt", "Cash And Cash Equivalents",
                "Stockholders Equity", "Net Tangible Assets",
            ]
            for field in key_fields:
                if field in balance_sheet.index:
                    val = balance_sheet.loc[field, latest_col]
                    balance_data[field] = float(val) if val is not None else "N/A"

            result["balance_sheet"] = {
                "period": period_label,
                "data": balance_data,
            }
        else:
            result["balance_sheet"] = {"data": "N/A"}

        return result
    except Exception as e:
        return {"error": f"Failed to fetch financials for '{symbol}': {str(e)}"}
