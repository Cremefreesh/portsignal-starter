import { FormEvent, useState } from "react";
import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  ScreenerRequest,
  ScreenerResponse,
  addWatchlistTicker,
  runScreener,
} from "../api";

const DEFAULT_TICKERS =
  "AAPL, MSFT, NVDA, AMD, META, GOOGL, AMZN";

function optionalNumber(value: string) {
  if (value.trim() === "") {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : null;
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatMarketCap(
  millions: number | null,
) {
  if (millions === null) {
    return "—";
  }

  if (millions >= 1_000_000) {
    return `$${(
      millions / 1_000_000
    ).toFixed(2)}T`;
  }

  if (millions >= 1_000) {
    return `$${(millions / 1_000).toFixed(1)}B`;
  }

  return `$${millions.toFixed(0)}M`;
}

export default function ScreenerPage() {
  const [tickers, setTickers] =
    useState(DEFAULT_TICKERS);

  const [minimumPrice, setMinimumPrice] =
    useState("");

  const [maximumPrice, setMaximumPrice] =
    useState("");

  const [minimumMarketCap, setMinimumMarketCap] =
    useState("");

  const [maximumPe, setMaximumPe] =
    useState("");

  const [minimumDailyChange, setMinimumDailyChange] =
    useState("");

  const [industry, setIndustry] = useState("");

  const [results, setResults] =
    useState<ScreenerResponse | null>(null);

  const queryClient = useQueryClient();

  const screenerMutation = useMutation({
    mutationFn: runScreener,

    onSuccess: setResults,
  });

  const watchlistMutation = useMutation({
    mutationFn: addWatchlistTicker,

    onSuccess: (watchlist) => {
      queryClient.setQueryData(
        ["watchlist"],
        watchlist,
      );
    },
  });

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const request: ScreenerRequest = {
      tickers: tickers
        .split(",")
        .map((ticker) =>
          ticker.trim().toUpperCase(),
        )
        .filter(Boolean),

      minimum_price:
        optionalNumber(minimumPrice),

      maximum_price:
        optionalNumber(maximumPrice),

      minimum_market_cap:
        optionalNumber(minimumMarketCap),

      maximum_pe:
        optionalNumber(maximumPe),

      minimum_daily_change:
        optionalNumber(minimumDailyChange),

      industry:
        industry.trim() || null,
    };

    screenerMutation.mutate(request);
  }

  return (
    <section>
      <header className="page-heading">
        <p className="eyebrow">STOCK SCREENER</p>
        <h1>Compare selected companies</h1>

        <p>
          Screen a manageable group of stocks by
          price, market capitalisation, valuation
          and industry.
        </p>
      </header>

      <form
        className="card screener-form"
        onSubmit={handleSubmit}
      >
        <label className="screener-tickers">
          Tickers separated by commas

          <textarea
            value={tickers}
            rows={3}
            onChange={(event) =>
              setTickers(event.target.value)
            }
          />
        </label>

        <div className="screener-filter-grid">
          <label>
            Minimum price

            <input
              type="number"
              min="0"
              step="any"
              value={minimumPrice}
              onChange={(event) =>
                setMinimumPrice(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Maximum price

            <input
              type="number"
              min="0"
              step="any"
              value={maximumPrice}
              onChange={(event) =>
                setMaximumPrice(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Minimum market cap (£m/USD m)

            <input
              type="number"
              min="0"
              step="any"
              value={minimumMarketCap}
              onChange={(event) =>
                setMinimumMarketCap(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Maximum P/E

            <input
              type="number"
              min="0"
              step="any"
              value={maximumPe}
              onChange={(event) =>
                setMaximumPe(event.target.value)
              }
            />
          </label>

          <label>
            Minimum daily change %

            <input
              type="number"
              step="any"
              value={minimumDailyChange}
              onChange={(event) =>
                setMinimumDailyChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Industry contains

            <input
              value={industry}
              placeholder="Technology"
              onChange={(event) =>
                setIndustry(event.target.value)
              }
            />
          </label>
        </div>

        <button
          className="primary-button"
          type="submit"
          disabled={screenerMutation.isPending}
        >
          {screenerMutation.isPending
            ? "Screening companies…"
            : "Run screener"}
        </button>
      </form>

      {screenerMutation.isError && (
        <section className="card error-card">
          <h2>The screener could not be run</h2>

          <p>
            Try fewer tickers in case the market
            data provider has rate-limited the
            request.
          </p>
        </section>
      )}

      {results && (
        <section className="card screener-results">
          <div className="holdings-heading">
            <div>
              <p className="eyebrow">
                SCREENER RESULTS
              </p>

              <h2>
                {results.results.length} matching
                companies
              </h2>
            </div>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Price</th>
                  <th>Today</th>
                  <th>Market cap</th>
                  <th>P/E</th>
                  <th>Dividend</th>
                  <th>Industry</th>
                  <th />
                </tr>
              </thead>

              <tbody>
                {results.results.map((result) => (
                  <tr key={result.ticker}>
                    <td>
                      <div className="screener-company">
                        {result.logo_url && (
                          <img
                            src={result.logo_url}
                            alt=""
                            className="company-logo small"
                          />
                        )}

                        <div>
                          <strong>
                            {result.ticker}
                          </strong>

                          <small>
                            {result.company_name}
                          </small>
                        </div>
                      </div>
                    </td>

                    <td>
                      {formatMoney(
                        result.current_price,
                      )}
                    </td>

                    <td
                      className={
                        result.daily_change_percent >= 0
                          ? "positive-value"
                          : "negative-value"
                      }
                    >
                      {result.daily_change_percent > 0
                        ? "+"
                        : ""}
                      {result.daily_change_percent.toFixed(
                        2,
                      )}
                      %
                    </td>

                    <td>
                      {formatMarketCap(
                        result.market_cap_millions,
                      )}
                    </td>

                    <td>
                      {result.pe_ratio?.toFixed(2) ??
                        "—"}
                    </td>

                    <td>
                      {result.dividend_yield_percent !==
                      null
                        ? `${result.dividend_yield_percent.toFixed(
                            2,
                          )}%`
                        : "—"}
                    </td>

                    <td>
                      {result.industry ?? "—"}
                    </td>

                    <td>
                      <button
                        className="secondary-button compact-button"
                        type="button"
                        disabled={
                          watchlistMutation.isPending
                        }
                        onClick={() =>
                          watchlistMutation.mutate(
                            result.ticker,
                          )
                        }
                      >
                        Watch
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.results.length === 0 && (
            <div className="empty-state">
              No stocks matched the selected
              filters.
            </div>
          )}
        </section>
      )}
    </section>
  );
}