import httpx
from fastmcp.exceptions import ToolError

# -------------------------
# COMMON API HELPER
# -------------------------
BASE_URL = "https://api.finapi.upvaly.com"


async def make_api_call(endpoint: str, params: dict = None):
    """
    Common helper for making unauthenticated API calls to the Analytics API.

    Args:
        endpoint: The API endpoint path (e.g., "/api/analytics/mf/top-performers")
        params: Optional query parameters dict

    Returns:
        Parsed JSON response

    Raises:
        ToolError: If the API call fails
    """
    async with httpx.AsyncClient(timeout=15) as client:
        url = f"{BASE_URL}{endpoint}"
        response = await client.get(url, params=params, headers={"Accept": "application/json"})

        if response.status_code != 200:
            raise ToolError(response.text)

        return response.json()


# -------------------------
# MCP TOOLS SETUP
# -------------------------
def setup_tools(mcp):
    """Register all Analytics API tools with the MCP server"""

    # ── Mutual Fund: Performance ──────────────────────────────────────────────

    @mcp.tool()
    async def get_mf_top_performers(period: str = "3y", limit: int = 10, category: str = ""):
        """
        Get top performing mutual funds for a given return period.

        Answers questions like:
        - "Which mutual funds performed best in the last 3 years?"
        - "Top 10 debt funds by 5-year returns"
        - "Best performing large cap funds"

        Args:
            period: Return period — one of: 1y, 3y, 5y, 7y, 10y (default: 3y)
            limit: Maximum number of results to return, up to 100 (default: 10)
            category: Optional category filter — partial match e.g. "Equity", "Debt", "Large Cap"

        Returns:
            List of top performing mutual funds with returns, NAV, AUM, and other details.
        """
        params = {"period": period, "limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/top-performers", params)

    @mcp.tool()
    async def get_mf_consistent_performers(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the best average return consistently across 1-year, 3-year, and 5-year periods.
        Only funds that have data for all three periods are included.

        Answers questions like:
        - "Which mutual fund has been consistently performing well in last 1, 3, and 5 years?"
        - "Best all-weather mutual funds"

        Args:
            limit: Maximum number of results to return, up to 100 (default: 10)
            category: Optional category filter — partial match e.g. "Equity", "Debt"

        Returns:
            List of consistently performing mutual funds ranked by average return across 1y, 3y, and 5y.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/consistent-performers", params)

    @mcp.tool()
    async def get_mf_worst_performers(period: str = "1y", limit: int = 10, category: str = ""):
        """
        Get worst performing mutual funds for a given return period.

        Answers questions like:
        - "Which mutual funds are underperforming this year?"
        - "Worst performing small cap funds"

        Args:
            period: Return period — one of: 1y, 3y, 5y, 7y, 10y (default: 1y)
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Small Cap", "Debt"

        Returns:
            List of worst performing mutual funds with returns and details.
        """
        params = {"period": period, "limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/worst-performers", params)

    # ── Mutual Fund: Holdings & Sector ────────────────────────────────────────

    @mcp.tool()
    async def get_mf_by_holding(stockName: str, limit: int = 20):
        """
        Find mutual funds that hold a specific stock in their portfolio.
        Uses partial, case-insensitive name matching so you don't need an exact name.

        Answers questions like:
        - "Which mutual funds have HDFC Bank as a top holding?"
        - "Show me funds that hold Reliance Industries"
        - "Which mutual funds are invested in Infosys?"

        Args:
            stockName: Stock name to search for (e.g. "HDFC Bank", "Reliance", "Infosys") — required
            limit: Maximum number of results to return, up to 100 (default: 20)

        Returns:
            List of mutual funds holding the specified stock, with holding weightage context.
        """
        params = {"stockName": stockName, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-holding", params)

    @mcp.tool()
    async def get_mf_by_sector_exposure(sector: str, limit: int = 20):
        """
        Find mutual funds with the highest exposure to a given sector.
        Results are sorted by sector weightage in descending order.

        Answers questions like:
        - "Which mutual funds have maximum Financial Services exposure?"
        - "Funds with high technology sector allocation"
        - "Healthcare sector focused mutual funds"

        Args:
            sector: Sector name to search for (e.g. "Financial Services", "Technology", "Healthcare") — required
            limit: Maximum number of results to return, up to 100 (default: 20)

        Returns:
            List of mutual funds ranked by their exposure to the specified sector.
        """
        params = {"sector": sector, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-sector-exposure", params)

    # ── Mutual Fund: Ratings & Risk ───────────────────────────────────────────

    @mcp.tool()
    async def get_mf_by_rating(rating: int, limit: int = 20, category: str = ""):
        """
        Get mutual funds filtered by Morningstar star rating (1 to 5, where 5 is best).
        Returns an error if rating is outside the 1–5 range.

        Answers questions like:
        - "Which mutual funds have a 5-star Morningstar rating?"
        - "Show me 4 or 5 star rated equity funds"

        Args:
            rating: Morningstar star rating — integer from 1 (worst) to 5 (best) — required
            limit: Maximum number of results to return (default: 20)
            category: Optional category filter — partial match e.g. "Equity"

        Returns:
            List of mutual funds with the specified Morningstar rating.
        """
        params = {"rating": rating, "limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/by-rating", params)

    @mcp.tool()
    async def get_mf_by_risk_level(risk: str, limit: int = 20):
        """
        Get mutual funds filtered by their official risk label.
        Supports partial matching so "Low" matches "Moderately Low" as well.

        Answers questions like:
        - "Show me low-risk mutual funds"
        - "Which funds have very high risk?"
        - "Safe mutual funds for conservative investors"

        Args:
            risk: Risk label — partial match against: "Low", "Moderately Low", "Moderate",
                  "Moderately High", "High", "Very High" — required
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of mutual funds matching the specified risk level.
        """
        params = {"risk": risk, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-risk-level", params)

    @mcp.tool()
    async def get_mf_by_fund_manager(managerName: str, limit: int = 20):
        """
        Get mutual funds managed by a specific fund manager.
        Uses partial, case-insensitive name matching.

        Answers questions like:
        - "Which mutual funds does Prashant Jain manage?"
        - "Show me funds managed by Nilesh Shah"

        Args:
            managerName: Fund manager name — partial match, case-insensitive (e.g. "Prashant Jain") — required
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of mutual funds managed by the specified fund manager.
        """
        params = {"managerName": managerName, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-fund-manager", params)

    @mcp.tool()
    async def get_mf_by_benchmark(benchmark: str, limit: int = 20):
        """
        Get mutual funds benchmarked against a specific index.
        Uses partial, case-insensitive matching for the benchmark name.

        Answers questions like:
        - "Which mutual funds track Nifty 50?"
        - "Funds benchmarked against BSE Sensex"

        Args:
            benchmark: Benchmark index name — partial match (e.g. "Nifty 50", "BSE Sensex", "Nifty Midcap") — required
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of mutual funds using the specified benchmark index.
        """
        params = {"benchmark": benchmark, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-benchmark", params)

    # ── Mutual Fund: Portfolio Allocation ─────────────────────────────────────

    @mcp.tool()
    async def get_mf_highest_cash_allocation(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the highest percentage of cash or cash-equivalents in their portfolio.

        Answers questions like:
        - "Which mutual fund has the highest cash allocation?"
        - "Which funds are sitting on the most cash?"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Equity"

        Returns:
            List of mutual funds ranked by cash allocation percentage, highest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/highest-cash-allocation", params)

    @mcp.tool()
    async def get_mf_highest_equity_allocation(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the highest equity allocation percentage in their portfolio.

        Answers questions like:
        - "Which funds have maximum equity exposure?"
        - "Most equity-heavy mutual funds"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Hybrid"

        Returns:
            List of mutual funds ranked by equity allocation percentage, highest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/highest-equity-allocation", params)

    @mcp.tool()
    async def get_mf_large_cap_heavy(limit: int = 10):
        """
        Get mutual funds with the highest large-cap stock allocation within their equity portfolio.

        Answers questions like:
        - "Which funds invest most in large-cap stocks?"
        - "Best large cap oriented funds"

        Args:
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of mutual funds ranked by large-cap allocation percentage, highest first.
        """
        params = {"limit": limit}
        return await make_api_call("/api/analytics/mf/large-cap-heavy", params)

    @mcp.tool()
    async def get_mf_mid_cap_heavy(limit: int = 10):
        """
        Get mutual funds with the highest mid-cap stock allocation within their equity portfolio.

        Answers questions like:
        - "Which funds have maximum mid-cap exposure?"
        - "Funds most heavy in mid-cap stocks"

        Args:
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of mutual funds ranked by mid-cap allocation percentage, highest first.
        """
        params = {"limit": limit}
        return await make_api_call("/api/analytics/mf/mid-cap-heavy", params)

    @mcp.tool()
    async def get_mf_small_cap_heavy(limit: int = 10):
        """
        Get mutual funds with the highest small-cap stock allocation within their equity portfolio.

        Answers questions like:
        - "Which small-cap funds have the highest small-cap exposure?"
        - "Funds most heavy in small-cap stocks"

        Args:
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of mutual funds ranked by small-cap allocation percentage, highest first.
        """
        params = {"limit": limit}
        return await make_api_call("/api/analytics/mf/small-cap-heavy", params)

    # ── Mutual Fund: Cost & Efficiency ────────────────────────────────────────

    @mcp.tool()
    async def get_mf_lowest_expense_ratio(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the lowest Total Expense Ratio (TER) — the most cost-efficient funds to own.

        Answers questions like:
        - "Which mutual funds have the lowest expense ratio?"
        - "Cheapest index funds to buy"
        - "Most cost-efficient equity mutual funds"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Equity", "Index"

        Returns:
            List of mutual funds ranked by expense ratio, lowest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/lowest-expense-ratio", params)

    @mcp.tool()
    async def get_mf_highest_aum(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the highest Assets Under Management (AUM / corpus size).

        Answers questions like:
        - "Which are the largest mutual funds in India?"
        - "Top 10 debt funds by corpus"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Debt", "Equity"

        Returns:
            List of mutual funds ranked by AUM in crores, largest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/highest-aum", params)

    @mcp.tool()
    async def get_mf_lowest_volatility(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the lowest standard deviation — the least volatile and most stable funds.

        Answers questions like:
        - "Which mutual funds are the least volatile?"
        - "Stable funds suitable for risk-averse investors"
        - "Least volatile debt funds"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Debt", "Hybrid"

        Returns:
            List of mutual funds ranked by standard deviation, lowest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/lowest-volatility", params)

    # ── Mutual Fund: Category & Metadata ─────────────────────────────────────

    @mcp.tool()
    async def get_mf_categories():
        """
        Get all unique mutual fund scheme categories with their fund count, sorted by fund count descending.

        Answers questions like:
        - "What categories of mutual funds are available?"
        - "How many growth vs IDCW funds are there?"

        Returns:
            List of categories with name and fund count, e.g. [{"category": "Growth", "fundCount": 1200}, ...]
        """
        return await make_api_call("/api/analytics/mf/categories")

    @mcp.tool()
    async def get_mf_fund_houses():
        """
        Get all AMCs (Asset Management Companies / fund houses) with the number of schemes they offer,
        sorted by scheme count descending.

        Answers questions like:
        - "Which AMC offers the most mutual funds?"
        - "List all mutual fund companies"

        Returns:
            List of fund houses with their scheme counts.
        """
        return await make_api_call("/api/analytics/mf/fund-houses")

    @mcp.tool()
    async def get_mf_category_leaders():
        """
        Get analytics per mutual fund category: fund count, average 1y/3y/5y returns, and the top fund in each category.

        Answers questions like:
        - "What is the average return of equity funds?"
        - "Which is the best fund in each category?"
        - "Best fund in each mutual fund category"

        Returns:
            List of category analytics with average returns and top fund details per category.
        """
        return await make_api_call("/api/analytics/mf/category-leaders")

    @mcp.tool()
    async def get_mf_by_category(category: str, limit: int = 50):
        """
        Get all mutual funds matching a category or sub-category name.
        Uses partial, case-insensitive matching.

        Answers questions like:
        - "Show me all Large Cap mutual funds"
        - "List all liquid funds"
        - "Which funds are in the Flexi Cap category?"

        Args:
            category: Category keyword — partial match (e.g. "Large Cap", "Flexi Cap", "Liquid") — required
            limit: Maximum number of results to return, up to 200 (default: 50)

        Returns:
            List of mutual funds belonging to the specified category.
        """
        params = {"category": category, "limit": limit}
        return await make_api_call("/api/analytics/mf/by-category", params)

    # ── Mutual Fund: Vintage / Age ────────────────────────────────────────────

    @mcp.tool()
    async def get_mf_oldest_funds(limit: int = 10, category: str = ""):
        """
        Get mutual funds with the earliest inception dates — funds with the longest track records.

        Answers questions like:
        - "Which mutual funds have the longest track record?"
        - "Oldest equity mutual funds in India"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Equity"

        Returns:
            List of mutual funds sorted by inception date, oldest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/oldest-funds", params)

    @mcp.tool()
    async def get_mf_newest_funds(limit: int = 10, category: str = ""):
        """
        Get mutual funds that were launched most recently (newest NFOs / fund launches).

        Answers questions like:
        - "Which mutual funds were launched recently?"
        - "New NFOs in the equity category"

        Args:
            limit: Maximum number of results to return (default: 10)
            category: Optional category filter — partial match e.g. "Equity"

        Returns:
            List of mutual funds sorted by inception date, newest first.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        return await make_api_call("/api/analytics/mf/newest-funds", params)

    # ── IPO Analytics ─────────────────────────────────────────────────────────

    @mcp.tool()
    async def get_ipo_live(type: str = ""):
        """
        Get all IPOs currently open for subscription.

        Answers questions like:
        - "Which IPOs are currently open for subscription?"
        - "Live mainboard IPOs right now"

        Args:
            type: Optional filter — "MAINBOARD" or "SME"

        Returns:
            List of IPOs with LIVE status including price range, subscription dates, and subscription data.
        """
        params = {}
        if type:
            params["type"] = type
        return await make_api_call("/api/analytics/ipo/live", params or None)

    @mcp.tool()
    async def get_ipo_upcoming(type: str = ""):
        """
        Get all IPOs that will open soon (not yet live for subscription).

        Answers questions like:
        - "Which IPOs are opening soon?"
        - "Upcoming SME IPOs"

        Args:
            type: Optional filter — "MAINBOARD" or "SME"

        Returns:
            List of upcoming IPOs with UPCOMING status, open/close dates, and price band.
        """
        params = {}
        if type:
            params["type"] = type
        return await make_api_call("/api/analytics/ipo/upcoming", params or None)

    @mcp.tool()
    async def get_ipo_active(type: str = "", limit: int = 100):
        """
        Get all active IPOs — both LIVE and UPCOMING combined.
        For closed/historical IPOs, use search_ipo instead.

        Answers questions like:
        - "Show all active SME IPOs"
        - "List all mainboard IPOs that are open or coming soon"

        Args:
            type: Optional filter — "MAINBOARD" or "SME"
            limit: Maximum number of results to return, up to 500 (default: 100)

        Returns:
            Combined list of LIVE and UPCOMING IPOs.
        """
        params = {"limit": limit}
        if type:
            params["type"] = type
        return await make_api_call("/api/analytics/ipo/active", params)

    @mcp.tool()
    async def get_ipo_most_subscribed(limit: int = 10):
        """
        Get LIVE and UPCOMING IPOs ranked by total subscription multiple, highest first.

        Answers questions like:
        - "Which live IPOs are most over-subscribed?"
        - "Most popular upcoming IPOs by subscription"

        Args:
            limit: Maximum number of results to return, up to 100 (default: 10)

        Returns:
            List of IPOs ranked by total subscription times (e.g. 45.23x), with subscription breakdown by category.
        """
        params = {"limit": limit}
        return await make_api_call("/api/analytics/ipo/most-subscribed", params)

    @mcp.tool()
    async def get_ipo_highest_gmp(limit: int = 10):
        """
        Get LIVE and UPCOMING IPOs with the highest Grey Market Premium (GMP) value.
        GMP indicates the expected listing premium in the grey market before official listing.

        Answers questions like:
        - "Which live IPOs have the highest grey market premium right now?"
        - "Upcoming IPOs with best GMP"

        Args:
            limit: Maximum number of results to return, up to 100 (default: 10)

        Returns:
            List of active IPOs ranked by latest GMP value, highest first.
        """
        params = {"limit": limit}
        return await make_api_call("/api/analytics/ipo/highest-gmp", params)

    @mcp.tool()
    async def search_ipo(name: str, limit: int = 20):
        """
        Search for IPOs by company name or stock symbol using partial, case-insensitive matching.
        Covers ALL statuses including CLOSED/historical IPOs — use this to look up any past or present IPO.

        Answers questions like:
        - "Tell me about the Zomato IPO"
        - "Find details for any historical or recent IPO"
        - "What was the Paytm IPO price?"

        Args:
            name: Company name or stock symbol to search — partial match (e.g. "Zomato", "NSE") — required
            limit: Maximum number of results to return, up to 100 (default: 20)

        Returns:
            List of IPOs matching the search term with full details including subscription, GMP, and listing info.
        """
        params = {"name": name, "limit": limit}
        return await make_api_call("/api/analytics/ipo/search", params)

    @mcp.tool()
    async def get_ipo_overview():
        """
        Get a high-level summary of the entire IPO market across all statuses (LIVE, UPCOMING, CLOSED).

        Answers questions like:
        - "How many IPOs are currently live?"
        - "Give me an overview of the IPO market"
        - "How many total IPOs are there by type and status?"

        Returns:
            Summary with total IPO count broken down by status (LIVE/UPCOMING/CLOSED) and type (MAINBOARD/SME).
        """
        return await make_api_call("/api/analytics/ipo/overview")

    # ── Public / General ──────────────────────────────────────────────────────

    @mcp.tool()
    async def check_health():
        """
        Check the health and availability of the FinAPI API server.

        Answers questions like:
        - "Is the FinAPI API up and running?"
        - "Check server health"

        Returns:
            Health status of the API server.
        """
        return await make_api_call("/api/public/health")

    @mcp.tool()
    async def get_exchange_holidays():
        """
        Get the list of stock exchange holidays for the year.

        Answers questions like:
        - "What are the stock market holidays?"
        - "Is the market open on a specific date?"
        - "List all NSE/BSE holidays"

        Returns:
            List of exchange holidays with dates and descriptions.
        """
        return await make_api_call("/api/exchange/holidays")

    # ── Mutual Fund: Direct Lookup ────────────────────────────────────────────

    @mcp.tool()
    async def get_mf_by_scheme_code(schemeCode: str):
        """
        Get a specific mutual fund record by its unique scheme code (AMFI scheme code).

        Answers questions like:
        - "Get details of mutual fund with scheme code 118989"
        - "Fetch fund info for scheme 120503"

        Args:
            schemeCode: Unique AMFI scheme code for the mutual fund — required

        Returns:
            Full mutual fund record including NAV, returns, allocation, risk, and metadata.
        """
        return await make_api_call(f"/api/mf/scheme-code/{schemeCode}")

    @mcp.tool()
    async def get_mf_by_isin(isin: str):
        """
        Get a specific mutual fund record by its unique ISIN code.
        Works for both payout (ISIN1) and reinvestment (ISIN2) ISINs.

        Answers questions like:
        - "Find mutual fund with ISIN INF209K01YH3"
        - "Get fund details by ISIN code"

        Args:
            isin: ISIN code of the mutual fund (e.g. "INF209K01YH3") — required

        Returns:
            Full mutual fund record matching the given ISIN.
        """
        return await make_api_call(f"/api/mf/isin/{isin}")

    @mcp.tool()
    async def get_mf_by_fund_house(fundHouse: str):
        """
        Get all mutual fund records from a specific fund house / AMC.

        Answers questions like:
        - "Show all funds from HDFC Mutual Fund"
        - "List all schemes offered by SBI Mutual Fund"
        - "What funds does Mirae Asset offer?"

        Args:
            fundHouse: Name of the AMC / fund house (e.g. "HDFC Mutual Fund", "SBI Mutual Fund") — required

        Returns:
            List of all mutual fund schemes from the specified fund house.
        """
        return await make_api_call(f"/api/mf/fund-house/{fundHouse}")

    @mcp.tool()
    async def search_mf(query: str):
        """
        Wildcard search for mutual funds by scheme name — partial, case-insensitive matching.
        Use this to find funds when you know part of the name but not the exact scheme code or ISIN.

        Answers questions like:
        - "Search for Axis Bluechip funds"
        - "Find all HDFC mid cap schemes"
        - "Look up Parag Parikh Flexi Cap fund"

        Args:
            query: Partial scheme name to search for (e.g. "Axis Bluechip", "HDFC Mid Cap") — required

        Returns:
            List of mutual funds whose scheme names match the search query.
        """
        return await make_api_call("/api/mf/search", {"query": query})

    @mcp.tool()
    async def get_mf_by_scheme_name(schemeName: str):
        """
        Get a specific mutual fund record by its exact scheme name (case-insensitive, unique match).
        Use this when you have the full exact name of the fund.

        Answers questions like:
        - "Get details for 'Mirae Asset Large Cap Fund - Growth'"
        - "Fetch the fund record for exact scheme name"

        Args:
            schemeName: Full exact scheme name of the mutual fund (case-insensitive) — required

        Returns:
            The single mutual fund record matching the exact scheme name.
        """
        return await make_api_call(f"/api/mf/scheme-name/{schemeName}")

    @mcp.tool()
    async def get_mf_nav_by_isin(isin: str, startDate: str = "", endDate: str = ""):
        """
        Get historical NAV (Net Asset Value) data for a mutual fund identified by its ISIN, within an optional date range.
        Automatically resolves payout or reinvestment ISINs to the correct scheme.

        Answers questions like:
        - "What was the NAV of INF209K01YH3 last month?"
        - "Show NAV history for this ISIN between Jan and Mar 2025"
        - "Historical NAV trend for a fund by ISIN"

        Args:
            isin: ISIN code of the mutual fund — required
            startDate: Start date for NAV history in YYYY-MM-DD format (optional)
            endDate: End date for NAV history in YYYY-MM-DD format (optional)

        Returns:
            Scheme metadata and a chronologically ordered list of NAV entries with dates and values.
        """
        params = {}
        if startDate:
            params["startDate"] = startDate
        if endDate:
            params["endDate"] = endDate
        return await make_api_call(f"/api/mf/isin/{isin}/nav", params or None)

    @mcp.tool()
    async def get_mf_nav_by_scheme_code(schemeCode: str, startDate: str = "", endDate: str = ""):
        """
        Get historical NAV (Net Asset Value) data for a mutual fund identified by its scheme code, within an optional date range.

        Answers questions like:
        - "Show me the NAV history of scheme 118989 for the past year"
        - "What was the NAV of this fund in January 2024?"
        - "NAV trend for a mutual fund by scheme code"

        Args:
            schemeCode: Unique AMFI scheme code of the mutual fund — required
            startDate: Start date for NAV history in YYYY-MM-DD format (optional)
            endDate: End date for NAV history in YYYY-MM-DD format (optional)

        Returns:
            Scheme metadata and a chronologically ordered list of NAV entries with dates and values.
        """
        params = {}
        if startDate:
            params["startDate"] = startDate
        if endDate:
            params["endDate"] = endDate
        return await make_api_call(f"/api/mf/scheme-code/{schemeCode}/nav", params or None)

