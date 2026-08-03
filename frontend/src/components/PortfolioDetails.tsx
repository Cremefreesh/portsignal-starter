import { useQuery } from "@tanstack/react-query";
import {
  PortfolioResponse,
  getPortfolioValuation,
} from "../api";

type Props = {
  portfolio: PortfolioResponse;
};

function formatMoney(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(
  value: number | null,
) {
  if (value === null) {
    return "—";
  }

  const prefix = value > 0 ? "+" : "";

  return `${prefix}${value.toFixed(2)}%`;
}

function getChangeClass(value: number) {
  if (value > 0) {
    return "positive-value";
  }

  if (value < 0) {
    return "negative-value";
  }

  return "neutral-value";
}

export default function PortfolioDetails({
  portfolio,
}: Props) {
  const valuationQuery = useQuery({
    queryKey: [
      "portfolio-valuation",
      portfolio.id,
    ],
    queryFn: () =>
      getPortfolioValuation(portfolio.id),

    refetchInterval: 60_000,
    staleTime: 45_000,
    retry: 1,
  });

  if (valuationQuery.isLoading) {
    return (
      <section className="card loading-card">
        <p className="eyebrow">
          LIVE MARKET DATA
        </p>

        <h2>Valuing your portfolio…</h2>

        <p>
          Retrieving the latest prices for your
          holdings.
        </p>
      </section>
    );
  }

  if (
    valuationQuery.isError ||
    !valuationQuery.data
  ) {
    return (
      <section className="card error-card">
        <p className="eyebrow">
          MARKET DATA ERROR
        </p>

        <h2>
          We could not value this portfolio
        </h2>

        <p>
          Check that Finnhub is available and that
          your holdings use valid US ticker symbols.
        </p>

        <button
          className="secondary-button"
          type="button"
          onClick={() =>
            valuationQuery.refetch()
          }
        >
          Try again
        </button>
      </section>
    );
  }

  const valuation = valuationQuery.data;

  return (
    <section className="portfolio-details">
      <header className="portfolio-header card">
        <div>
          <p className="eyebrow">
            LIVE PORTFOLIO
          </p>

          <h1>{portfolio.name}</h1>
        </div>

        <div className="portfolio-header-stats">
          <span>
            {valuation.positions.length} valued
            holdings
          </span>

          <span>
            Benchmark:{" "}
            {portfolio.benchmark_ticker}
          </span>

          <span>
            Updated automatically
          </span>
        </div>
      </header>

      <section className="portfolio-summary-grid">
        <article className="card summary-card primary-summary">
          <p>Current portfolio value</p>

          <strong>
            {formatMoney(
              valuation.total_market_value,
              valuation.valuation_currency,
            )}
          </strong>

          <div
            className={getChangeClass(
              valuation.total_day_change,
            )}
          >
            {formatMoney(
              valuation.total_day_change,
              valuation.valuation_currency,
            )}

            {" · "}

            {formatPercent(
              valuation.total_day_change_percent,
            )}

            {" today"}
          </div>
        </article>

        <article className="card summary-card">
          <p>Total gain/loss</p>

          <strong
            className={getChangeClass(
              valuation.total_gain,
            )}
          >
            {formatMoney(
              valuation.total_gain,
              valuation.valuation_currency,
            )}
          </strong>

          <span
            className={getChangeClass(
              valuation.total_gain,
            )}
          >
            {formatPercent(
              valuation.total_gain_percent,
            )}
          </span>
        </article>

        <article className="card summary-card">
          <p>Total cost basis</p>

          <strong>
            {formatMoney(
              valuation.total_cost_basis,
              valuation.valuation_currency,
            )}
          </strong>

          <span className="summary-note">
            Based on your entered average costs
          </span>
        </article>
      </section>

      {valuation.warnings.length > 0 && (
        <section className="warning-panel">
          <strong>
            Some holdings were not included
          </strong>

          {valuation.warnings.map(
            (warning) => (
              <p key={warning}>{warning}</p>
            ),
          )}
        </section>
      )}

      <section className="card holdings-table-card">
        <div className="holdings-heading">
          <div>
            <p className="eyebrow">
              LIVE HOLDINGS
            </p>

            <h2>Your positions</h2>
          </div>

          <button
            className="secondary-button"
            type="button"
            disabled={
              valuationQuery.isFetching
            }
            onClick={() =>
              valuationQuery.refetch()
            }
          >
            {valuationQuery.isFetching
              ? "Refreshing…"
              : "Refresh prices"}
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Quantity</th>
                <th>Average cost</th>
                <th>Current price</th>
                <th>Market value</th>
                <th>Today</th>
                <th>Total return</th>
              </tr>
            </thead>

            <tbody>
              {valuation.positions.map(
                (position) => (
                  <tr
                    key={position.position_id}
                  >
                    <td>
                      <strong className="ticker-symbol">
                        {position.ticker}
                      </strong>
                    </td>

                    <td>
                      {position.quantity}
                    </td>

                    <td>
                      {formatMoney(
                        position.average_cost,
                        position.currency,
                      )}
                    </td>

                    <td>
                      {formatMoney(
                        position.current_price,
                        position.currency,
                      )}
                    </td>

                    <td>
                      <strong>
                        {formatMoney(
                          position.market_value,
                          position.currency,
                        )}
                      </strong>
                    </td>

                    <td>
                      <div
                        className={getChangeClass(
                          position.day_change,
                        )}
                      >
                        {formatMoney(
                          position.day_change,
                          position.currency,
                        )}
                      </div>

                      <small
                        className={getChangeClass(
                          position.day_change_percent,
                        )}
                      >
                        {formatPercent(
                          position.day_change_percent,
                        )}
                      </small>
                    </td>

                    <td>
                      <div
                        className={getChangeClass(
                          position.total_gain,
                        )}
                      >
                        {formatMoney(
                          position.total_gain,
                          position.currency,
                        )}
                      </div>

                      <small
                        className={getChangeClass(
                          position.total_gain,
                        )}
                      >
                        {formatPercent(
                          position.total_gain_percent,
                        )}
                      </small>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}