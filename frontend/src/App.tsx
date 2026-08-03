import { useQuery } from "@tanstack/react-query";
import {
  useEffect,
  useState,
} from "react";

import {
  PortfolioResponse,
  getPortfolio,
  getPortfolios,
} from "./api";

import CreatePortfolioForm from "./components/CreatePortfolioForm";
import PortfolioDetails from "./components/PortfolioDetails";

export default function App() {
  const [
    selectedPortfolio,
    setSelectedPortfolio,
  ] = useState<PortfolioResponse | null>(
    null,
  );

  const [
    isCreatingPortfolio,
    setIsCreatingPortfolio,
  ] = useState(false);

  const portfoliosQuery = useQuery({
    queryKey: ["portfolios"],
    queryFn: getPortfolios,
  });

  useEffect(() => {
    async function loadFirstPortfolio() {
      if (
        isCreatingPortfolio ||
        selectedPortfolio ||
        !portfoliosQuery.data?.length
      ) {
        return;
      }

      const firstPortfolio =
        portfoliosQuery.data[0];

      try {
        const portfolio =
          await getPortfolio(firstPortfolio.id);

        setSelectedPortfolio(portfolio);
      } catch (error) {
        console.error(
          "Could not load saved portfolio",
          error,
        );
      }
    }

    void loadFirstPortfolio();
  }, [
    portfoliosQuery.data,
    selectedPortfolio,
    isCreatingPortfolio,
  ]);

  function handlePortfolioCreated(
    portfolio: PortfolioResponse,
  ) {
    setSelectedPortfolio(portfolio);
    setIsCreatingPortfolio(false);
  }

  function openCreatePortfolioScreen() {
    setSelectedPortfolio(null);
    setIsCreatingPortfolio(true);
  }

  if (portfoliosQuery.isLoading) {
    return (
      <main className="shell">
        Loading your portfolios…
      </main>
    );
  }

  return (
    <main className="shell">
      {!selectedPortfolio ? (
        <>
          <header className="app-heading">
            <p className="eyebrow">
              PORTSIGNAL
            </p>

            <h1>
              Understand what your portfolio
              owns, risks and reacts to.
            </h1>

            <p>
              Create a portfolio to begin
              tracking live market value,
              performance and relevant financial
              news.
            </p>
          </header>

          <CreatePortfolioForm
            onPortfolioCreated={
              handlePortfolioCreated
            }
          />
        </>
      ) : (
        <>
          <button
            className="secondary-button back-button"
            type="button"
            onClick={
              openCreatePortfolioScreen
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