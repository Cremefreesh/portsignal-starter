import { PortfolioSummary } from "../api";

type Props = {
  portfolios: PortfolioSummary[];
  selectedPortfolioId: string | null;
  isLoading: boolean;
  onSelect: (portfolioId: string) => void;
  onCreateNew: () => void;
};

export default function PortfolioSelector({
  portfolios,
  selectedPortfolioId,
  isLoading,
  onSelect,
  onCreateNew,
}: Props) {
  return (
    <nav className="portfolio-selector card">
      <div className="portfolio-selector-copy">
        <p className="eyebrow">ACTIVE PORTFOLIO</p>

        <select
          value={selectedPortfolioId ?? ""}
          disabled={isLoading}
          onChange={(event) =>
            onSelect(event.target.value)
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
        onClick={onCreateNew}
      >
        New portfolio
      </button>
    </nav>
  );
}