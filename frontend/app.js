const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const rowsEl = document.getElementById("rows");

const formatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

const formatMoney = (value) => `$${formatter.format(value)}`;

const renderSummary = (best) => {
  if (!best) {
    summaryEl.innerHTML = "<p>No opportunities yet.</p>";
    return;
  }

  summaryEl.innerHTML = `
    <div>
      <h2>Best Opportunity</h2>
      <p class="summary-market">${best.market.market_id}</p>
    </div>
    <div>
      <p class="summary-label">Strategy</p>
      <p>${best.best_strategy.name}</p>
    </div>
    <div>
      <p class="summary-label">Total Cost</p>
      <p>${formatMoney(best.best_strategy.total_cost)}</p>
    </div>
    <div>
      <p class="summary-label">Expected Profit</p>
      <p>${formatMoney(best.best_strategy.expected_profit)}</p>
    </div>
  `;
};

const renderRows = (opportunities) => {
  rowsEl.innerHTML = "";

  opportunities.forEach((item) => {
    const row = document.createElement("tr");
    row.className = item.best_strategy.total_cost < 1 ? "profit" : "";

    row.innerHTML = `
      <td>${item.market.market_id}</td>
      <td>${new Date(item.market.expiration).toISOString().replace(".000Z", "Z")}</td>
      <td>${formatMoney(item.market.strike_price)}</td>
      <td>${item.best_strategy.name}</td>
      <td>${formatMoney(item.best_strategy.total_cost)}</td>
      <td>${formatMoney(item.best_strategy.expected_profit)}</td>
    `;

    rowsEl.appendChild(row);
  });
};

const update = async () => {
  try {
    const response = await fetch("/opportunities");
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    const payload = await response.json();
    statusEl.textContent = `Live · refresh ${payload.refresh_interval_seconds}s`;
    statusEl.classList.add("ok");
    renderSummary(payload.best);
    renderRows(payload.opportunities);

    setTimeout(update, payload.refresh_interval_seconds * 1000);
  } catch (error) {
    statusEl.textContent = "Offline · retrying";
    statusEl.classList.remove("ok");
    setTimeout(update, 4000);
  }
};

update();
