import { PortfolioValuation } from "../api";

type Props = {
  valuation: PortfolioValuation;
};

type AllocationItem = {
  ticker: string;
  marketValue: number;
  weight: number;
};

function formatMoney(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

export default function PortfolioAllocation({
  valuation,
}: Props) {
  const allocation: AllocationItem[] =
    valuation.positions
      .map((position) => ({
        ticker: position.ticker,
        marketValue: position.market_value,
        weight:
          valuation.total_market_value > 0
            ? position.market_value /
              valuation.total_market_value
            : 0,
      }))
      .sort((a, b) => b.weight - a.weight);

  const largestHolding = allocation[0];

  const concentrationScore = allocation.reduce(
    (total, holding) =>
      total + holding.weight ** 2,
    0,
  );

  const effectiveHoldings =
    concentrationScore > 0
      ? 1 / concentrationScore
      : 0;

  function concentrationLabel() {
    if (
      !largestHolding ||
      largestHolding.weight < 0.2
    ) {
      return "Low";
    }

    if (largestHolding.weight < 0.35) {
      return "Moderate";
    }

    return "High";
  }

  return (
    <section className="allocation-layout">
      <article className="card allocation-card">
        <div className="allocation-heading">
          <div>
            <p className="eyebrow">
              PORTFOLIO ALLOCATION
            </p>

            <h2>Position weights</h2>
          </div>

          <span className="allocation-total">
            {formatMoney(
              valuation.total_market_value,
              valuation.valuation_currency,
            )}
          </span>
        </div>

        <div className="allocation-list">
          {allocation.map((holding) => (
            <div
              className="allocation-row"
              key={holding.ticker}
            >
              <div className="allocation-row-heading">
                <strong>{holding.ticker}</strong>

                <span>
                  {(holding.weight * 100).toFixed(
                    1,
                  )}
                  %
                </span>
              </div>

              <div className="allocation-track">
                <div
                  className="allocation-fill"
                  style={{
                    width: `${Math.max(
                      holding.weight * 100,
                      1,
                    )}%`,
                  }}
                />
              </div>

              <small>
                {formatMoney(
                  holding.marketValue,
                    valuation.valuation_currency,
                )}
              </small>
            </div>
          ))}
        </div>
      </article>

      <aside className="allocation-stat-grid">
        <article className="card allocation-stat-card">
          <p>Largest holding</p>

          <strong>
            {largestHolding?.ticker ?? "—"}
          </strong>

          <span>
            {largestHolding
              ? `${(
                  largestHolding.weight * 100
                ).toFixed(1)}%`
              : "—"}
          </span>
        </article>

        <article className="card allocation-stat-card">
          <p>Effective holdings</p>

          <strong>
            {effectiveHoldings.toFixed(1)}
          </strong>

          <span>
            Across {allocation.length} positions
          </span>
        </article>

        <article className="card allocation-stat-card">
          <p>Concentration</p>

          <strong>{concentrationLabel()}</strong>

          <span>
            HHI {concentrationScore.toFixed(3)}
          </span>
        </article>
      </aside>
    </section>
  );
}