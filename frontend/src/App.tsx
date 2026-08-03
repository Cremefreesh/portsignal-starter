import { useState } from "react";
import {
  PortfolioResponse,
} from "./api";
import CreatePortfolioForm from "./components/CreatePortfolioForm";
import PortfolioDetails from "./components/PortfolioDetails";

export default function App() {
  const [
    selectedPortfolio,
    setSelectedPortfolio,
  ] = useState<PortfolioResponse | null>(null);

  return (
    <main className="shell">
      {!selectedPortfolio ? (
        <>
          <header className="app-heading">
            <p className="eyebrow">PORTSIGNAL</p>

            <h1>
              Understand what your portfolio owns,
              risks and reacts to.
            </h1>

            <p>
              Build your portfolio first. Market data,
              analytics and personalised news will be
              added on top of these holdings.
            </p>
          </header>

          <CreatePortfolioForm
            onPortfolioCreated={setSelectedPortfolio}
          />
        </>
      ) : (
        <>
          <button
            className="secondary-button back-button"
            type="button"
            onClick={() =>
              setSelectedPortfolio(null)
            }
          >
            Create another portfolio
          </button>

          <PortfolioDetails
            portfolio={selectedPortfolio}
          />
        </>
      )}
    </main>
  );
}