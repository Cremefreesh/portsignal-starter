import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import {
  PortfolioResponse,
  getPortfolioNews,
} from "../api";

type Props = {
  portfolio: PortfolioResponse;
};

const categories = [
  { value: "all", label: "All events" },
  { value: "earnings", label: "Earnings" },
  { value: "product", label: "Products" },
  {
    value: "regulation",
    label: "Regulation",
  },
  {
    value: "analyst_rating",
    label: "Analyst ratings",
  },
  {
    value: "merger_acquisition",
    label: "M&A",
  },
];

export default function NewsPage({
  portfolio,
}: Props) {
  const [days, setDays] = useState(7);

  const [
    importantOnly,
    setImportantOnly,
  ] = useState(true);

  const [category, setCategory] =
    useState("all");

  const newsQuery = useQuery({
    queryKey: [
      "portfolio-news",
      portfolio.id,
      days,
      importantOnly,
      category,
    ],
    queryFn: () =>
      getPortfolioNews(
        portfolio.id,
        days,
        importantOnly,
        category,
      ),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  if (newsQuery.isLoading) {
    return (
      <section className="card loading-card">
        <p className="eyebrow">
          PORTFOLIO NEWS
        </p>

        <h2>
          Finding material stories…
        </h2>
      </section>
    );
  }

  if (
    newsQuery.isError ||
    !newsQuery.data
  ) {
    return (
      <section className="card error-card">
        <p className="eyebrow">
          NEWS ERROR
        </p>

        <h2>
          News could not be loaded
        </h2>

        <button
          className="secondary-button"
          type="button"
          onClick={() =>
            newsQuery.refetch()
          }
        >
          Try again
        </button>
      </section>
    );
  }

  const feed = newsQuery.data;

  return (
    <section>
      <header className="page-heading">
        <p className="eyebrow">
          PORTFOLIO NEWS
        </p>

        <h1>
          What matters to {portfolio.name}
        </h1>

        <p>
          Duplicate stories are grouped and
          ranked by evidence, portfolio exposure
          and freshness.
        </p>
      </header>

      <section className="card news-brief">
        <div>
          <p className="eyebrow">
            PORTFOLIO BRIEF
          </p>

          <h2>{feed.brief.summary}</h2>
        </div>

        <div className="brief-stat">
          <strong>
            {(
              feed.brief
                .affected_portfolio_weight *
              100
            ).toFixed(1)}
            %
          </strong>

          <span>
            materially affected
          </span>
        </div>
      </section>

      <section className="card news-controls">
        <label>
          Time period

          <select
            value={days}
            onChange={(event) =>
              setDays(
                Number(
                  event.target.value,
                ),
              )
            }
          >
            <option value={1}>
              Last 24 hours
            </option>

            <option value={7}>
              Last 7 days
            </option>

            <option value={30}>
              Last 30 days
            </option>
          </select>
        </label>

        <label>
          Event category

          <select
            value={category}
            onChange={(event) =>
              setCategory(
                event.target.value,
              )
            }
          >
            {categories.map(
              (option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ),
            )}
          </select>
        </label>

        <label className="checkbox-control">
          <input
            type="checkbox"
            checked={importantOnly}
            onChange={(event) =>
              setImportantOnly(
                event.target.checked,
              )
            }
          />

          Important stories only
        </label>
      </section>

      <section className="news-grid">
        {feed.articles.map((article) => (
          <article
            className="card news-card"
            key={article.id}
          >
            {article.image_url && (
              <img
                src={article.image_url}
                alt=""
                className="news-image"
              />
            )}

            <div className="news-card-body">
              <div className="news-card-meta">
                <span
                  className={
                    `importance-badge ` +
                    article.importance
                  }
                >
                  {article.importance}
                </span>

                <span className="category-badge">
                  {article.category.replace(
                    "_",
                    " ",
                  )}
                </span>

                <span>
                  {article.source}
                </span>

                <span>
                  {new Date(
                    article.published_at,
                  ).toLocaleString(
                    "en-GB",
                  )}
                </span>
              </div>

              <h2>{article.headline}</h2>

              <p>{article.summary}</p>

              {article.duplicate_count > 1 && (
                <p className="duplicate-note">
                  Grouped from{" "}
                  {article.duplicate_count} similar
                  reports
                </p>
              )}

              <div className="ticker-badges">
                {article.affected_tickers.map(
                  (ticker) => (
                    <span key={ticker}>
                      {ticker}
                    </span>
                  ),
                )}
              </div>

              <div className="news-impact">
                <strong>
                  {(
                    article
                      .affected_portfolio_weight *
                    100
                  ).toFixed(1)}
                  % of portfolio affected
                </strong>

                <p>
                  {article.why_it_matters}
                </p>
              </div>

              <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                className={
                  "secondary-button article-link"
                }
              >
                Read full story
              </a>
            </div>
          </article>
        ))}
      </section>

      {feed.articles.length === 0 && (
        <section className="card empty-state">
          No stories met the selected relevance
          threshold.
        </section>
      )}
    </section>
  );
}