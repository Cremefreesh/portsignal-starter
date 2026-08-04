import { FormEvent, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  addWatchlistTicker,
  getWatchlist,
  removeWatchlistItem,
} from "../api";

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function changeClass(value: number) {
  if (value > 0) {
    return "positive-value";
  }

  if (value < 0) {
    return "negative-value";
  }

  return "neutral-value";
}

export default function WatchlistPage() {
  const [ticker, setTicker] = useState("");
  const [formError, setFormError] =
    useState<string | null>(null);

  const queryClient = useQueryClient();

  const watchlistQuery = useQuery({
    queryKey: ["watchlist"],
    queryFn: getWatchlist,
    staleTime: 60_000,
  });

  const addMutation = useMutation({
    mutationFn: addWatchlistTicker,

    onSuccess: (watchlist) => {
      queryClient.setQueryData(
        ["watchlist"],
        watchlist,
      );

      setTicker("");
      setFormError(null);
    },

    onError: (error) => {
      console.error(error);

      setFormError(
        "That ticker could not be added. Check that it is a valid US ticker.",
      );
    },
  });

  const removeMutation = useMutation({
    mutationFn: removeWatchlistItem,

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

    const cleanTicker = ticker.trim().toUpperCase();

    if (!cleanTicker) {
      return;
    }

    addMutation.mutate(cleanTicker);
  }

  if (watchlistQuery.isLoading) {
    return (
      <section className="card loading-card">
        <p className="eyebrow">WATCHLIST</p>
        <h2>Loading your watchlist…</h2>
      </section>
    );
  }

  if (
    watchlistQuery.isError ||
    !watchlistQuery.data
  ) {
    return (
      <section className="card error-card">
        <p className="eyebrow">WATCHLIST ERROR</p>
        <h2>Your watchlist could not be loaded</h2>

        <button
          className="secondary-button"
          type="button"
          onClick={() => watchlistQuery.refetch()}
        >
          Try again
        </button>
      </section>
    );
  }

  const watchlist = watchlistQuery.data;

  return (
    <section>
      <header className="page-heading">
        <p className="eyebrow">WATCHLIST</p>
        <h1>Companies you are following</h1>

        <p>
          Monitor live prices without adding the
          company to one of your portfolios.
        </p>
      </header>

      <form
        className="card watchlist-add-form"
        onSubmit={handleSubmit}
      >
        <label>
          Add a ticker

          <input
            value={ticker}
            placeholder="AAPL"
            maxLength={20}
            onChange={(event) =>
              setTicker(
                event.target.value.toUpperCase(),
              )
            }
          />
        </label>

        <button
          className="primary-button"
          type="submit"
          disabled={
            addMutation.isPending ||
            ticker.trim().length === 0
          }
        >
          {addMutation.isPending
            ? "Adding…"
            : "Add to watchlist"}
        </button>
      </form>

      {formError && (
        <p className="form-error">{formError}</p>
      )}

      {watchlist.warnings.length > 0 && (
        <section className="warning-panel">
          {watchlist.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </section>
      )}

      <section className="watchlist-grid">
        {watchlist.items.map((item) => (
          <article
            className="card watchlist-card"
            key={item.id}
          >
            <div className="watchlist-company">
              {item.logo_url && (
                <img
                  src={item.logo_url}
                  alt=""
                  className="company-logo"
                />
              )}

              <div>
                <strong>{item.ticker}</strong>
                <span>{item.company_name}</span>
              </div>
            </div>

            <div className="watchlist-price">
              <strong>
                {formatMoney(item.current_price)}
              </strong>

              <span
                className={changeClass(
                  item.change_percent,
                )}
              >
                {item.change_percent > 0 ? "+" : ""}
                {item.change_percent.toFixed(2)}%
              </span>
            </div>

            <div className="watchlist-card-footer">
              <span>
                {item.industry ?? "Industry unavailable"}
              </span>

              <button
                className="remove-button"
                type="button"
                disabled={removeMutation.isPending}
                onClick={() =>
                  removeMutation.mutate(item.id)
                }
              >
                Remove
              </button>
            </div>
          </article>
        ))}
      </section>

      {watchlist.items.length === 0 && (
        <section className="card empty-state">
          Your watchlist is empty. Add a ticker
          above to begin tracking it.
        </section>
      )}
    </section>
  );
}