from datetime import date


def _normalise(value: float, low: float, high: float, invert: bool = False) -> float:
    if high <= low:
        raise ValueError("high must be greater than low")

    score = max(0.0, min(1.0, (value - low) / (high - low)))
    return 1.0 - score if invert else score


def calculate_market_regime(
    market_momentum: float,
    market_volatility: float,
    safe_haven_demand: float,
    junk_bond_spread: float,
    breadth: float,
) -> dict:
    # Provider-agnostic, explainable 0-100 market sentiment score.
    components = {
        "momentum": _normalise(market_momentum, -0.20, 0.20),
        "volatility": _normalise(market_volatility, 0.10, 0.45, invert=True),
        "safe_haven": _normalise(safe_haven_demand, -0.10, 0.10, invert=True),
        "credit": _normalise(junk_bond_spread, 0.02, 0.10, invert=True),
        "breadth": _normalise(breadth, 0.20, 0.80),
    }

    weights = {
        "momentum": 0.25,
        "volatility": 0.25,
        "safe_haven": 0.15,
        "credit": 0.15,
        "breadth": 0.20,
    }

    score = round(100 * sum(components[key] * weights[key] for key in components))

    if score <= 20:
        label = "Extreme Fear"
    elif score <= 40:
        label = "Fear"
    elif score < 60:
        label = "Neutral"
    elif score < 80:
        label = "Greed"
    else:
        label = "Extreme Greed"

    return {
        "score": score,
        "label": label,
        "as_of": date.today(),
        "components": {
            key: round(value * 100, 1)
            for key, value in components.items()
        },
    }
