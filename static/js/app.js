"use strict";

const DATA_TYPES = [
    "Row Number", "First Name", "Last Name", "Full Name", "Email Address",
    "Gender", "IP Address v4", "Phone Number", "City", "Country", "Date",
    "Number", "Decimal", "Custom List", "Blank/Null",
];

const FORMAT_EXTENSIONS = {
    CSV: "csv", JSON: "json", XML: "xml", SQL: "sql", EXCEL: "xlsx",
};

let fieldCounter = 0;

const fieldList = document.getElementById("field-list");
const addFieldBtn = document.getElementById("addFieldBtn");
const generateBtn = document.getElementById("generateBtn");
const previewBtn = document.getElementById("previewBtn");
const generateFromPreviewBtn = document.getElementById("generateFromPreviewBtn");
const previewNumRows = document.getElementById("previewNumRows");
const previewModalElement = document.getElementById("previewModal");

new Sortable(fieldList, {
    animation: 150,
    handle: ".drag-handle",
    ghostClass: "sortable-ghost",
});

function suggestFieldName(typeName) {
    if (typeName === "Row Number") return "id";
    return typeName.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
}

function buildFieldRow(fieldId, initial = {}) {
    const fieldRow = document.createElement("div");
    fieldRow.className = "field-row";
    fieldRow.dataset.fieldId = fieldId;
    const initialType = initial.type || "Row Number";
    const initialName = initial.name ?? suggestFieldName(initialType);

    fieldRow.innerHTML = `
        <div class="drag-handle"></div>
        <div>
            <input type="text" class="form-control form-control-sm field-name"
                   id="${fieldId}-name" name="${fieldId}-name"
                   placeholder="Field Name" required>
        </div>
        <div>
            <select class="form-select form-select-sm data-type"
                    id="${fieldId}-type" name="${fieldId}-type">
                ${DATA_TYPES.map(t => `<option value="${t}">${t}</option>`).join("")}
            </select>
            <input type="text" class="form-control form-control-sm custom-list-input"
                   id="${fieldId}-custom-list" name="${fieldId}-custom-list"
                   placeholder="Comma-separated values">
            <input type="number" class="form-control form-control-sm blank-percentage-input"
                   id="${fieldId}-blank-percentage" name="${fieldId}-blank-percentage"
                   placeholder="Blank %" min="0" max="100">
            <div class="blank-modifier">
                <label for="${fieldId}-null-pct">Null %:</label>
                <input type="number" class="form-control form-control-sm null-modifier"
                       id="${fieldId}-null-pct" min="0" max="100" value="0"
                       title="Percentage of values to leave null for this field">
            </div>
        </div>
        <div class="remove-btn" data-field-id="${fieldId}" title="Remove field">
            <i class="bi bi-x-lg"></i>
        </div>
    `;

    const nameInput = fieldRow.querySelector(".field-name");
    nameInput.value = initialName;
    nameInput.dataset.userEdited = initial.name ? "true" : "false";

    const typeSelect = fieldRow.querySelector(".data-type");
    typeSelect.value = initialType;

    return fieldRow;
}

function addField(initial = {}) {
    const fieldId = `field-${Date.now()}-${fieldCounter++}`;
    const fieldRow = buildFieldRow(fieldId, initial);
    fieldList.appendChild(fieldRow);
    handleDataTypeChange(fieldRow.querySelector(".data-type"));
}

function removeField(button) {
    button.closest(".field-row").remove();
}

function handleDataTypeChange(select) {
    const fieldRow = select.closest(".field-row");
    const customListInput = fieldRow.querySelector(".custom-list-input");
    const blankPercentageInput = fieldRow.querySelector(".blank-percentage-input");

    customListInput.style.display = "none";
    blankPercentageInput.style.display = "none";

    if (select.value === "Custom List") {
        customListInput.style.display = "block";
    } else if (select.value === "Blank/Null") {
        blankPercentageInput.style.display = "block";
    }
}

function collectSchema(numRowsOverride) {
    const numRowsInput = document.getElementById("numRows");
    const schema = {
        fields: [],
        num_rows: numRowsOverride !== undefined
            ? parseInt(numRowsOverride, 10)
            : parseInt(numRowsInput.value, 10),
        format: document.getElementById("outputFormat").value,
    };

    const fieldRows = Array.from(document.querySelectorAll(".field-row"));
    if (fieldRows.length === 0) {
        throw new Error("Please add at least one field");
    }

    fieldRows.forEach((row, index) => {
        const nameInput = row.querySelector(".field-name");
        const typeSelect = row.querySelector(".data-type");
        const fieldName = nameInput.value.trim();

        if (!fieldName) {
            throw new Error(`Field #${index + 1} requires a name`);
        }

        const field = { name: fieldName, type: typeSelect.value };

        if (field.type === "Custom List") {
            const values = row.querySelector(".custom-list-input").value
                .split(",").map(v => v.trim()).filter(Boolean);
            if (values.length === 0) {
                throw new Error(`Custom List field "${fieldName}" requires at least one value`);
            }
            field.values = values;
        } else if (field.type === "Blank/Null") {
            const pct = parseInt(row.querySelector(".blank-percentage-input").value, 10) || 0;
            if (pct < 0 || pct > 100) {
                throw new Error(`Blank percentage for "${fieldName}" must be 0-100`);
            }
            field.blank_percentage = pct;
        }

        // Per-field null modifier (applies on top of any type).
        const nullPct = parseInt(row.querySelector(".null-modifier").value, 10) || 0;
        if (nullPct > 0) {
            if (nullPct > 100) {
                throw new Error(`Null % for "${fieldName}" must be 0-100`);
            }
            field.blank_percentage = nullPct;
        }

        schema.fields.push(field);
    });

    return schema;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ---- Toast helper ---------------------------------------------------------
function showToast(message, variant = "danger") {
    const container = document.getElementById("toast-container");
    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-bg-${variant} border-0`;
    toastEl.setAttribute("role", "alert");
    toastEl.setAttribute("aria-live", "assertive");
    toastEl.setAttribute("aria-atomic", "true");
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${escapeHtml(message)}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: variant === "danger" ? 6000 : 3500 });
    toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
    toast.show();
}

// ---- Button busy state ----------------------------------------------------
function setBusy(button, busy) {
    if (busy) {
        button.dataset.busy = "true";
        if (!button.querySelector(".btn-spinner")) {
            const spinner = document.createElement("span");
            spinner.className = "btn-spinner";
            spinner.setAttribute("aria-hidden", "true");
            button.prepend(spinner);
        }
    } else {
        delete button.dataset.busy;
    }
}

async function withBusy(button, fn) {
    setBusy(button, true);
    try {
        await fn();
    } finally {
        setBusy(button, false);
    }
}

// ---- API helpers ----------------------------------------------------------
async function postJson(path, body) {
    const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        let message = `Server error: ${response.status}`;
        try {
            const data = await response.json();
            message = data.error || message;
        } catch (_) {
            const text = await response.text().catch(() => "");
            if (text) message = text;
        }
        throw new Error(message);
    }
    return response;
}

// ---- Preview --------------------------------------------------------------
async function previewData() {
    let schema;
    try {
        const numRows = previewNumRows.value || 20;
        schema = collectSchema(numRows);
    } catch (error) {
        showToast(error.message);
        return;
    }

    await withBusy(previewBtn, async () => {
        try {
            const response = await postJson("/preview", schema);
            const format = schema.format.toUpperCase();
            let result;
            if (format === "CSV" || format === "EXCEL") {
                const data = await response.json();
                if (data && data.data && data.field_order) {
                    result = { format, data: data.data, fieldOrder: data.field_order };
                } else {
                    result = { format, data };
                }
            } else {
                result = { format, text: await response.text() };
            }
            renderPreview(result, previewNumRows.value || 20);
            const previewModal = bootstrap.Modal.getOrCreateInstance(previewModalElement);
            previewModal.show();
        } catch (error) {
            const hint = error.message.includes("Failed to fetch")
                ? " Make sure the Flask server is running."
                : "";
            showToast(`Preview error: ${error.message}${hint}`);
        }
    });
}

function renderPreview(result, numRows) {
    const { format, data, text, fieldOrder } = result;
    const previewContent = document.getElementById("preview-content");
    previewContent.innerHTML = "";

    if (format === "CSV" || format === "EXCEL") {
        const dataArray = Array.isArray(data) ? data : [];
        if (dataArray.length === 0) {
            previewContent.textContent = "No data available for preview.";
        } else {
            const table = document.createElement("table");
            table.className = "table table-striped table-bordered preview-table";

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");
            const headers = fieldOrder || Object.keys(dataArray[0]);
            headers.forEach(header => {
                const th = document.createElement("th");
                th.textContent = header;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement("tbody");
            dataArray.forEach(row => {
                const tr = document.createElement("tr");
                headers.forEach(header => {
                    const td = document.createElement("td");
                    const value = row[header];
                    td.textContent = value !== null && value !== undefined ? value : "";
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            previewContent.appendChild(table);
        }
    } else {
        const pre = document.createElement("pre");
        const code = document.createElement("code");
        code.textContent = text;
        pre.appendChild(code);
        previewContent.appendChild(pre);
    }

    const note = document.getElementById("previewNote");
    note.textContent = format === "EXCEL"
        ? 'Excel preview shown as a table. Use "Generate Data" to download the actual file.'
        : `Showing preview in ${format} format (limited to ${numRows} rows)`;
}

// ---- Generate -------------------------------------------------------------
async function generateData(fromPreview = false) {
    const button = fromPreview ? generateFromPreviewBtn : generateBtn;
    let schema;
    try {
        const override = fromPreview ? previewNumRows.value : undefined;
        schema = collectSchema(override);
    } catch (error) {
        showToast(error.message);
        return;
    }

    await withBusy(button, async () => {
        try {
            const response = await postJson("/generate", schema);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            const ext = FORMAT_EXTENSIONS[schema.format.toUpperCase()] || schema.format.toLowerCase();
            a.href = url;
            a.download = `mock_data_${new Date().toISOString().replace(/[:.]/g, "-")}.${ext}`;
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(url);
            a.remove();

            if (fromPreview) {
                bootstrap.Modal.getInstance(previewModalElement)?.hide();
            }
            showToast("Download started", "success");
        } catch (error) {
            showToast(`Error generating data: ${error.message}`);
        }
    });
}

// ---- Theme ----------------------------------------------------------------
function applyTheme(theme) {
    document.body.classList.remove("theme-dark", "theme-blue");
    if (theme !== "light") document.body.classList.add(`theme-${theme}`);
}

// ---- Init -----------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    // Clamp numeric inputs to >= 1.
    ["numRows", "previewNumRows"].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener("input", function () {
            if (parseInt(this.value, 10) <= 0) this.value = 1;
        });
    });

    // Modal cleanup: registered ONCE rather than per-preview to avoid listener leak.
    previewModalElement.addEventListener("hidden.bs.modal", () => {
        document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
        document.body.classList.remove("modal-open");
        document.body.style.overflow = "";
        document.body.style.paddingRight = "";
    });

    // Initialize default rows (rendered by Jinja) — wire up handlers,
    // mark pre-existing field names as user-edited so they survive type changes.
    if (fieldList.children.length === 0) {
        addField();
    } else {
        document.querySelectorAll(".field-row").forEach(row => {
            const nameInput = row.querySelector(".field-name");
            if (nameInput) nameInput.dataset.userEdited = "true";
            handleDataTypeChange(row.querySelector(".data-type"));
        });
    }

    addFieldBtn.addEventListener("click", () => addField());
    generateBtn.addEventListener("click", () => generateData(false));
    previewBtn.addEventListener("click", previewData);
    generateFromPreviewBtn.addEventListener("click", () => generateData(true));

    // Event delegation: type change + name-edit tracking + remove.
    fieldList.addEventListener("change", event => {
        if (event.target.classList.contains("data-type")) {
            const typeSelect = event.target;
            const fieldRow = typeSelect.closest(".field-row");
            handleDataTypeChange(typeSelect);

            const nameInput = fieldRow?.querySelector(".field-name");
            // Only overwrite the name if the user hasn't customized it.
            if (nameInput && nameInput.dataset.userEdited !== "true") {
                nameInput.value = suggestFieldName(typeSelect.value);
            }
        }
    });

    fieldList.addEventListener("input", event => {
        if (event.target.classList.contains("field-name")) {
            event.target.dataset.userEdited = "true";
        }
    });

    fieldList.addEventListener("click", event => {
        const btn = event.target.closest(".remove-btn");
        if (btn) removeField(btn);
    });

    // Theme toggle.
    const themeToggle = document.querySelector(".theme-toggle");
    themeToggle.addEventListener("click", () => {
        const isDark = document.body.classList.contains("theme-dark");
        const next = isDark ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem("selectedTheme", next);
    });

    const saved = localStorage.getItem("selectedTheme");
    if (saved) applyTheme(saved);
});
