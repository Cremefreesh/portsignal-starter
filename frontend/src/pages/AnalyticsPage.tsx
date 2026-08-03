import { useQuery } from "@tanstack/react-query";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  PortfolioResponse,
  getPortfolioAnalytics,
} from "../api";

type Props = {
  portfolio: PortfolioResponse;
};

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function AnalyticsPage({
  portfolio,
}: Props) {
  const analyticsQuery = useQuery({
    queryKey: ["portfolio-analytics", portfolio.id],
    queryFn: () =>
      getPortfolioAnalytics(portfolio.id),
    staleTime: 60 * 60 * 1000,
    retry: 1,
  });

  if (analyticsQuery.isLoading) {
    return (
      <section className="card loading-card">
        <p className="eyebrow">ANALYTICS</p>
        <h2>Calculating portfolio analytics…</h2>
        <p>
          Historical prices are being loaded and compared
          with {portfolio.benchmark_ticker}.
        </p>
      </section>
    );
  }

  if (
    analyticsQuery.isError ||
    !analyticsQuery.data
  ) {
    return (
      <section className="card error-card">
        <p className="eyebrow">ANALYTICS ERROR</p>
        <h2>Analytics could not be calculated</h2>

        <button
          className="secondary-button"
          type="button"
          onClick={() => analyticsQuery.refetch()}
        >
          Try again
        </button>
      </section>
    );
  }

  const analytics = analyticsQuery.data;

  return (
    <section>
      <header className="page-heading">
        <p className="eyebrow">PORTFOLIO ANALYTICS</p>
        <h1>{portfolio.name}</h1>
        <p>
          Based on {analytics.observation_count} daily
          observations from {analytics.start_date} to{" "}
          {analytics.end_date}.
        </p>
      </header>

      <section className="analytics-grid">
        <Metric
          label="Annualised return"
          value={formatPercent(
            analytics.annualised_return,
          )}
        />

        <Metric
          label="Annualised volatility"
          value={formatPercent(
            analytics.annualised_volatility,
          )}
        />

        <Metric
          label="Beta"
          value={analytics.beta.toFixed(2)}
        />

        <Metric
          label="CAPM return"
          value={formatPercent(
            analytics.capm_expected_return,
          )}
        />

        <Metric
          label="Sharpe ratio"
          value={
            analytics.sharpe_ratio?.toFixed(2) ?? "—"
          }
        />

        <Metric
          label="Sortino ratio"
          value={
            analytics.sortino_ratio?.toFixed(2) ?? "—"
          }
        />

        <Metric
          label="Maximum drawdown"
          value={formatPercent(
            analytics.maximum_drawdown,
          )}
        />

        <Metric
          label="Daily VaR 95%"
          value={formatPercent(
            analytics.historical_var_95,
          )}
        />

        <Metric
          label="Effective holdings"
          value={analytics.effective_holdings.toFixed(
            1,
          )}
        />

        <Metric
          label="Largest position"
          value={formatPercent(
            analytics.largest_position_weight,
          )}
        />
      </section>

      <article className="card analytics-chart-card">
        <div>
          <p className="eyebrow">PORTFOLIO HISTORY</p>
          <h2>Historical value</h2>
        </div>

        <div className="analytics-chart">
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={analytics.history}>
              <XAxis
                dataKey="date"
                tickFormatter={(value) =>
                  new Date(value).toLocaleDateString(
                    "en-GB",
                    {
                      month: "short",
                      day: "numeric",
                    },
                  )
                }
              />

              <YAxis
                tickFormatter={(value) =>
                  formatMoney(value)
                }
              />

              <Tooltip
                formatter={(value) =>
                  formatMoney(Number(value))
                }
                labelFormatter={(value) =>
                  new Date(value).toLocaleDateString(
                    "en-GB",
                  )
                }
              />

              <Line
                type="monotone"
                dataKey="portfolio_value"
                stroke="#c7c9cf"
                strokeWidth={3}
                dot={false}
                />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </article>

      {analytics.warnings.length > 0 && (
        <section className="warning-panel">
          {analytics.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </section>
      )}
    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <article className="card analytics-metric">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}