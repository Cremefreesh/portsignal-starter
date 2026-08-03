import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { PortfolioValuation } from "../api";

type Props = {
  valuation: PortfolioValuation;
};

type TooltipPayload = {
  name: string;
  value: number;
  payload: {
    ticker: string;
    marketValue: number;
    weight: number;
  };
};

const CHART_COLOURS = [
  "#e1e2e5",
  "#b9bbc1",
  "#91949b",
  "#6e7178",
  "#55585f",
  "#3e4147",
  "#c9cbd0",
  "#7c7f86",
];

function formatMoney(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

function AllocationTooltip({
  active,
  payload,
  currency,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  currency: string;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  const holding = payload[0].payload;

  return (
    <div className="chart-tooltip">
      <strong>{holding.ticker}</strong>

      <span>
        {formatMoney(
          holding.marketValue,
          currency,
        )}
      </span>

      <span>
        {(holding.weight * 100).toFixed(1)}%
      </span>
    </div>
  );
}

export default function PortfolioAllocationChart({
  valuation,
}: Props) {
  const chartData = valuation.positions
    .map((position) => ({
      ticker: position.ticker,
      marketValue: position.market_value,
      weight:
        valuation.total_market_value > 0
          ? position.market_value /
            valuation.total_market_value
          : 0,
    }))
    .sort(
      (first, second) =>
        second.marketValue - first.marketValue,
    );

  if (chartData.length === 0) {
    return (
      <article className="card allocation-chart-card">
        <p>No valued holdings to display.</p>
      </article>
    );
  }

  return (
    <article className="card allocation-chart-card">
      <div className="chart-card-heading">
        <div>
          <p className="eyebrow">
            ALLOCATION CHART
          </p>

          <h2>Portfolio composition</h2>
        </div>
      </div>

      <div className="allocation-chart-container">
        <ResponsiveContainer
          width="100%"
          height={360}
        >
          <PieChart>
            <Pie
              data={chartData}
              dataKey="marketValue"
              nameKey="ticker"
              cx="50%"
              cy="47%"
              innerRadius={76}
              outerRadius={124}
              paddingAngle={2}
              stroke="none"
            >
              {chartData.map((holding, index) => (
                <Cell
                  key={holding.ticker}
                  fill={
                    CHART_COLOURS[
                      index % CHART_COLOURS.length
                    ]
                  }
                />
              ))}
            </Pie>

            <Tooltip
              content={
                <AllocationTooltip
                  currency={
                    valuation.valuation_currency
                  }
                />
              }
            />

            <Legend
              verticalAlign="bottom"
              height={42}
              formatter={(ticker) => (
                <span className="chart-legend-label">
                  {ticker}
                </span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>

        <div className="allocation-chart-centre">
          <strong>
            {valuation.positions.length}
          </strong>

          <span>Holdings</span>
        </div>
      </div>
    </article>
  );
}