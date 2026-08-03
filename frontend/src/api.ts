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