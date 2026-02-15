"""
Investment analysis tools that calculate risk and return metrics
from historical data for both stocks and mutual funds.

Metrics calculated:
  - CAGR (Compound Annual Growth Rate) for 1Y, 3Y, 5Y
  - Annualized volatility (standard deviation of daily returns)
  - Sharpe ratio (risk-adjusted return, using India's risk-free rate ~7%)
  - Maximum drawdown (worst peak-to-trough decline)
  - Rolling returns
"""

import numpy as np
import pandas as pd
import yfinance as yf
from mftool import Mftool

# India's approximate risk-free rate (10-year government bond yield)
RISK_FREE_RATE = 0.07

mf = Mftool()


def _get_stock_prices(symbol: str, years: int = 5) -> pd.Series | None:
    """Fetch closing price series for a stock from yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        period = f"{years}y" if years <= 10 else "max"
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        return hist["Close"]
    except Exception:
        return None


def _get_mf_navs(scheme_code: str) -> pd.Series | None:
    """Fetch historical NAV series for a mutual fund from AMFI."""
    try:
        history = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
        if history is None or history.empty:
            return None

        # mftool returns nav as string; convert to float
        nav_series = history["nav"].astype(float)

        # Convert index to datetime if it isn't already
        if not isinstance(nav_series.index, pd.DatetimeIndex):
            nav_series.index = pd.to_datetime(nav_series.index, format="%d-%m-%Y", errors="coerce")

        nav_series = nav_series.dropna()
        nav_series = nav_series.sort_index()
        return nav_series
    except Exception:
        return None


def _calculate_cagr(prices: pd.Series, years: int) -> float | None:
    """Calculate CAGR over the last N years from a price series."""
    if prices is None or len(prices) < 2:
        return None

    trading_days = years * 252
    if len(prices) < trading_days:
        # Use whatever data is available
        actual_days = len(prices)
        actual_years = actual_days / 252
    else:
        actual_years = years
        prices = prices.iloc[-trading_days:]

    start_val = float(prices.iloc[0])
    end_val = float(prices.iloc[-1])

    if start_val <= 0:
        return None

    cagr = (end_val / start_val) ** (1 / actual_years) - 1
    return round(cagr * 100, 2)


def _calculate_volatility(prices: pd.Series) -> float | None:
    """Calculate annualized volatility from a price series."""
    if prices is None or len(prices) < 30:
        return None

    daily_returns = prices.pct_change().dropna()
    if daily_returns.empty:
        return None

    annualized_vol = float(daily_returns.std() * np.sqrt(252))
    return round(annualized_vol * 100, 2)


def _calculate_sharpe(prices: pd.Series) -> float | None:
    """Calculate annualized Sharpe ratio."""
    if prices is None or len(prices) < 30:
        return None

    daily_returns = prices.pct_change().dropna()
    if daily_returns.empty or daily_returns.std() == 0:
        return None

    annualized_return = float(daily_returns.mean() * 252)
    annualized_vol = float(daily_returns.std() * np.sqrt(252))

    sharpe = (annualized_return - RISK_FREE_RATE) / annualized_vol
    return round(sharpe, 2)


def _calculate_max_drawdown(prices: pd.Series) -> float | None:
    """Calculate maximum drawdown (worst peak-to-trough decline)."""
    if prices is None or len(prices) < 2:
        return None

    cumulative_max = prices.cummax()
    drawdowns = (prices - cumulative_max) / cumulative_max
    max_dd = float(drawdowns.min())
    return round(max_dd * 100, 2)


def analyze_investment(identifier: str, investment_type: str = "stock") -> dict:
    """Calculates comprehensive risk and return metrics for a stock or mutual fund.

    This tool computes CAGR (1Y, 3Y, 5Y), annualized volatility, Sharpe ratio,
    and maximum drawdown from historical price/NAV data.

    Args:
        identifier: The stock symbol (e.g. 'RELIANCE.NS', 'TCS.NS') or
                    mutual fund scheme code (e.g. '119597', '120503').
        investment_type: Either 'stock' or 'mutual_fund'.
                         Use 'stock' for NSE/BSE equities.
                         Use 'mutual_fund' for AMFI scheme codes.

    Returns:
        A dictionary with CAGR (1Y, 3Y, 5Y), annualized volatility,
        Sharpe ratio, maximum drawdown, and data summary.
    """
    try:
        if investment_type == "stock":
            prices = _get_stock_prices(identifier, years=5)
            label = f"Stock: {identifier}"
        elif investment_type == "mutual_fund":
            prices = _get_mf_navs(identifier)
            label = f"Mutual Fund (scheme code: {identifier})"
        else:
            return {"error": f"Invalid investment_type '{investment_type}'. Use 'stock' or 'mutual_fund'."}

        if prices is None or len(prices) < 10:
            return {"error": f"Insufficient historical data for '{identifier}'. Verify the identifier and try again."}

        # Calculate metrics
        cagr_1y = _calculate_cagr(prices, 1)
        cagr_3y = _calculate_cagr(prices, 3)
        cagr_5y = _calculate_cagr(prices, 5)
        volatility = _calculate_volatility(prices)
        sharpe = _calculate_sharpe(prices)
        max_drawdown = _calculate_max_drawdown(prices)

        result = {
            "identifier": identifier,
            "investment_type": investment_type,
            "label": label,
            "data_points": len(prices),
            "data_start_date": prices.index[0].strftime("%Y-%m-%d"),
            "data_end_date": prices.index[-1].strftime("%Y-%m-%d"),
            "latest_value": round(float(prices.iloc[-1]), 2),
            "metrics": {
                "cagr_1y_percent": cagr_1y if cagr_1y is not None else "Insufficient data",
                "cagr_3y_percent": cagr_3y if cagr_3y is not None else "Insufficient data",
                "cagr_5y_percent": cagr_5y if cagr_5y is not None else "Insufficient data",
                "annualized_volatility_percent": volatility if volatility is not None else "Insufficient data",
                "sharpe_ratio": sharpe if sharpe is not None else "Insufficient data",
                "max_drawdown_percent": max_drawdown if max_drawdown is not None else "Insufficient data",
            },
            "assumptions": {
                "risk_free_rate_percent": RISK_FREE_RATE * 100,
                "trading_days_per_year": 252,
            },
            "disclaimer": "Past performance is not indicative of future results. This is for informational purposes only.",
        }

        return result
    except Exception as e:
        return {"error": f"Analysis failed for '{identifier}': {str(e)}"}
