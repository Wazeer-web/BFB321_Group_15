/*
 * Kopano Home & Lifestyle — frontend interactions.
 * All records are simulated and stored in browser memory only.
 * Refreshing the page resets changes. No server/database is used in Steps 1–2.
 */
"use strict";

const inventory = [
  { name: "Timber Panels", sku: "KHL-RAW-001", stock: 120, reorder: 150, supplier: "TimberWorks SA" },
  { name: "Metal Frames", sku: "KHL-RAW-002", stock: 32, reorder: 90, supplier: "MetalCraft Suppliers" },
  { name: "Fabric Rolls", sku: "KHL-RAW-003", stock: 140, reorder: 110, supplier: "FabricWorks SA" },
  { name: "Desk Components", sku: "KHL-COMP-004", stock: 52, reorder: 80, supplier: "MetalCraft Suppliers" }
];

const deliveries = [
  { route: "Pretoria - Johannesburg", vehicle: "TRK-015", eta: "2026-10-23 10:00", status: "Delayed", exception: "Supplier dispatch delay" },
  { route: "Johannesburg - Centurion", vehicle: "TRK-021", eta: "2026-10-23 12:30", status: "On schedule", exception: "None reported" },
  { route: "Pretoria - Midrand", vehicle: "TRK-008", eta: "2026-10-23 14:00", status: "At risk", exception: "Stock availability risk" }
];

const $ = selector => document.querySelector(selector);
let inventorySort = { key: "name", direction: 1 };
let deliverySort = { key: "route", direction: 1 };

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
}

function inventoryStatus(item) {
  if (item.stock <= 0) return { label: "Stockout", className: "text-bg-danger" };
  if (item.stock <= item.reorder) return { label: "Reorder", className: "text-bg-danger" };
  if (item.stock <= item.reorder * 1.2) return { label: "Monitor", className: "text-bg-warning" };
  return { label: "Healthy", className: "text-bg-success" };
}

function populateProductSelect() {
  const select = $("#stockProduct");
  if (!select) return;
  const previous = select.value;
  select.innerHTML = '<option value="">Choose a product</option>' +
    inventory.map(item => `<option value="${escapeHtml(item.sku)}">${escapeHtml(item.name)} (${escapeHtml(item.sku)})</option>`).join("");
  if (inventory.some(item => item.sku === previous)) select.value = previous;
}

function populateDeliverySelect() {
  const select = $("#deliveryVehicle");
  if (!select) return;
  const previous = select.value;
  select.innerHTML = '<option value="">Choose a delivery</option>' +
    deliveries.map(item => `<option value="${escapeHtml(item.vehicle)}">${escapeHtml(item.vehicle)} — ${escapeHtml(item.route)}</option>`).join("");
  if (deliveries.some(item => item.vehicle === previous)) select.value = previous;
}

function renderInventory() {
  const body = $("#inventoryBody");
  if (!body) return;
  const search = ($("#inventorySearch")?.value || "").trim().toLowerCase();

  const filtered = inventory.filter(item =>
    `${item.name} ${item.sku} ${item.supplier}`.toLowerCase().includes(search)
  );
  filtered.sort((a, b) => {
    const first = a[inventorySort.key], second = b[inventorySort.key];
    const result = typeof first === "number" ? first - second :
      String(first).localeCompare(String(second), undefined, { numeric: true });
    return result * inventorySort.direction;
  });

  body.innerHTML = filtered.map(item => {
    const status = inventoryStatus(item);
    return `<tr>
      <td class="fw-semibold">${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.sku)}</td><td>${item.stock}</td><td>${item.reorder}</td>
      <td>${escapeHtml(item.supplier)}</td>
      <td><span class="badge ${status.className}">${status.label}</span></td>
    </tr>`;
  }).join("");

  $("#totalProducts").textContent = inventory.length;
  $("#lowStockCount").textContent = inventory.filter(item => item.stock <= item.reorder).length;
  const lowItems = inventory.filter(item => item.stock <= item.reorder);
  $("#actionList").innerHTML = lowItems.length
    ? lowItems.map(item => `<li>Review <strong>${escapeHtml(item.name)}</strong>: ${item.stock} units in stock; reorder point is ${item.reorder}.</li>`).join("")
    : "<li>No products are currently at or below their reorder point.</li>";
  populateProductSelect();
}

function renderDeliveries() {
  const body = $("#deliveryBody");
  if (!body) return;
  const rows = [...deliveries].sort((a, b) =>
    String(a[deliverySort.key]).localeCompare(String(b[deliverySort.key]), undefined, { numeric: true, sensitivity: "base" }) * deliverySort.direction
  );

  body.innerHTML = rows.map(item => {
    const cls = item.status === "Delivered" || item.status === "On schedule"
      ? "text-bg-success" : item.status === "Delayed" ? "text-bg-danger" : "text-bg-warning";
    return `<tr>
      <td>${escapeHtml(item.route)}</td><td>${escapeHtml(item.vehicle)}</td>
      <td>${escapeHtml(item.eta)}</td>
      <td><span class="badge ${cls}">${escapeHtml(item.status)}</span></td>
      <td>${escapeHtml(item.exception)}</td>
    </tr>`;
  }).join("");

  $("#delayedCount").textContent = deliveries.filter(item => item.status === "Delayed").length;
  populateDeliverySelect();
}

function connectSorting() {
  document.querySelectorAll("[data-inventory-sort]").forEach(button => {
    button.addEventListener("click", () => {
      const key = button.dataset.inventorySort;
      inventorySort = { key, direction: inventorySort.key === key ? -inventorySort.direction : 1 };
      renderInventory();
    });
  });
  document.querySelectorAll("[data-delivery-sort]").forEach(button => {
    button.addEventListener("click", () => {
      const key = button.dataset.deliverySort;
      deliverySort = { key, direction: deliverySort.key === key ? -deliverySort.direction : 1 };
      renderDeliveries();
    });
  });
}

function connectStockForm() {
  const form = $("#stockForm");
  if (!form) return;
  form.addEventListener("submit", event => {
    event.preventDefault();
    const product = inventory.find(item => item.sku === $("#stockProduct").value);
    const input = $("#newStock");
    const quantity = Number(input.value);
    input.setCustomValidity(Number.isInteger(quantity) && quantity >= 0 ? "" : "Enter a whole number of zero or more.");
    if (!form.checkValidity() || !product) {
      form.classList.add("was-validated");
      if (!product) $("#stockProduct").setCustomValidity("Select a product.");
      return;
    }
    $("#stockProduct").setCustomValidity("");
    product.stock = quantity;
    renderInventory();
    $("#stockMessage").textContent = `Updated ${product.name} to ${quantity} units. This change is temporary and will reset on refresh.`;
    $("#stockMessage").className = "form-message mt-2 text-success";
    input.value = "";
    form.classList.remove("was-validated");
  });
}

function connectExceptionForm() {
  const form = $("#exceptionForm");
  if (!form) return;
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      form.reportValidity();
      return;
    }
    const vehicle = $("#deliveryVehicle").value;
    const status = $("#deliveryStatus").value;
    const note = $("#deliveryException").value.trim();
    const delivery = deliveries.find(item => item.vehicle === vehicle);
    if (!delivery || !note) {
      $("#deliveryException").setCustomValidity(note ? "" : "Enter an update note.");
      form.classList.add("was-validated");
      return;
    }
    delivery.status = status;
    delivery.exception = note;
    renderDeliveries();
    form.reset();
    form.classList.remove("was-validated");
    bootstrap.Modal.getOrCreateInstance($("#exceptionModal")).hide();
  });
}

function connectCsvExport() {
  $("#exportButton")?.addEventListener("click", () => {
    const headers = ["Product", "SKU", "Stock", "Reorder point", "Supplier", "Status"];
    const rows = inventory.map(item => [item.name, item.sku, item.stock, item.reorder, item.supplier, inventoryStatus(item).label]);
    const cell = value => `"${String(value).replace(/"/g, '""')}"`;
    const csv = [headers, ...rows].map(row => row.map(cell).join(",")).join("\\r\\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "kopano-inventory.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
}

function connectEoqForm() {
  const form = $("#eoqForm");
  if (!form) return;
  form.addEventListener("submit", event => {
    event.preventDefault();
    const demand = Number($("#annualDemand").value);
    const orderCost = Number($("#orderCost").value);
    const holdingCost = Number($("#holdingCost").value);
    const fields = ["#annualDemand", "#orderCost", "#holdingCost"];

    fields.forEach(selector => {
      const input = $(selector);
      const value = Number(input.value);
      input.setCustomValidity(Number.isFinite(value) && value > 0 ? "" : "Enter a value greater than zero.");
    });
    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      form.reportValidity();
      return;
    }

    const eoq = Math.sqrt((2 * demand * orderCost) / holdingCost);
    const orders = demand / eoq;
    const annualCost = (demand / eoq) * orderCost + (eoq / 2) * holdingCost;
    $("#eoqResult").innerHTML = `<strong>Recommended EOQ:</strong> ${eoq.toFixed(2)} units<br>
      <strong>Orders per year:</strong> ${orders.toFixed(2)}<br>
      <strong>Annual ordering + holding cost:</strong> R${annualCost.toFixed(2)}`;
    form.classList.remove("was-validated");
  });
}

$("#inventorySearch")?.addEventListener("input", renderInventory);
connectSorting();
connectStockForm();
connectExceptionForm();
connectCsvExport();
connectEoqForm();
renderInventory();
renderDeliveries();
