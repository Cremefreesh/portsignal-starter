import {
  ChangeEvent,
  FormEvent,
  useState,
} from "react";
import {
  PortfolioCreate,
  PortfolioResponse,
  PositionCreate,
  createPortfolio,
} from "../api";

type Props = {
  onPortfolioCreated: (
    portfolio: PortfolioResponse,
  ) => void;
};

const emptyPosition = (): PositionCreate => ({
  ticker: "",
  quantity: 1,
  average_cost: 0,
  currency: "USD",
});

export default function CreatePortfolioForm({
  onPortfolioCreated,
}: Props) {
  const [name, setName] = useState("");
  const [benchmarkTicker, setBenchmarkTicker] =
    useState("SPY");
  const [baseCurrency, setBaseCurrency] =
    useState("GBP");
  const [positions, setPositions] = useState<
    PositionCreate[]
  >([emptyPosition()]);

  const [isSubmitting, setIsSubmitting] =
    useState(false);
  const [error, setError] = useState<string | null>(
    null,
  );

  function updatePosition(
    index: number,
    field: keyof PositionCreate,
    value: string,
  ) {
    setPositions((currentPositions) =>
      currentPositions.map((position, positionIndex) => {
        if (positionIndex !== index) {
          return position;
        }

        if (
          field === "quantity" ||
          field === "average_cost"
        ) {
          return {
            ...position,
            [field]: Number(value),
          };
        }

        return {
          ...position,
          [field]: value.toUpperCase(),
        };
      }),
    );
  }

  function addPositionRow() {
    setPositions((currentPositions) => [
      ...currentPositions,
      emptyPosition(),
    ]);
  }

  function removePositionRow(index: number) {
    setPositions((currentPositions) =>
      currentPositions.filter(
        (_, positionIndex) => positionIndex !== index,
      ),
    );
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);
    setIsSubmitting(true);

    const payload: PortfolioCreate = {
      name: name.trim(),
      benchmark_ticker:
        benchmarkTicker.trim().toUpperCase(),
      base_currency:
        baseCurrency.trim().toUpperCase(),
      positions: positions.map((position) => ({
        ...position,
        ticker: position.ticker.trim().toUpperCase(),
        currency:
          position.currency.trim().toUpperCase(),
      })),
    };

    try {
      const portfolio =
        await createPortfolio(payload);

      onPortfolioCreated(portfolio);
    } catch (requestError) {
      console.error(requestError);

      setError(
        "The portfolio could not be created. Check the values and try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      className="portfolio-form card"
      onSubmit={handleSubmit}
    >
      <div className="form-heading">
        <div>
          <p className="eyebrow">NEW PORTFOLIO</p>
          <h2>Build your portfolio</h2>
        </div>

        <p>
          Enter the holdings you currently own. Live prices
          will be connected later.
        </p>
      </div>

      <div className="portfolio-fields">
        <label>
          Portfolio name

          <input
            required
            value={name}
            placeholder="Archie's Main Portfolio"
            onChange={(
              event: ChangeEvent<HTMLInputElement>,
            ) => setName(event.target.value)}
          />
        </label>

        <label>
          Benchmark

          <input
            required
            value={benchmarkTicker}
            placeholder="SPY"
            onChange={(
              event: ChangeEvent<HTMLInputElement>,
            ) =>
              setBenchmarkTicker(event.target.value)
            }
          />
        </label>

        <label>
          Base currency

          <select
            value={baseCurrency}
            onChange={(
              event: ChangeEvent<HTMLSelectElement>,
            ) => setBaseCurrency(event.target.value)}
          >
            <option value="GBP">GBP</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
          </select>
        </label>
      </div>

      <div className="holdings-heading">
        <div>
          <p className="eyebrow">HOLDINGS</p>
          <h3>Stocks and funds</h3>
        </div>

        <button
          className="secondary-button"
          type="button"
          onClick={addPositionRow}
        >
          Add holding
        </button>
      </div>

      <div className="holdings-list">
        {positions.map((position, index) => (
          <div
            className="holding-row"
            key={index}
          >
            <label>
              Ticker

              <input
                required
                value={position.ticker}
                placeholder="NVDA"
                onChange={(event) =>
                  updatePosition(
                    index,
                    "ticker",
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              Quantity

              <input
                required
                min="0.000001"
                step="any"
                type="number"
                value={position.quantity}
                onChange={(event) =>
                  updatePosition(
                    index,
                    "quantity",
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              Average cost

              <input
                required
                min="0"
                step="any"
                type="number"
                value={position.average_cost}
                onChange={(event) =>
                  updatePosition(
                    index,
                    "average_cost",
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              Currency

              <select
                value={position.currency}
                onChange={(event) =>
                  updatePosition(
                    index,
                    "currency",
                    event.target.value,
                  )
                }
              >
                <option value="GBP">GBP</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </label>

            <button
              className="remove-button"
              type="button"
              disabled={positions.length === 1}
              onClick={() =>
                removePositionRow(index)
              }
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      {error && (
        <p className="form-error">{error}</p>
      )}

      <button
        className="primary-button"
        type="submit"
        disabled={isSubmitting}
      >
        {isSubmitting
          ? "Creating portfolio…"
          : "Create portfolio"}
      </button>
    </form>
  );
}