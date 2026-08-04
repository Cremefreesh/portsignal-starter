import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  PortfolioResponse,
  PositionResponse,
  addPortfolioPosition,
  deletePortfolioPosition,
  updatePortfolioPosition,
} from "../api";

type Props = {
  portfolio: PortfolioResponse;
  onPortfolioChanged: () => Promise<void>;
};

type EditState = {
  quantity: string;
  averageCost: string;
  currency: string;
};

export default function PortfolioPositionManager({
  portfolio,
  onPortfolioChanged,
}: Props) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [averageCost, setAverageCost] =
    useState("0");
  const [currency, setCurrency] =
    useState("USD");

  const [editingId, setEditingId] =
    useState<string | null>(null);

  const [editState, setEditState] =
    useState<EditState | null>(null);

  const [isSaving, setIsSaving] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    setEditingId(null);
    setEditState(null);
    setError(null);
  }, [portfolio.id]);

  async function addPosition(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setIsSaving(true);
    setError(null);

    try {
      await addPortfolioPosition(portfolio.id, {
        ticker: ticker.trim().toUpperCase(),
        quantity: Number(quantity),
        average_cost: Number(averageCost),
        currency,
      });

      setTicker("");
      setQuantity("1");
      setAverageCost("0");

      await onPortfolioChanged();
    } catch (requestError) {
      console.error(requestError);

      setError(
        "The holding could not be added. It may already exist in this portfolio.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  function beginEditing(
    position: PositionResponse,
  ) {
    setEditingId(position.id);

    setEditState({
      quantity: String(position.quantity),
      averageCost: String(
        position.average_cost,
      ),
      currency: position.currency,
    });
  }

  async function saveEdit(
    positionId: string,
  ) {
    if (!editState) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await updatePortfolioPosition(
        portfolio.id,
        positionId,
        {
          quantity: Number(editState.quantity),
          average_cost: Number(
            editState.averageCost,
          ),
          currency: editState.currency,
        },
      );

      setEditingId(null);
      setEditState(null);

      await onPortfolioChanged();
    } catch (requestError) {
      console.error(requestError);

      setError(
        "The holding could not be updated.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function removePosition(
    position: PositionResponse,
  ) {
    const confirmed = window.confirm(
      `Remove ${position.ticker} from this portfolio?`,
    );

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await deletePortfolioPosition(
        portfolio.id,
        position.id,
      );

      await onPortfolioChanged();
    } catch (requestError) {
      console.error(requestError);

      setError(
        "The holding could not be removed.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="card position-manager">
      <div>
        <p className="eyebrow">
          MANAGE HOLDINGS
        </p>

        <h2>Add, edit or remove positions</h2>
      </div>

      <form
        className="add-position-form"
        onSubmit={addPosition}
      >
        <label>
          Ticker

          <input
            required
            value={ticker}
            placeholder="AAPL"
            onChange={(event) =>
              setTicker(
                event.target.value.toUpperCase(),
              )
            }
          />
        </label>

        <label>
          Quantity

          <input
            required
            type="number"
            min="0.000001"
            step="any"
            value={quantity}
            onChange={(event) =>
              setQuantity(event.target.value)
            }
          />
        </label>

        <label>
          Average cost

          <input
            required
            type="number"
            min="0"
            step="any"
            value={averageCost}
            onChange={(event) =>
              setAverageCost(
                event.target.value,
              )
            }
          />
        </label>

        <label>
          Currency

          <select
            value={currency}
            onChange={(event) =>
              setCurrency(event.target.value)
            }
          >
            <option value="USD">USD</option>
            <option value="GBP">GBP</option>
            <option value="EUR">EUR</option>
          </select>
        </label>

        <button
          className="primary-button"
          type="submit"
          disabled={isSaving}
        >
          Add holding
        </button>
      </form>

      {error && (
        <p className="form-error">{error}</p>
      )}

      <div className="position-manager-list">
        {portfolio.positions.map((position) => {
          const isEditing =
            editingId === position.id;

          return (
            <div
              className="position-manager-row"
              key={position.id}
            >
              <strong>{position.ticker}</strong>

              {isEditing && editState ? (
                <>
                  <input
                    aria-label={`${position.ticker} quantity`}
                    type="number"
                    min="0.000001"
                    step="any"
                    value={editState.quantity}
                    onChange={(event) =>
                      setEditState({
                        ...editState,
                        quantity:
                          event.target.value,
                      })
                    }
                  />

                  <input
                    aria-label={`${position.ticker} average cost`}
                    type="number"
                    min="0"
                    step="any"
                    value={editState.averageCost}
                    onChange={(event) =>
                      setEditState({
                        ...editState,
                        averageCost:
                          event.target.value,
                      })
                    }
                  />

                  <select
                    value={editState.currency}
                    onChange={(event) =>
                      setEditState({
                        ...editState,
                        currency:
                          event.target.value,
                      })
                    }
                  >
                    <option value="USD">
                      USD
                    </option>
                    <option value="GBP">
                      GBP
                    </option>
                    <option value="EUR">
                      EUR
                    </option>
                  </select>

                  <div className="position-actions">
                    <button
                      className="primary-button compact-button"
                      type="button"
                      disabled={isSaving}
                      onClick={() =>
                        saveEdit(position.id)
                      }
                    >
                      Save
                    </button>

                    <button
                      className="secondary-button compact-button"
                      type="button"
                      onClick={() => {
                        setEditingId(null);
                        setEditState(null);
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <span>
                    {position.quantity} shares
                  </span>

                  <span>
                    {position.currency}{" "}
                    {position.average_cost.toFixed(
                      2,
                    )}
                  </span>

                  <span>{position.currency}</span>

                  <div className="position-actions">
                    <button
                      className="secondary-button compact-button"
                      type="button"
                      onClick={() =>
                        beginEditing(position)
                      }
                    >
                      Edit
                    </button>

                    <button
                      className="remove-button compact-button"
                      type="button"
                      disabled={isSaving}
                      onClick={() =>
                        removePosition(position)
                      }
                    >
                      Remove
                    </button>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}