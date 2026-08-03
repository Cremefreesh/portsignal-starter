import { PortfolioResponse } from "../api";

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
  }).format(value);
}

export default function PortfolioDetails({
  portfolio,
}: Props) {
  const totalCost = portfolio.positions.reduce(
    (total, position) =>
      total +
      position.quantity * position.average_cost,
    0,
  );

  return (
    <section className="portfolio-details">
      <header className="portfolio-header card">
        <div>
          <p className="eyebrow">PORTFOLIO</p>
          <h1>{portfolio.name}</h1>
        </div>

        <div className="portfolio-header-stats">
          <span>
            {portfolio.positions.length} holdings
          </span>

          <span>
            Benchmark: {portfolio.benchmark_ticker}
          </span>
        </div>
      </header>

      <article className="card portfolio-total">
        <p>Total acquisition cost</p>

        <strong>
          {formatMoney(
            totalCost,
            portfolio.base_currency,
          )}
        </strong>

        <small>
          This is currently based on average purchase
          costs, not live market prices.
        </small>
      </article>

      <section className="card holdings-table-card">
        <div className="holdings-heading">
          <div>
            <p className="eyebrow">HOLDINGS</p>
            <h2>Your positions</h2>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Quantity</th>
                <th>Average cost</th>
                <th>Cost value</th>
              </tr>
            </thead>

            <tbody>
              {portfolio.positions.map((position) => {
                const costValue =
                  position.quantity *
                  position.average_cost;

                return (
                  <tr key={position.id}>
                    <td>
                      <strong>{position.ticker}</strong>
                    </td>

                    <td>{position.quantity}</td>

                    <td>
                      {formatMoney(
                        position.average_cost,
                        position.currency,
                      )}
                    </td>

                    <td>
                      {formatMoney(
                        costValue,
                        position.currency,
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}