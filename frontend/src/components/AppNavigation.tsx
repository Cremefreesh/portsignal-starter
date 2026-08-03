import { NavLink } from "react-router-dom";

import { PortfolioSummary } from "../api";

type Props = {
  portfolios: PortfolioSummary[];
  selectedPortfolioId: string | null;
  isLoading: boolean;
  onSelectPortfolio: (portfolioId: string) => void;
  onCreatePortfolio: () => void;
};

export default function AppNavigation({
  portfolios,
  selectedPortfolioId,
  isLoading,
  onSelectPortfolio,
  onCreatePortfolio,
}: Props) {
  return (
    <header className="top-navigation card">
      <div className="top-navigation-left">
        <div className="brand-block">
          <p className="eyebrow">PORTSIGNAL</p>
          <strong>Portfolio intelligence</strong>
        </div>

        <div className="portfolio-switcher">
          <label htmlFor="portfolio-select">
            Current portfolio
          </label>

          <select
            id="portfolio-select"
            value={selectedPortfolioId ?? ""}
            disabled={isLoading}
            onChange={(event) =>
              onSelectPortfolio(event.target.value)
            }
          >
            {portfolios.map((portfolio) => (
              <option
                key={portfolio.id}
                value={portfolio.id}
              >
                {portfolio.name}
              </option>
            ))}
          </select>
        </div>

        <button
          className="secondary-button"
          type="button"
          onClick={onCreatePortfolio}
        >
          New portfolio
        </button>
      </div>

      <nav className="navigation-links">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive
              ? "nav-link active"
              : "nav-link"
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive
              ? "nav-link active"
              : "nav-link"
          }
        >
          Analytics
        </NavLink>

        <NavLink
          to="/news"
          className={({ isActive }) =>
            isActive
              ? "nav-link active"
              : "nav-link"
          }
        >
          News
        </NavLink>
      </nav>
    </header>
  );
}