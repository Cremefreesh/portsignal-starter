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