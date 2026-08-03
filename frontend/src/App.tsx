import { useQuery } from "@tanstack/react-query";
import { Activity, Bell, Newspaper, ShieldCheck } from "lucide-react";
import { api, MarketRegime, PortfolioSummary, RiskMetrics } from "./api";

const percent = (value: number) =>
  new Intl.NumberFormat("en-GB", {
    style: "percent",
    maximumFractionDigits: 2,
  }).format(value);

const money = (value: number, currency: string) =>
  new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
  }).format(value);

function MetricCard({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <article className="card metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

export default function App() {
  const portfolios = useQuery({
    queryKey: ["portfolios"],
    queryFn: async () =>
      (await api.get<PortfolioSummary[]>("/portfolios")).data,
  });

  const portfolio = portfolios.data?.[0];

  const risk = useQuery({
    queryKey: ["risk", portfolio?.id],
    enabled: Boolean(portfolio),
    queryFn: async () =>
      (await api.get<RiskMetrics>(`/portfolios/${portfolio!.id}/risk`)).data,
  });

  const regime = useQuery({
    queryKey: ["market-regime", portfolio?.id],
    enabled: Boolean(portfolio),
    queryFn: async () =>
      (
        await api.get<MarketRegime>(
          `/portfolios/${portfolio!.id}/market-regime`,
        )
      ).data,
  });

  if (portfolios.isLoading) {
    return <main className="shell">Loading PortSignal…</main>;
  }

  if (!portfolio || portfolios.isError) {
    return <main className="shell">Unable to load the portfolio.</main>;
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">PORTSIGNAL</p>
          <h1>{portfolio.name}</h1>
        </div>
        <button className="icon-button" aria-label="Notifications">
          <Bell size={20} />
        </button>
      </header>

      <section className="hero card">
        <div>
          <p>Total portfolio value</p>
          <h2>{money(portfolio.total_value, portfolio.base_currency)}</h2>
          <span className="positive">
            +{portfolio.day_change_pct.toFixed(2)}% today
          </span>
        </div>
        <div className="hero-meta">
          <span>{portfolio.positions_count} holdings</span>
          <span>Benchmark: {portfolio.benchmark_ticker}</span>
        </div>
      </section>

      <section className="section-heading">
        <div>
          <p className="eyebrow">RISK LAB</p>
          <h2>Portfolio health</h2>
        </div>
        <ShieldCheck />
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Annualised return"
          value={risk.data ? percent(risk.data.annualised_return) : "—"}
          note="Historical estimate"
        />
        <MetricCard
          label="Volatility"
          value={risk.data ? percent(risk.data.annualised_volatility) : "—"}
          note="Annualised standard deviation"
        />
        <MetricCard
          label="Portfolio beta"
          value={risk.data ? risk.data.beta.toFixed(2) : "—"}
          note={`Relative to ${portfolio.benchmark_ticker}`}
        />
        <MetricCard
          label="CAPM return"
          value={risk.data ? percent(risk.data.capm_expected_return) : "—"}
          note="Assumption-based estimate"
        />
        <MetricCard
          label="Sharpe ratio"
          value={risk.data?.sharpe_ratio?.toFixed(2) ?? "—"}
          note="Risk-adjusted return"
        />
        <MetricCard
          label="Maximum drawdown"
          value={risk.data ? percent(risk.data.maximum_drawdown) : "—"}
          note="Worst peak-to-trough fall"
        />
      </section>

      <section className="two-column">
        <article className="card regime-card">
          <div className="card-title">
            <Activity />
            <div>
              <p className="eyebrow">MARKET REGIME</p>
              <h2>Fear & greed</h2>
            </div>
          </div>

          <div className="regime-score">
            <strong>{regime.data?.score ?? "—"}</strong>
            <span>{regime.data?.label ?? "Loading"}</span>
          </div>

          <div className="meter">
            <div
              className="meter-fill"
              style={{ width: `${regime.data?.score ?? 0}%` }}
            />
          </div>

          <p className="muted">
            An explainable composite of momentum, volatility, credit,
            safe-haven demand and market breadth.
          </p>
        </article>

        <article className="card">
          <div className="card-title">
            <Newspaper />
            <div>
              <p className="eyebrow">PORTFOLIO NEWS</p>
              <h2>What matters today</h2>
            </div>
          </div>

          <div className="news-item">
            <span className="importance">HIGH RELEVANCE</span>
            <h3>Example portfolio-relevant market story</h3>
            <p>
              Affected holdings represent 44% of this portfolio. Live news
              ingestion is the next integration.
            </p>
          </div>
        </article>
      </section>

      <footer>
        Analytics are informational and do not constitute investment advice.
      </footer>
    </main>
  );
}
