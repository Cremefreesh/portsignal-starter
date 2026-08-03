import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  timeout: 10_000,
});

export type PortfolioSummary = {
  id: string;
  name: string;
  benchmark_ticker: string;
  base_currency: string;
  total_value: number;
  day_change_pct: number;
  positions_count: number;
};

export type RiskMetrics = {
  annualised_return: number;
  annualised_volatility: number;
  beta: number;
  capm_expected_return: number;
  sharpe_ratio: number | null;
  maximum_drawdown: number;
  historical_var_95: number;
  concentration_hhi: number;
  effective_number_of_holdings: number;
};

export type MarketRegime = {
  score: number;
  label: string;
  as_of: string;
  components: Record<string, number>;
};
