# MCP Analytics API Documentation

**Base URL:** `/api/analytics`  
**Auth:** None required (auth-free)  
**Format:** JSON (`APIResponse<T>` wrapper with `status`, `message`, `data` fields)

---

## Overview

The MCP Analytics Controller exposes rich, AI-friendly analytical endpoints over FinAPI's mutual fund and IPO dataset. These APIs are designed specifically for **MCP (Model Context Protocol) server** use — enabling LLMs to answer natural-language financial questions backed by real data.

### Response Envelope

Every endpoint returns:

```json
{
  "status": "SUCCESS",
  "message": "...",
  "data": [ ... ]
}
```

---

## Mutual Fund Analytics

### Performance

---

#### `GET /api/analytics/mf/top-performers`

Returns top performing mutual funds for a given return period.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | `3y` | Return period: `1y`, `3y`, `5y`, `7y`, `10y` |
| `limit` | int | `10` | Max results (cap: 100) |
| `category` | string | — | Optional category filter (partial match, e.g. `Equity`, `Debt`) |

**Example:**
```
GET /api/analytics/mf/top-performers?period=3y&limit=10&category=Equity
```

**Use-cases:**
- "Which mutual funds performed best in the last 3 years?"
- "Top 10 debt funds by 5-year returns"
- "Best performing large cap funds"

---

#### `GET /api/analytics/mf/consistent-performers`

Returns funds with the best **average** return across 1y, 3y, and 5y periods. Only funds with all three periods available are included.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results (cap: 100) |
| `category` | string | — | Optional category filter |

**Example:**
```
GET /api/analytics/mf/consistent-performers?limit=10
```

**Use-cases:**
- "Which mutual fund has been consistently performing well in last 1, 2, and 3 years?"
- "Best all-weather mutual funds"

---

#### `GET /api/analytics/mf/worst-performers`

Returns worst performing mutual funds for a given return period.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | `1y` | Return period: `1y`, `3y`, `5y`, `7y`, `10y` |
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Example:**
```
GET /api/analytics/mf/worst-performers?period=1y&limit=10
```

**Use-cases:**
- "Which mutual funds are underperforming this year?"
- "Worst performing small cap funds"

---

### Holdings & Sector

---

#### `GET /api/analytics/mf/by-holding`

Finds mutual funds that hold a specific stock. Partial, case-insensitive name match against portfolio holdings.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `stockName` | string | **required** | Stock name (e.g. `HDFC Bank`, `Reliance`, `Infosys`) |
| `limit` | int | `20` | Max results (cap: 100) |

**Example:**
```
GET /api/analytics/mf/by-holding?stockName=HDFC+Bank&limit=20
```

**Use-cases:**
- "Which mutual funds have HDFC Bank as a top holding?"
- "Show me funds that hold Reliance Industries"
- "Which mutual funds are invested in Infosys?"

**Response `analyticsContext` field:** `holding=HDFC Bank Ltd., weightage=8.5%`

---

#### `GET /api/analytics/mf/by-sector-exposure`

Finds mutual funds with highest exposure to a given sector. Sorted by sector weightage descending.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sector` | string | **required** | Sector name (e.g. `Financial Services`, `Technology`, `Healthcare`) |
| `limit` | int | `20` | Max results (cap: 100) |

**Example:**
```
GET /api/analytics/mf/by-sector-exposure?sector=Financial+Services&limit=15
```

**Use-cases:**
- "Which mutual funds have maximum Financial Services exposure?"
- "Funds with high technology sector allocation"
- "Healthcare sector focused mutual funds"

**Response `analyticsContext` field:** `sector=Financial Services, weightage=32.4%`

---

### Ratings & Risk

---

#### `GET /api/analytics/mf/by-rating`

Returns mutual funds filtered by Morningstar star rating.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `rating` | int | **required** | Morningstar rating `1`–`5` (5 = best) |
| `limit` | int | `20` | Max results |
| `category` | string | — | Optional category filter |

**Validation:** Returns `400 Bad Request` if rating is outside the 1–5 range.

**Example:**
```
GET /api/analytics/mf/by-rating?rating=5&limit=20
```

**Use-cases:**
- "Which mutual funds have a 5-star Morningstar rating?"
- "Show me 4 or 5 star rated equity funds"

---

#### `GET /api/analytics/mf/by-risk-level`

Returns mutual funds filtered by their official risk label.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `risk` | string | **required** | Risk label (partial match): `Low`, `Moderately Low`, `Moderate`, `Moderately High`, `High`, `Very High` |
| `limit` | int | `20` | Max results |

**Example:**
```
GET /api/analytics/mf/by-risk-level?risk=Low&limit=20
```

**Use-cases:**
- "Show me low-risk mutual funds"
- "Which funds have very high risk?"
- "Safe mutual funds for conservative investors"

---

#### `GET /api/analytics/mf/by-fund-manager`

Returns mutual funds managed by a specific fund manager (partial name match).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `managerName` | string | **required** | Fund manager name (partial, case-insensitive) |
| `limit` | int | `20` | Max results |

**Example:**
```
GET /api/analytics/mf/by-fund-manager?managerName=Prashant+Jain&limit=20
```

**Use-cases:**
- "Which mutual funds does Prashant Jain manage?"
- "Show me funds managed by Nilesh Shah"

---

#### `GET /api/analytics/mf/by-benchmark`

Returns mutual funds benchmarked against a specific index.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `benchmark` | string | **required** | Benchmark index name (partial match, e.g. `Nifty 50`, `BSE Sensex`, `Nifty Midcap`) |
| `limit` | int | `20` | Max results |

**Example:**
```
GET /api/analytics/mf/by-benchmark?benchmark=Nifty+50&limit=20
```

**Use-cases:**
- "Which mutual funds track Nifty 50?"
- "Funds benchmarked against BSE Sensex"

---

### Portfolio Allocation

---

#### `GET /api/analytics/mf/highest-cash-allocation`

Returns mutual funds with the highest percentage of cash or cash-equivalents in their portfolio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Example:**
```
GET /api/analytics/mf/highest-cash-allocation?limit=10
```

**Use-cases:**
- "Which mutual fund has the highest cash allocation?"
- "Which funds are sitting on the most cash?"

---

#### `GET /api/analytics/mf/highest-equity-allocation`

Returns mutual funds with the highest equity allocation percentage.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Use-cases:**
- "Which funds have maximum equity exposure?"

---

#### `GET /api/analytics/mf/large-cap-heavy`

Returns mutual funds with the highest large-cap stock allocation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |

**Use-cases:**
- "Which funds invest most in large-cap stocks?"
- "Best large cap oriented funds"

---

#### `GET /api/analytics/mf/mid-cap-heavy`

Returns mutual funds with the highest mid-cap stock allocation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |

**Use-cases:**
- "Which funds have maximum mid-cap exposure?"

---

#### `GET /api/analytics/mf/small-cap-heavy`

Returns mutual funds with the highest small-cap stock allocation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |

**Use-cases:**
- "Which small-cap funds have the highest small-cap exposure?"

---

### Cost & Efficiency

---

#### `GET /api/analytics/mf/lowest-expense-ratio`

Returns mutual funds with the lowest Total Expense Ratio (TER) — the cheapest funds to own.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Example:**
```
GET /api/analytics/mf/lowest-expense-ratio?limit=10&category=Equity
```

**Use-cases:**
- "Which mutual funds have the lowest expense ratio?"
- "Cheapest index funds to buy"
- "Most cost-efficient equity mutual funds"

---

#### `GET /api/analytics/mf/highest-aum`

Returns mutual funds with the highest Assets Under Management (corpus size).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Use-cases:**
- "Which are the largest mutual funds in India?"
- "Top 10 debt funds by corpus"

---

#### `GET /api/analytics/mf/lowest-volatility`

Returns mutual funds with the lowest standard deviation — least volatile / most stable funds.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Use-cases:**
- "Which mutual funds are the least volatile?"
- "Stable funds suitable for risk-averse investors"

---

### Category & Metadata

---

#### `GET /api/analytics/mf/categories`

Returns all unique scheme categories with their fund count, sorted by fund count descending.

**Example response:**
```json
[
  { "category": "Growth", "fundCount": 1200 },
  { "category": "IDCW", "fundCount": 600 }
]
```

**Use-cases:**
- "What categories of mutual funds are available?"
- "How many growth vs IDCW funds are there?"

---

#### `GET /api/analytics/mf/fund-houses`

Returns all AMCs (fund houses) with the number of schemes they offer, sorted by fund count.

**Use-cases:**
- "Which AMC offers the most mutual funds?"
- "List all mutual fund companies"

---

#### `GET /api/analytics/mf/category-leaders`

Returns analytics per category: fund count, average 1y/3y/5y returns, and the top fund in each category.

**Example response:**
```json
[
  {
    "name": "Equity Schemes",
    "fundCount": 520,
    "avgReturn1y": "18.45%",
    "avgReturn3y": "14.22%",
    "avgReturn5y": "16.10%",
    "topFundName": "Mirae Asset Large Cap Fund",
    "topFundSchemeCode": "118989",
    "topFundReturn3y": "22.5%"
  }
]
```

**Use-cases:**
- "What is the average return of equity funds?"
- "Which is the best fund in each category?"

---

#### `GET /api/analytics/mf/by-category`

Returns all funds matching a category or sub-category name (partial match).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category` | string | **required** | Category keyword (e.g. `Large Cap`, `Flexi Cap`, `Liquid`) |
| `limit` | int | `50` | Max results (cap: 200) |

**Example:**
```
GET /api/analytics/mf/by-category?category=Large+Cap&limit=50
```

**Use-cases:**
- "Show me all Large Cap mutual funds"
- "List all liquid funds"
- "Which funds are in the Flexi Cap category?"

---

### Vintage / Age

---

#### `GET /api/analytics/mf/oldest-funds`

Returns mutual funds with the earliest inception dates — the longest track records.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Use-cases:**
- "Which mutual funds have the longest track record?"
- "Oldest equity mutual funds in India"

---

#### `GET /api/analytics/mf/newest-funds`

Returns mutual funds that were launched most recently.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results |
| `category` | string | — | Optional category filter |

**Use-cases:**
- "Which mutual funds were launched recently?"
- "New NFOs in the equity category"

---

## IPO Analytics

> **Scope:** Live and upcoming IPO endpoints (`/ipo/live`, `/ipo/upcoming`, `/ipo/active`, `/ipo/most-subscribed`, `/ipo/highest-gmp`) operate on active IPOs only.  
> Use `/ipo/search` to find any IPO including closed/historical ones, and `/ipo/overview` for a full market summary across all statuses.

---

#### `GET /api/analytics/ipo/live`

Returns all IPOs currently open for subscription.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | — | Filter by `MAINBOARD` or `SME` |

**Use-cases:**
- "Which IPOs are currently open for subscription?"
- "Live mainboard IPOs right now"

---

#### `GET /api/analytics/ipo/upcoming`

Returns all IPOs that will open soon (not yet live).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | — | Filter by `MAINBOARD` or `SME` |

**Use-cases:**
- "Which IPOs are opening soon?"
- "Upcoming SME IPOs"

---

#### `GET /api/analytics/ipo/active`

Returns all active IPOs (LIVE + UPCOMING combined) with optional type filter.  
For closed IPOs, use `/ipo/search`.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | — | Optional type filter: `MAINBOARD`, `SME` |
| `limit` | int | `100` | Max results (cap: 500) |

**Use-cases:**
- "Show all active SME IPOs"
- "List all mainboard IPOs that are open or coming soon"

---

#### `GET /api/analytics/ipo/most-subscribed`

Returns LIVE and UPCOMING IPOs ranked by total subscription multiple (highest first).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results (cap: 100) |

**Example:**
```
GET /api/analytics/ipo/most-subscribed?limit=10
```

**Use-cases:**
- "Which live IPOs are most over-subscribed?"
- "Most popular upcoming IPOs by subscription"

**Response `analyticsContext` field:** `totalSubscription=45.23x`

---

#### `GET /api/analytics/ipo/highest-gmp`

Returns LIVE and UPCOMING IPOs with the highest latest Grey Market Premium value.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `10` | Max results (cap: 100) |

**Example:**
```
GET /api/analytics/ipo/highest-gmp?limit=10
```

**Use-cases:**
- "Which live IPOs have the highest grey market premium right now?"
- "Upcoming IPOs with best GMP"

---

#### `GET /api/analytics/ipo/search`

Search for IPOs by company name or stock symbol (partial, case-insensitive). **Covers all statuses including CLOSED.**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **required** | Company name or symbol |
| `limit` | int | `20` | Max results (cap: 100) |

**Example:**
```
GET /api/analytics/ipo/search?name=Zomato
```

**Use-cases:**
- "Tell me about the Zomato IPO"
- "Find details for any historical or recent IPO"

---

#### `GET /api/analytics/ipo/overview`

Returns a high-level summary of the entire IPO market (all statuses).

**Example response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "totalIpos": 185,
    "byStatus": {
      "LIVE": 4,
      "UPCOMING": 12,
      "CLOSED": 169
    },
    "byType": {
      "MAINBOARD": 90,
      "SME": 95
    }
  }
}
```

**Use-cases:**
- "How many IPOs are currently live?"
- "Give me an overview of the IPO market"

---

## Response DTO Reference

### `MFAnalyticsSummaryDto`

| Field | Type | Description |
|-------|------|-------------|
| `schemeCode` | string | Unique fund scheme code |
| `schemeName` | string | Full scheme name |
| `fundHouse` | string | AMC name |
| `category` | string | Scheme category (Growth/IDCW) |
| `subCategory` | string | Sub-category (Large Cap, Flexi Cap, etc.) |
| `isin` | string | Primary ISIN |
| `morningStarRating` | int | 1–5 star rating |
| `schemeRisk` | string | Risk label |
| `latestNav` | string | Current NAV |
| `latestNavDate` | date | NAV date |
| `return1y` | string | 1-year CAGR % |
| `return3y` | string | 3-year CAGR % |
| `return5y` | string | 5-year CAGR % |
| `return7y` | string | 7-year CAGR % |
| `return10y` | string | 10-year CAGR % |
| `equityAllocation` | string | Equity % in portfolio |
| `debtAllocation` | string | Debt % in portfolio |
| `cashAllocation` | string | Cash % in portfolio |
| `otherAllocation` | string | Other assets % |
| `largeCap` | string | Large-cap % of equity |
| `midCap` | string | Mid-cap % of equity |
| `smallCap` | string | Small-cap % of equity |
| `aum` | string | AUM in crores |
| `expenseRatio` | string | TER % |
| `portfolioTurnover` | string | Portfolio turnover % |
| `standardDeviation` | string | Volatility (std dev) |
| `benchmarkIndex` | string | Benchmark index name |
| `inceptionDate` | date | Fund launch date |
| `fundManagers` | string | Comma-separated manager names |
| `exitLoadMessage` | string | Exit load details |
| `analyticsContext` | string | Ranking metric for the specific query |

---

### `IpoAnalyticsSummaryDto`

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock symbol |
| `name` | string | Company name |
| `type` | string | MAINBOARD / SME |
| `status` | string | LIVE / UPCOMING / CLOSED |
| `priceRange` | string | IPO price range |
| `openDate` | string | Subscription open date |
| `closeDate` | string | Subscription close date |
| `listingDate` | string | Expected listing date |
| `totalIssueSize` | string | Total issue size (₹ Cr) |
| `freshIssue` | string | Fresh issue component |
| `offerForSale` | string | OFS component |
| `totalSubscriptionTimes` | string | Overall subscription multiple |
| `institutionalSubscriptionTimes` | string | QIB subscription multiple |
| `niiSubscriptionTimes` | string | NII/HNI subscription multiple |
| `retailSubscriptionTimes` | string | Retail subscription multiple |
| `latestGmp` | string | Latest grey market premium |
| `gmpSource` | string | GMP data source |
| `analyticsContext` | string | Ranking metric for the specific query |

---

### `CategoryAnalyticsDto`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Category name |
| `fundCount` | long | Number of funds in category |
| `avgReturn1y` | string | Average 1-year return |
| `avgReturn3y` | string | Average 3-year return |
| `avgReturn5y` | string | Average 5-year return |
| `topFundName` | string | Best fund by 3y return |
| `topFundSchemeCode` | string | Best fund's scheme code |
| `topFundReturn3y` | string | Best fund's 3y return |

---

## MCP Server Integration Notes

1. **No Auth Required** — All `/api/analytics/**` endpoints are publicly accessible.
2. **Designed for LLM Consumption** — Each response includes an `analyticsContext` field that states the ranking metric used (e.g., `return_3y=22.5%`), making it easy for AI to present results.
3. **Partial String Matching** — Filters for `stockName`, `sector`, `category`, `benchmark`, `managerName` all use case-insensitive partial matching, so LLMs don't need exact names.
4. **Safe Limits** — All endpoints enforce a maximum result cap (100–500) to prevent large payloads.
5. **Null Safety** — All response DTOs use `@JsonInclude(NON_NULL)`, so absent data fields are omitted from responses.

---

## Quick Reference: Example MCP Queries → API Calls

| Natural Language Query | API Call |
|------------------------|----------|
| Which MF has been consistently performing well in 1, 3, 5 years? | `GET /api/analytics/mf/consistent-performers?limit=10` |
| Which MF has HDFC Bank as a top holding? | `GET /api/analytics/mf/by-holding?stockName=HDFC+Bank` |
| Which MF has the highest cash allocation? | `GET /api/analytics/mf/highest-cash-allocation?limit=10` |
| Which MF has 5 Morningstar stars? | `GET /api/analytics/mf/by-rating?rating=5` |
| Best performing equity funds in 3 years? | `GET /api/analytics/mf/top-performers?period=3y&category=Equity` |
| Cheapest index funds by expense ratio? | `GET /api/analytics/mf/lowest-expense-ratio?category=Index` |
| Large cap funds with most large-cap allocation? | `GET /api/analytics/mf/large-cap-heavy?limit=10` |
| Funds managed by Prashant Jain? | `GET /api/analytics/mf/by-fund-manager?managerName=Prashant+Jain` |
| Low risk mutual funds? | `GET /api/analytics/mf/by-risk-level?risk=Low` |
| Funds tracking Nifty 50? | `GET /api/analytics/mf/by-benchmark?benchmark=Nifty+50` |
| Funds with highest Financial Services exposure? | `GET /api/analytics/mf/by-sector-exposure?sector=Financial+Services` |
| Largest mutual funds by AUM? | `GET /api/analytics/mf/highest-aum?limit=10` |
| Least volatile debt funds? | `GET /api/analytics/mf/lowest-volatility?category=Debt` |
| Which IPOs are currently open for subscription? | `GET /api/analytics/ipo/live` |
| Which IPOs are opening soon? | `GET /api/analytics/ipo/upcoming` |
| All active (live + upcoming) IPOs? | `GET /api/analytics/ipo/active` |
| Most subscribed live/upcoming IPOs? | `GET /api/analytics/ipo/most-subscribed?limit=10` |
| Live/upcoming IPOs with highest GMP? | `GET /api/analytics/ipo/highest-gmp` |
| Search for a specific IPO (incl. closed)? | `GET /api/analytics/ipo/search?name=Zomato` |
| How many live IPOs are there? | `GET /api/analytics/ipo/overview` |
| Best fund in each category? | `GET /api/analytics/mf/category-leaders` |
| Oldest mutual funds? | `GET /api/analytics/mf/oldest-funds?limit=10` |
| Worst performing funds this year? | `GET /api/analytics/mf/worst-performers?period=1y&limit=10` |
| Recently launched mutual funds? | `GET /api/analytics/mf/newest-funds?limit=10` |
| All funds in a specific category? | `GET /api/analytics/mf/by-category?category=Large+Cap` |
| What fund categories exist? | `GET /api/analytics/mf/categories` |
| Which AMC has the most funds? | `GET /api/analytics/mf/fund-houses` |
| Funds most heavy in mid-cap stocks? | `GET /api/analytics/mf/mid-cap-heavy?limit=10` |
| Funds most heavy in small-cap stocks? | `GET /api/analytics/mf/small-cap-heavy?limit=10` |
| Most equity-heavy mutual funds? | `GET /api/analytics/mf/highest-equity-allocation?limit=10` |
