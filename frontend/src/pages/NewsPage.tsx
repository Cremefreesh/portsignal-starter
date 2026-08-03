import { useQuery } from "@tanstack/react-query";

import {
  PortfolioResponse,
  getPortfolioNews,
} from "../api";

type Props = {
  portfolio: PortfolioResponse;
};

export default function NewsPage({
  portfolio,
}: Props) {
  const newsQuery = useQuery({
    queryKey: ["portfolio-news", portfolio.id],
    queryFn: () => getPortfolioNews(portfolio.id, 7),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  if (newsQuery.isLoading) {
    return (
      <section className="card loading-card">
        <p className="eyebrow">PORTFOLIO NEWS</p>
        <h2>Finding relevant stories…</h2>
      </section>
    );
  }

  if (newsQuery.isError || !newsQuery.data) {
    return (
      <section className="card error-card">
        <p className="eyebrow">NEWS ERROR</p>
        <h2>News could not be loaded</h2>

        <button
          className="secondary-button"
          type="button"
          onClick={() => newsQuery.refetch()}
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
        <p className="eyebrow">PORTFOLIO NEWS</p>
        <h1>What matters to {portfolio.name}</h1>
        <p>
          Stories ranked by affected portfolio weight
          and freshness.
        </p>
      </header>

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
                  className={`importance-badge ${article.importance}`}
                >
                  {article.importance}
                </span>

                <span>{article.source}</span>

                <span>
                  {new Date(
                    article.published_at,
                  ).toLocaleString("en-GB")}
                </span>
              </div>

              <h2>{article.headline}</h2>

              <p>{article.summary}</p>

              <div className="ticker-badges">
                {article.affected_tickers.map(
                  (ticker) => (
                    <span key={ticker}>{ticker}</span>
                  ),
                )}
              </div>

              <div className="news-impact">
                <strong>
                  {(
                    article.affected_portfolio_weight *
                    100
                  ).toFixed(1)}
                  % of portfolio affected
                </strong>

                <p>{article.why_it_matters}</p>
              </div>

              <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                className="secondary-button article-link"
              >
                Read full story
              </a>
            </div>
          </article>
        ))}
      </section>

      {feed.articles.length === 0 && (
        <section className="card empty-state">
          No relevant stories were found.
        </section>
      )}
    </section>
  );
}