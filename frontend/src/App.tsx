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
import WatchlistPage from "./pages/WatchlistPage";
import ScreenerPage from "./pages/ScreenerPage";


import {
  Route,
  Routes,
} from "react-router-dom";

import AppNavigation from "./components/AppNavigation";
import AnalyticsPage from "./pages/AnalyticsPage";
import NewsPage from "./pages/NewsPage";


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

  const [
    isLoadingPortfolio,
    setIsLoadingPortfolio,
  ] = useState(false);

  const portfoliosQuery = useQuery({
    queryKey: ["portfolios"],
    queryFn: getPortfolios,
  });

  async function selectPortfolio(
    portfolioId: string,
  ) {
    setIsCreatingPortfolio(false);
    setIsLoadingPortfolio(true);

    try {
      const portfolio =
        await getPortfolio(portfolioId);

      setSelectedPortfolio(portfolio);
    } catch (error) {
      console.error(
        "Could not load portfolio",
        error,
      );
    } finally {
      setIsLoadingPortfolio(false);
    }
  }

  useEffect(() => {
    if (
      isCreatingPortfolio ||
      selectedPortfolio ||
      !portfoliosQuery.data?.length
    ) {
      return;
    }

    void selectPortfolio(
      portfoliosQuery.data[0].id,
    );
  }, [
    portfoliosQuery.data,
    selectedPortfolio,
    isCreatingPortfolio,
  ]);

  async function handlePortfolioCreated(
    portfolio: PortfolioResponse,
  ) {
    setSelectedPortfolio(portfolio);
    setIsCreatingPortfolio(false);

    await portfoliosQuery.refetch();
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

  async function reloadSelectedPortfolio() {
  if (!selectedPortfolio) {
    return;
  }

  const refreshed = await getPortfolio(
    selectedPortfolio.id,
  );

  setSelectedPortfolio(refreshed);

  await portfoliosQuery.refetch();
  }

  const portfolios =
    portfoliosQuery.data ?? [];

  const showCreateScreen =
    isCreatingPortfolio ||
    portfolios.length === 0;

  return (
    <main className="shell">
      {showCreateScreen ? (
        <>
          <header className="app-heading">
            <p className="eyebrow">
              PORTSIGNAL
            </p>

            <h1>
              Build a portfolio that understands
              its own risks.
            </h1>

            <p>
              Add your holdings to track live
              values, allocation, performance and
              relevant financial news.
            </p>
          </header>

          {portfolios.length > 0 && (
            <button
              className="secondary-button back-button"
              type="button"
              onClick={() => {
                setIsCreatingPortfolio(false);

                void selectPortfolio(
                  portfolios[0].id,
                );
              }}
            >
              Back to portfolios
            </button>
          )}

          <CreatePortfolioForm
            onPortfolioCreated={
              handlePortfolioCreated
            }
          />
        </>
      ) : (
        <>
          {isLoadingPortfolio ? (
            <section className="card loading-card">
              <p className="eyebrow">
                PORTFOLIO
              </p>

              <h2>Loading portfolio…</h2>
            </section>
          ) : selectedPortfolio ? (
            <>
              <AppNavigation
                portfolios={portfolios}
                selectedPortfolioId={
                  selectedPortfolio?.id ?? null
                }
                isLoading={isLoadingPortfolio}
                onSelectPortfolio={selectPortfolio}
                onCreatePortfolio={
                  openCreatePortfolioScreen
                }
              />

              {isLoadingPortfolio ? (
                <section className="card loading-card">
                  <h2>Loading portfolio…</h2>
                </section>
              ) : (
                <Routes>

                  <Route
                    path="/analytics"
                    element={
                      <AnalyticsPage
                        portfolio={selectedPortfolio}
                      />
                    }
                  />
                  
                    <Route
                      path="/watchlist"
                      element={<WatchlistPage />}
                    />

                    <Route
                      path="/screener"
                      element={<ScreenerPage />}
                    />

                    <Route
                      path="/"
                      element={
                        <PortfolioDetails
                          portfolio={selectedPortfolio}
                          onPortfolioChanged={
                            reloadSelectedPortfolio
                          }
                        />
                      }
                    />

                  <Route
                    path="/news"
                    element={
                      <NewsPage
                        portfolio={selectedPortfolio}
                      />
                    }
                  />
                </Routes>
              )}
            </>
          ) : null}
        </>
      )}
    </main>
  );
}