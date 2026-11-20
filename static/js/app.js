"use strict";

// Kopano Home & Lifestyle — live Flask/MySQL dashboard

const API = {
    products: "/api/products?per_page=100",
    suppliers: "/api/suppliers",
    deliveries: "/api/deliveries",
    summary: "/api/dashboard/summary"
};

let inventory = [];
let suppliers = [];
let deliveries = [];

let inventorySort = { key: "name", direction: 1 };
let deliverySort = { key: "route", direction: 1 };

const $ = selector => document.querySelector(selector);

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options
    });

    let result;
    try {
        result = await response.json();
    } catch {
        throw new Error("The server returned an unreadable response.");
    }

    if (!response.ok) {
        throw new Error(result.error || result.message || "The request failed.");
    }

    return result;
}

function inventoryStatus(item) {
    if (item.stock <= 0) {
        return { label: "Stockout", className: "text-bg-danger" };
    }
    if (item.stock <= item.reorder) {
        return { label: "Reorder", className: "text-bg-danger" };
    }
    if (item.stock <= item.reorder * 1.2) {
        return { label: "Monitor", className: "text-bg-warning" };
    }
    return { label: "Healthy", className: "text-bg-success" };
}

function mapProduct(product) {
    return {
        id: product.product_id,
        name: product.product_name,
        sku: product.sku,
        stock: Number(product.quantity_in_stock),
        reorder: Number(product.reorder_level),
        supplier: product.supplier_name || "Unknown supplier",
        category: product.category,
        price: Number(product.unit_price)
    };
}

function mapDelivery(delivery) {
    return {
        id: delivery.delivery_id,
        route: delivery.delivery_reference,
        vehicle: delivery.supplier_name || "Unknown supplier",
        eta: delivery.expected_date || "Not specified",
        status: delivery.delivery_status,
        exception: delivery.notes || "No notes",
        actualDate: delivery.actual_date
    };
}

async function loadDashboard() {
    try {
        const [productResult, supplierResult, deliveryResult, summary] =
            await Promise.all([
                apiRequest(API.products),
                apiRequest(API.suppliers),
                apiRequest(API.deliveries),
                apiRequest(API.summary)
            ]);

        inventory = (productResult.data || []).map(mapProduct);
        suppliers = supplierResult;
        deliveries = deliveryResult.map(mapDelivery);

        renderInventory();
        renderDeliveries();
        renderSuppliers();
        renderSummary(summary);
    } catch (error) {
        console.error("Dashboard loading error:", error);

        const message = `Could not load dashboard data: ${error.message}`;

        if ($("#stockMessage")) {
            $("#stockMessage").textContent = message;
            $("#stockMessage").className = "form-message mt-2 text-danger";
        }

        if ($("#inventoryBody")) {
            $("#inventoryBody").innerHTML =
                `<tr><td colspan="6">${escapeHtml(message)}</td></tr>`;
        }

        if ($("#deliveryBody")) {
            $("#deliveryBody").innerHTML =
                `<tr><td colspan="5">${escapeHtml(message)}</td></tr>`;
        }
    }
}

function populateProductSelect() {
    const select = $("#stockProduct");
    if (!select) return;

    const previous = select.value;

    select.innerHTML =
        '<option value="">Choose a product</option>' +
        inventory.map(item =>
            `<option value="${item.id}">${escapeHtml(item.name)} (${escapeHtml(item.sku)})</option>`
        ).join("");

    if (inventory.some(item => String(item.id) === previous)) {
        select.value = previous;
    }
}

function populateDeliverySelect() {
    const select = $("#deliveryVehicle");
    if (!select) return;

    const previous = select.value;

    select.innerHTML =
        '<option value="">Choose a delivery</option>' +
        deliveries.map(item =>
            `<option value="${item.id}">${escapeHtml(item.route)} — ${escapeHtml(item.vehicle)}</option>`
        ).join("");

    if (deliveries.some(item => String(item.id) === previous)) {
        select.value = previous;
    }
}

function renderInventory() {
    const body = $("#inventoryBody");
    if (!body) return;

    const search = ($("#inventorySearch")?.value || "").trim().toLowerCase();

    const filtered = inventory.filter(item =>
        `${item.name} ${item.sku} ${item.supplier} ${item.category}`
            .toLowerCase()
            .includes(search)
    );

    filtered.sort((a, b) => {
        const first = a[inventorySort.key];
        const second = b[inventorySort.key];

        const result = typeof first === "number"
            ? first - second
            : String(first).localeCompare(
                String(second),
                undefined,
                { numeric: true }
            );

        return result * inventorySort.direction;
    });

    body.innerHTML = filtered.map(item => {
        const status = inventoryStatus(item);

        return `
            <tr>
                <td class="fw-semibold">${escapeHtml(item.name)}</td>
                <td>${escapeHtml(item.sku)}</td>
                <td>${item.stock}</td>
                <td>${item.reorder}</td>
                <td>${escapeHtml(item.supplier)}</td>
                <td><span class="badge ${status.className}">${status.label}</span></td>
            </tr>
        `;
    }).join("");

    $("#totalProducts").textContent = inventory.length;

    const lowItems = inventory.filter(item => item.stock <= item.reorder);

    $("#lowStockCount").textContent = lowItems.length;

    $("#actionList").innerHTML = lowItems.length
        ? lowItems.map(item => `
            <li>
                Review <strong>${escapeHtml(item.name)}</strong>:
                ${item.stock} units in stock; reorder point is ${item.reorder}.
            </li>
        `).join("")
        : "<li>No products are currently at or below their reorder point.</li>";

    populateProductSelect();
}

function renderDeliveries() {
    const body = $("#deliveryBody");
    if (!body) return;

    const rows = [...deliveries].sort((a, b) =>
        String(a[deliverySort.key]).localeCompare(
            String(b[deliverySort.key]),
            undefined,
            {
                numeric: true,
                sensitivity: "base"
            }
        ) * deliverySort.direction
    );

    body.innerHTML = rows.map(item => {
        const cls = item.status === "Delivered"
            ? "text-bg-success"
            : item.status === "Delayed"
                ? "text-bg-danger"
                : item.status === "Cancelled"
                    ? "text-bg-secondary"
                    : "text-bg-warning";

        return `
            <tr>
                <td>${escapeHtml(item.route)}</td>
                <td>${escapeHtml(item.vehicle)}</td>
                <td>${escapeHtml(item.eta)}</td>
                <td><span class="badge ${cls}">${escapeHtml(item.status)}</span></td>
                <td>${escapeHtml(item.exception)}</td>
            </tr>
        `;
    }).join("");

    $("#delayedCount").textContent =
        deliveries.filter(item => item.status === "Delayed").length;

    populateDeliverySelect();
}

function renderSuppliers() {
    const section = $("#supplier-heading")?.closest("section");
    const body = section?.querySelector("tbody");

    if (!body) return;

    body.innerHTML = suppliers.map(supplier => `
        <tr>
            <td>${escapeHtml(supplier.supplier_name)}</td>
            <td>${escapeHtml(supplier.phone || "Not provided")}</td>
            <td>${escapeHtml(supplier.email || "Not provided")}</td>
        </tr>
    `).join("");

    const supplierCount = document.querySelector(
        ".stats-grid .stat-card:nth-child(4) .stat-value"
    );

    if (supplierCount) {
        supplierCount.textContent = suppliers.length;
    }
}

function renderSummary(summary) {
    const openOrders = deliveries.filter(item =>
        ["Pending", "In Transit"].includes(item.status)
    ).length;

    if ($("#openOrders")) {
        $("#openOrders").textContent = openOrders;
    }

    const fulfilmentRate = deliveries.length
        ? deliveries.filter(item => item.status === "Delivered").length /
            deliveries.length * 100
        : 0;

    if ($("#fulfilmentRate")) {
        $("#fulfilmentRate").textContent =
            `${fulfilmentRate.toFixed(1)}%`;
    }

    const heroLabel = document.querySelector(".hero-metric span");
    const heroNote = document.querySelector(".hero-metric small");

    if (heroLabel) {
        heroLabel.textContent = "Delivery completion rate";
    }

    if (heroNote) {
        heroNote.textContent = "Calculated from recorded deliveries";
    }

    const statLabels = document.querySelectorAll(
        ".stats-grid .stat-card .stat-trend"
    );

    if (statLabels[0]) {
        statLabels[0].textContent = "Live database products";
    }

    if (statLabels[1]) {
        statLabels[1].textContent = "Pending and in-transit deliveries";
    }

    if (statLabels[3]) {
        statLabels[3].textContent = "Live supplier records";
    }

    if (statLabels[4]) {
        statLabels[4].textContent = "Require follow-up";
    }

    console.log("Live dashboard summary:", summary);
}

function connectSorting() {
    document.querySelectorAll("[data-inventory-sort]").forEach(button => {
        button.addEventListener("click", () => {
            const keyMap = {
                name: "name",
                sku: "sku",
                stock: "stock",
                reorder: "reorder"
            };

            const key = keyMap[button.dataset.inventorySort];
            if (!key) return;

            inventorySort = {
                key,
                direction: inventorySort.key === key
                    ? -inventorySort.direction
                    : 1
            };

            renderInventory();
        });
    });

    document.querySelectorAll("[data-delivery-sort]").forEach(button => {
        button.addEventListener("click", () => {
            const keyMap = {
                route: "route",
                vehicle: "vehicle",
                eta: "eta",
                status: "status"
            };

            const key = keyMap[button.dataset.deliverySort];
            if (!key) return;

            deliverySort = {
                key,
                direction: deliverySort.key === key
                    ? -deliverySort.direction
                    : 1
            };

            renderDeliveries();
        });
    });
}

function connectStockForm() {
    const form = $("#stockForm");
    if (!form) return;

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const productId = $("#stockProduct").value;
        const input = $("#newStock");
        const quantity = Number(input.value);

        input.setCustomValidity(
            Number.isInteger(quantity) && quantity >= 0
                ? ""
                : "Enter a whole number of zero or more."
        );

        if (!form.checkValidity() || !productId) {
            form.classList.add("was-validated");
            return;
        }

        const product = inventory.find(
            item => String(item.id) === productId
        );

        if (!product) return;

        const message = $("#stockMessage");

        message.textContent = "Saving stock update...";
        message.className = "form-message mt-2 text-secondary";

        try {
            await apiRequest(`/api/products/${product.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    quantity_in_stock: quantity,
                    reorder_level: product.reorder
                })
            });

            await loadDashboard();

            message.textContent =
                `Successfully updated ${product.name} to ${quantity} units in the database.`;

            message.className = "form-message mt-2 text-success";

            input.value = "";
            form.classList.remove("was-validated");

        } catch (error) {
            message.textContent = `Update failed: ${error.message}`;
            message.className = "form-message mt-2 text-danger";
        }
    });
}

function connectExceptionForm() {
    const form = $("#exceptionForm");
    if (!form) return;

    const statusSelect = $("#deliveryStatus");

    if (statusSelect) {
        // Use the exact statuses accepted by the MySQL ENUM and Flask API.
        statusSelect.innerHTML = `
            <option value="">Choose a status</option>
            <option value="Pending">Pending</option>
            <option value="In Transit">In Transit</option>
            <option value="Delivered">Delivered</option>
            <option value="Delayed">Delayed</option>
            <option value="Cancelled">Cancelled</option>
        `;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        if (!form.checkValidity()) {
            form.classList.add("was-validated");
            form.reportValidity();
            return;
        }

        const deliveryId = $("#deliveryVehicle").value;
        const status = $("#deliveryStatus").value;
        const note = $("#deliveryException").value.trim();

        const delivery = deliveries.find(
            item => String(item.id) === deliveryId
        );

        if (!delivery || !status || !note) {
            form.classList.add("was-validated");
            return;
        }

        const submitButton = form.querySelector(
            'button[type="submit"]'
        );

        const originalButtonText = submitButton?.textContent;

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Saving...";
        }

        try {
            await apiRequest(`/api/deliveries/${delivery.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    delivery_status: status,
                    notes: note
                })
            });

            await loadDashboard();

            form.reset();
            form.classList.remove("was-validated");

            const modalElement = $("#exceptionModal");

            if (modalElement && window.bootstrap) {
                bootstrap.Modal
                    .getOrCreateInstance(modalElement)
                    .hide();
            }

            // The delivery board refreshes from MySQL after a successful update.
            alert(
                `Delivery ${delivery.route} was updated successfully.`
            );

        } catch (error) {
            alert(`Delivery update failed: ${error.message}`);

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent =
                    originalButtonText || "Save update";
            }
        }
    });
}

function connectCsvExport() {
    $("#exportButton")?.addEventListener("click", () => {
        const headers = [
            "Product",
            "SKU",
            "Stock",
            "Reorder point",
            "Supplier",
            "Status"
        ];

        const rows = inventory.map(item => [
            item.name,
            item.sku,
            item.stock,
            item.reorder,
            item.supplier,
            inventoryStatus(item).label
        ]);

        const cell = value =>
            `"${String(value).replace(/"/g, '""')}"`;

        const csv = [headers, ...rows]
            .map(row => row.map(cell).join(","))
            .join("\r\n");

        const blob = new Blob(
            [csv],
            { type: "text/csv;charset=utf-8;" }
        );

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

        const fields = [
            "#annualDemand",
            "#orderCost",
            "#holdingCost"
        ];

        fields.forEach(selector => {
            const input = $(selector);
            const value = Number(input.value);

            input.setCustomValidity(
                Number.isFinite(value) && value > 0
                    ? ""
                    : "Enter a value greater than zero."
            );
        });

        if (!form.checkValidity()) {
            form.classList.add("was-validated");
            form.reportValidity();
            return;
        }

        const eoq = Math.sqrt(
            (2 * demand * orderCost) / holdingCost
        );

        const orders = demand / eoq;

        const annualCost =
            (demand / eoq) * orderCost +
            (eoq / 2) * holdingCost;

        $("#eoqResult").innerHTML = `
            <strong>Recommended EOQ:</strong> ${eoq.toFixed(2)} units<br>
            <strong>Orders per year:</strong> ${orders.toFixed(2)}<br>
            <strong>Annual ordering + holding cost:</strong> R${annualCost.toFixed(2)}
        `;

        form.classList.remove("was-validated");
    });
}

// Connect all dashboard functionality.
$("#inventorySearch")?.addEventListener("input", renderInventory);

connectSorting();
connectStockForm();
connectExceptionForm();
connectCsvExport();
connectEoqForm();

// Load the latest data from the Flask API and MySQL database.
loadDashboard();