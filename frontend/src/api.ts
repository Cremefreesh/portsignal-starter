import axios from "axios";

export const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ??
    "http://localhost:8000/api",
  timeout: 10_000,
});

export type PositionCreate = {
  ticker: string;
  quantity: number;
  average_cost: number;
  currency: string;
};

export type PositionResponse = PositionCreate & {
  id: string;
};

export type PortfolioCreate = {
  name: string;
  benchmark_ticker: string;
  base_currency: string;
  positions: PositionCreate[];
};

export type PortfolioResponse = {
  id: string;
  name: string;
  benchmark_ticker: string;
  base_currency: string;
  positions: PositionResponse[];
};

export type PortfolioSummary = {
  id: string;
  name: string;
  benchmark_ticker: string;
  base_currency: string;
  positions_count: number;
  total_cost: number;
};

export async function getPortfolios(): Promise<
  PortfolioSummary[]
> {
  const response =
    await api.get<PortfolioSummary[]>("/portfolios");

  return response.data;
}

export async function getPortfolio(
  portfolioId: string,
): Promise<PortfolioResponse> {
  const response = await api.get<PortfolioResponse>(
    `/portfolios/${portfolioId}`,
  );

  return response.data;
}

export async function createPortfolio(
  payload: PortfolioCreate,
): Promise<PortfolioResponse> {
  const response = await api.post<PortfolioResponse>(
    "/portfolios",
    payload,
  );

  return response.data;
}

export type ValuedPosition = {
  position_id: string;
  ticker: string;
  quantity: number;
  average_cost: number;
  currency: string;

  current_price: number;
  previous_close: number;

  cost_basis: number;
  market_value: number;

  total_gain: number;
  total_gain_percent: number | null;

  day_change: number;
  day_change_percent: number;
};

export type PortfolioValuation = {
  portfolio_id: string;
  portfolio_name: string;
  valuation_currency: string;

  total_cost_basis: number;
  total_market_value: number;

  total_gain: number;
  total_gain_percent: number | null;

  total_day_change: number;
  total_day_change_percent: number | null;

  positions: ValuedPosition[];
  warnings: string[];
};

export async function getPortfolioValuation(
  portfolioId: string,
): Promise<PortfolioValuation> {
  const response = await api.get<PortfolioValuation>(
    `/market-data/portfolios/${portfolioId}/valuation`,
  );

  return response.data;
}

export type PortfolioHistoryPoint = {
  date: string;
  portfolio_value: number;
  cumulative_return: number;
};

export type PortfolioAnalytics = {
  portfolio_id: string;
  portfolio_name: string;
  benchmark_ticker: string;
  observation_count: number;
  start_date: string;
  end_date: string;

  annualised_return: number;
  annualised_volatility: number;
  beta: number;
  capm_expected_return: number;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  maximum_drawdown: number;
  historical_var_95: number;
  concentration_hhi: number;
  effective_holdings: number;
  largest_position_weight: number;

  history: PortfolioHistoryPoint[];
  warnings: string[];
};

export type PortfolioNewsBrief = {
  material_story_count: number;
  affected_portfolio_weight: number;
  summary: string;
};

export type PortfolioNewsArticle = {
  id: string;
  headline: string;
  summary: string;
  source: string;
  additional_sources: string[];

  url: string;
  image_url: string | null;
  published_at: string;

  affected_tickers: string[];
  affected_portfolio_weight: number;

  category: string;
  importance: "high" | "medium" | "low";
  relevance_score: number;
  why_it_matters: string;

  duplicate_count: number;
};

export type PortfolioNewsFeed = {
  portfolio_id: string;
  portfolio_name: string;
  generated_at: string;

  brief: PortfolioNewsBrief;
  articles: PortfolioNewsArticle[];
  warnings: string[];
};

export async function getPortfolioAnalytics(
  portfolioId: string,
): Promise<PortfolioAnalytics> {
  const response = await api.get<PortfolioAnalytics>(
    `/analytics/portfolios/${portfolioId}`,
  );

  return response.data;
}

export async function getPortfolioNews(
  portfolioId: string,
  days = 7,
  importantOnly = true,
  category = "all",
): Promise<PortfolioNewsFeed> {
  const response =
    await api.get<PortfolioNewsFeed>(
      `/news/portfolios/${portfolioId}`,
      {
        params: {
          days,
          important_only: importantOnly,
          category:
            category === "all"
              ? undefined
              : category,
        },
      },
    );

  return response.data;
}

export type WatchlistItem = {
  id: string;
  ticker: string;
  company_name: string;
  industry: string | null;
  logo_url: string | null;

  current_price: number;
  change: number;
  change_percent: number;
  previous_close: number;
};

export type WatchlistResponse = {
  id: string;
  name: string;
  items: WatchlistItem[];
  warnings: string[];
};

export type ScreenerRequest = {
  tickers: string[];
  minimum_price: number | null;
  maximum_price: number | null;
  minimum_market_cap: number | null;
  maximum_pe: number | null;
  minimum_daily_change: number | null;
  industry: string | null;
};

export type ScreenerResult = {
  ticker: string;
  company_name: string;
  industry: string | null;
  exchange: string | null;
  logo_url: string | null;

  current_price: number;
  daily_change_percent: number;
  market_cap_millions: number | null;
  pe_ratio: number | null;
  dividend_yield_percent: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
};

export type ScreenerResponse = {
  results: ScreenerResult[];
  rejected_tickers: string[];
  warnings: string[];
};

export async function getWatchlist() {
  const response =
    await api.get<WatchlistResponse>(
      "/watchlist",
    );

  return response.data;
}

export async function addWatchlistTicker(
  ticker: string,
) {
  const response =
    await api.post<WatchlistResponse>(
      "/watchlist/items",
      { ticker },
    );

  return response.data;
}

export async function removeWatchlistItem(
  itemId: string,
) {
  const response =
    await api.delete<WatchlistResponse>(
      `/watchlist/items/${itemId}`,
    );

  return response.data;
}

export async function runScreener(
  payload: ScreenerRequest,
) {
  const response =
    await api.post<ScreenerResponse>(
      "/screener",
      payload,
    );

  return response.data;
}