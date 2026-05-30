"use strict";

// ---- i18n dictionaries ----------------------------------------------------

const I18N = {
    en: {
        "lang.label": "中",
        "lang.title": "切换中文",

        "header.eyebrow": "A small machine for synthetic data",
        "header.tagline": "Sketch a schema. Pour out as many rows as you need — in CSV, JSON, XML, SQL, or Excel.",
        "header.meta.types": "15 types",
        "header.meta.formats": "5 formats",
        "header.meta.telemetry": "0 telemetry",

        "schema.title": "Schema",
        "schema.field_name": "Field name",
        "schema.type": "Type",
        "schema.field_placeholder": "field_name",
        "schema.values_placeholder": "value1, value2, value3",
        "schema.blank_placeholder": "Blank %",
        "schema.null_label": "null",

        "toolbar.infer": "Infer",
        "toolbar.import": "Import",
        "toolbar.export": "Export",
        "toolbar.share": "Share",
        "toolbar.infer.title": "Infer from SQL, JSON, or TypeScript",
        "toolbar.import.title": "Import schema JSON file",
        "toolbar.export.title": "Download schema as JSON",
        "toolbar.share.title": "Copy a shareable URL",

        "btn.add_field": "Add another field",
        "btn.preview": "Preview",
        "btn.generate": "Generate",
        "btn.close": "Close",
        "btn.cancel": "Cancel",
        "btn.parse": "Parse & replace",
        "btn.toggle_theme": "Toggle theme",
        "btn.drag_handle": "Drag to reorder",
        "btn.remove_field": "Remove field",

        "output.rows": "Rows",
        "output.format": "Format",

        "modal.preview.title": "Preview",
        "modal.infer.title": "Infer schema",
        "modal.infer.intro": "Paste a CREATE TABLE statement, a JSON sample, or a TypeScript interface or type alias. We'll guess sensible field types and replace your current schema.",
        "modal.infer.tab.sql": "SQL DDL",
        "modal.infer.tab.json": "JSON sample",
        "modal.infer.tab.typescript": "TypeScript",

        "footer.oss": "Open source · MIT",

        "schema.template.hint.prefix": "Reference other fields with",
        "schema.template.hint.filters": "Filters",
        "schema.template.hint.suffix": "— chain with",

        "toast.exported": "Schema exported",
        "toast.imported_one": "Imported 1 field",
        "toast.imported_many": "Imported {n} fields",
        "toast.inferred_one": "Inferred 1 field",
        "toast.inferred_many": "Inferred {n} fields",
        "toast.shared": "Share URL copied to clipboard",
        "toast.loaded_url": "Loaded schema from URL",
        "toast.download_started": "Download started",
        "toast.no_recognized": "No fields recognized",
        "toast.copy_failed": "Could not copy to clipboard",
        "toast.paste_first": "Paste some source first",
        "toast.cannot_import": "Could not import: {message}",
        "toast.no_fields_in_file": "File does not contain a fields array",
        "toast.preview_prefix": "Preview error: ",
        "toast.generate_prefix": "Error generating data: ",
        "toast.infer_prefix": "Inference error: ",
        "toast.flask_hint": " Make sure the Flask server is running.",

        "error.add_field": "Please add at least one field",
        "error.field_name_required": "Field #{n} requires a name",
        "error.custom_list_empty": 'Custom List field "{name}" requires at least one value',
        "error.blank_range": 'Blank percentage for "{name}" must be 0-100',
        "error.null_range": 'Null % for "{name}" must be 0-100',
        "error.template_missing": 'Template field "{name}" needs a template string',

        "preview.note.excel": 'Excel preview shown as a table. Use "Generate" to download the actual file.',
        "preview.note.format": "Showing preview in {format} format (limited to {n} rows)",
        "preview.no_data": "No data available for preview.",
    },
    zh: {
        "lang.label": "EN",
        "lang.title": "Switch to English",

        "header.eyebrow": "一个用来生成假数据的小工具",
        "header.tagline": "勾画 Schema，按需倒出任意行数 —— 支持 CSV、JSON、XML、SQL、Excel。",
        "header.meta.types": "15 种字段类型",
        "header.meta.formats": "5 种导出格式",
        "header.meta.telemetry": "0 数据采集",

        "schema.title": "Schema",
        "schema.field_name": "字段名",
        "schema.type": "类型",
        "schema.field_placeholder": "field_name",
        "schema.values_placeholder": "值1, 值2, 值3",
        "schema.blank_placeholder": "空值 %",
        "schema.null_label": "空值",

        "toolbar.infer": "反推",
        "toolbar.import": "导入",
        "toolbar.export": "导出",
        "toolbar.share": "分享",
        "toolbar.infer.title": "从 SQL、JSON 或 TypeScript 反推 schema",
        "toolbar.import.title": "导入 schema JSON 文件",
        "toolbar.export.title": "把 schema 导出为 JSON",
        "toolbar.share.title": "复制可分享的 URL",

        "btn.add_field": "添加字段",
        "btn.preview": "预览",
        "btn.generate": "生成",
        "btn.close": "关闭",
        "btn.cancel": "取消",
        "btn.parse": "解析并替换",
        "btn.toggle_theme": "切换主题",
        "btn.drag_handle": "拖动重排",
        "btn.remove_field": "删除字段",

        "output.rows": "行数",
        "output.format": "格式",

        "modal.preview.title": "预览",
        "modal.infer.title": "反推 Schema",
        "modal.infer.intro": "粘贴一段 CREATE TABLE 语句、JSON 样本，或 TypeScript interface / type 别名，自动猜出合理的字段类型并替换当前 schema。",
        "modal.infer.tab.sql": "SQL DDL",
        "modal.infer.tab.json": "JSON 样本",
        "modal.infer.tab.typescript": "TypeScript",

        "footer.oss": "开源 · MIT",

        "schema.template.hint.prefix": "用",
        "schema.template.hint.filters": "可用 filter",
        "schema.template.hint.suffix": "用",

        "toast.exported": "Schema 已导出",
        "toast.imported_one": "已导入 1 个字段",
        "toast.imported_many": "已导入 {n} 个字段",
        "toast.inferred_one": "已反推出 1 个字段",
        "toast.inferred_many": "已反推出 {n} 个字段",
        "toast.shared": "分享链接已复制到剪贴板",
        "toast.loaded_url": "已从 URL 加载 schema",
        "toast.download_started": "开始下载",
        "toast.no_recognized": "没有识别到字段",
        "toast.copy_failed": "复制到剪贴板失败",
        "toast.paste_first": "先粘贴一段源",
        "toast.cannot_import": "导入失败：{message}",
        "toast.no_fields_in_file": "文件不包含 fields 数组",
        "toast.preview_prefix": "预览出错：",
        "toast.generate_prefix": "生成出错：",
        "toast.infer_prefix": "反推出错：",
        "toast.flask_hint": " 请确认 Flask 服务正在运行。",

        "error.add_field": "请至少添加一个字段",
        "error.field_name_required": "第 {n} 个字段需要填字段名",
        "error.custom_list_empty": "自定义列表字段「{name}」至少需要一个值",
        "error.blank_range": "「{name}」的空值百分比必须在 0-100",
        "error.null_range": "「{name}」的 Null % 必须在 0-100",
        "error.template_missing": "模板字段「{name}」需要填写模板字符串",

        "preview.note.excel": "Excel 在此以表格预览。点「生成」下载实际文件。",
        "preview.note.format": "以 {format} 格式预览（限 {n} 行）",
        "preview.no_data": "没有可预览的数据。",
    },
};

const TYPE_LABELS = {
    en: {
        "Row Number": "Row Number", "First Name": "First Name", "Last Name": "Last Name",
        "Full Name": "Full Name", "Email Address": "Email Address", "Gender": "Gender",
        "IP Address v4": "IP Address v4", "Phone Number": "Phone Number",
        "City": "City", "Country": "Country", "Date": "Date", "Number": "Number",
        "Decimal": "Decimal", "Custom List": "Custom List", "Blank/Null": "Blank/Null",
        "Template": "Template",
    },
    zh: {
        "Row Number": "行号", "First Name": "名", "Last Name": "姓",
        "Full Name": "全名", "Email Address": "邮箱", "Gender": "性别",
        "IP Address v4": "IPv4 地址", "Phone Number": "电话",
        "City": "城市", "Country": "国家", "Date": "日期", "Number": "整数",
        "Decimal": "小数", "Custom List": "自定义列表", "Blank/Null": "空值/Null",
        "Template": "模板",
    },
};

const TEMPLATE_FILTERS = ["lower", "upper", "title", "slug", "nospace", "initial", "digits", "trim"];

let currentLang = "en";

function t(key, vars = {}) {
    const dict = I18N[currentLang] || I18N.en;
    let str = dict[key] || I18N.en[key] || key;
    for (const [k, v] of Object.entries(vars)) {
        str = str.split(`{${k}}`).join(String(v));
    }
    return str;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function setLanguage(lang) {
    if (!I18N[lang]) lang = "en";
    currentLang = lang;
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.body.classList.toggle("lang-zh", lang === "zh");

    document.querySelectorAll("[data-i18n]").forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        el.title = t(el.dataset.i18nTitle);
    });

    // Re-label type dropdowns: option value stays English, label is translated.
    const labels = TYPE_LABELS[lang] || TYPE_LABELS.en;
    document.querySelectorAll(".data-type option").forEach(opt => {
        opt.textContent = labels[opt.value] || opt.value;
    });

    // Re-render template hints (they embed <code> tags).
    renderTemplateHints();

    // Update language toggle button label/title.
    const langLabel = document.getElementById("langLabel");
    const langBtn = document.getElementById("langToggle");
    if (langLabel) langLabel.textContent = t("lang.label");
    if (langBtn) langBtn.title = t("lang.title");

    try { localStorage.setItem(LANG_KEY, lang); } catch (_) { /* ignore */ }
}

function renderTemplateHints() {
    const filtersHtml = TEMPLATE_FILTERS.map(f => `<code>${escapeHtml(f)}</code>`).join(", ");
    const token = "<code>{{name}}</code>";
    const pipe = "<code>|</code>";
    const html = `${escapeHtml(t("schema.template.hint.prefix"))} ${token}. ` +
        `${escapeHtml(t("schema.template.hint.filters"))}: ${filtersHtml} ${escapeHtml(t("schema.template.hint.suffix"))} ${pipe}.`;
    document.querySelectorAll("[data-template-hint]").forEach(el => {
        el.innerHTML = html;
    });
}

// ---- Constants ------------------------------------------------------------

const DATA_TYPES = [
    "Row Number", "First Name", "Last Name", "Full Name", "Email Address",
    "Gender", "IP Address v4", "Phone Number", "City", "Country", "Date",
    "Number", "Decimal", "Custom List", "Blank/Null", "Template",
];

const FORMAT_EXTENSIONS = {
    CSV: "csv", JSON: "json", XML: "xml", SQL: "sql", EXCEL: "xlsx",
};

const STORAGE_KEY = "mdf.schema.v1";
const LANG_KEY = "mdf.lang.v1";
const TEMPLATE_PLACEHOLDER = "{{first_name|lower}}.{{last_name|lower}}@example.com";

let fieldCounter = 0;
let restoring = false;

const fieldList = document.getElementById("field-list");
const addFieldBtn = document.getElementById("addFieldBtn");
const generateBtn = document.getElementById("generateBtn");
const previewBtn = document.getElementById("previewBtn");
const generateFromPreviewBtn = document.getElementById("generateFromPreviewBtn");
const previewNumRows = document.getElementById("previewNumRows");
const previewModalElement = document.getElementById("previewModal");
const inferModalElement = document.getElementById("inferModal");
const importFileInput = document.getElementById("importFileInput");

new Sortable(fieldList, {
    animation: 150,
    handle: ".drag-handle",
    ghostClass: "sortable-ghost",
    onEnd: () => persistSchema(),
});

// ---- Field rendering ------------------------------------------------------

function suggestFieldName(typeName) {
    if (typeName === "Row Number") return "id";
    if (typeName === "Template") return "computed";
    return typeName.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
}

function buildFieldRow(fieldId, initial = {}) {
    const fieldRow = document.createElement("div");
    fieldRow.className = "field-row";
    fieldRow.dataset.fieldId = fieldId;
    const initialType = initial.type || "Row Number";
    const initialName = initial.name ?? suggestFieldName(initialType);
    const labels = TYPE_LABELS[currentLang] || TYPE_LABELS.en;

    fieldRow.innerHTML = `
        <div class="drag-handle" title="${escapeHtml(t("btn.drag_handle"))}"
             data-i18n-title="btn.drag_handle"></div>
        <div>
            <input type="text" class="form-control form-control-sm field-name"
                   id="${fieldId}-name" name="${fieldId}-name"
                   placeholder="${escapeHtml(t("schema.field_placeholder"))}"
                   data-i18n-placeholder="schema.field_placeholder"
                   required autocomplete="off">
        </div>
        <div class="field-input-stack">
            <select class="form-select form-select-sm data-type"
                    id="${fieldId}-type" name="${fieldId}-type">
                ${DATA_TYPES.map(t => `<option value="${t}">${escapeHtml(labels[t] || t)}</option>`).join("")}
            </select>
            <input type="text" class="form-control form-control-sm custom-list-input"
                   id="${fieldId}-custom-list" name="${fieldId}-custom-list"
                   placeholder="${escapeHtml(t("schema.values_placeholder"))}"
                   data-i18n-placeholder="schema.values_placeholder">
            <input type="number" class="form-control form-control-sm blank-percentage-input"
                   id="${fieldId}-blank-percentage" name="${fieldId}-blank-percentage"
                   placeholder="${escapeHtml(t("schema.blank_placeholder"))}"
                   data-i18n-placeholder="schema.blank_placeholder"
                   min="0" max="100">
            <input type="text" class="form-control form-control-sm template-input"
                   id="${fieldId}-template" name="${fieldId}-template"
                   placeholder="${escapeHtml(TEMPLATE_PLACEHOLDER)}">
            <div class="template-hint" data-template-hint></div>
            <div class="blank-modifier">
                <label for="${fieldId}-null-pct" data-i18n="schema.null_label">${escapeHtml(t("schema.null_label"))}</label>
                <input type="number" class="form-control form-control-sm null-modifier"
                       id="${fieldId}-null-pct" min="0" max="100" value="0">
                <span>%</span>
            </div>
        </div>
        <div class="remove-btn" data-field-id="${fieldId}"
             title="${escapeHtml(t("btn.remove_field"))}"
             data-i18n-title="btn.remove_field">
            <i class="bi bi-x-lg"></i>
        </div>
    `;

    const nameInput = fieldRow.querySelector(".field-name");
    nameInput.value = initialName;
    nameInput.dataset.userEdited = initial.name ? "true" : "false";

    const typeSelect = fieldRow.querySelector(".data-type");
    typeSelect.value = initialType;

    if (initial.values && Array.isArray(initial.values)) {
        fieldRow.querySelector(".custom-list-input").value = initial.values.join(", ");
    }
    if (initial.template) {
        fieldRow.querySelector(".template-input").value = initial.template;
    }
    if (initial.blank_percentage != null) {
        fieldRow.querySelector(".null-modifier").value = initial.blank_percentage;
    }

    return fieldRow;
}

function addField(initial = {}) {
    const fieldId = `field-${Date.now()}-${fieldCounter++}`;
    const fieldRow = buildFieldRow(fieldId, initial);
    fieldList.appendChild(fieldRow);
    handleDataTypeChange(fieldRow.querySelector(".data-type"));
    renderTemplateHints();
    if (!restoring) persistSchema();
}

function removeField(button) {
    button.closest(".field-row").remove();
    persistSchema();
}

function handleDataTypeChange(select) {
    const fieldRow = select.closest(".field-row");
    const customListInput = fieldRow.querySelector(".custom-list-input");
    const blankPercentageInput = fieldRow.querySelector(".blank-percentage-input");
    const templateInput = fieldRow.querySelector(".template-input");
    const templateHint = fieldRow.querySelector(".template-hint");

    customListInput.style.display = "none";
    blankPercentageInput.style.display = "none";
    templateInput.style.display = "none";
    if (templateHint) templateHint.style.display = "none";

    if (select.value === "Custom List") {
        customListInput.style.display = "block";
    } else if (select.value === "Blank/Null") {
        blankPercentageInput.style.display = "block";
    } else if (select.value === "Template") {
        templateInput.style.display = "block";
        if (templateHint) templateHint.style.display = "block";
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
        throw new Error(t("error.add_field"));
    }

    fieldRows.forEach((row, index) => {
        const nameInput = row.querySelector(".field-name");
        const typeSelect = row.querySelector(".data-type");
        const fieldName = nameInput.value.trim();

        if (!fieldName) {
            throw new Error(t("error.field_name_required", { n: index + 1 }));
        }

        const field = { name: fieldName, type: typeSelect.value };

        if (field.type === "Custom List") {
            const values = row.querySelector(".custom-list-input").value
                .split(",").map(v => v.trim()).filter(Boolean);
            if (values.length === 0) {
                throw new Error(t("error.custom_list_empty", { name: fieldName }));
            }
            field.values = values;
        } else if (field.type === "Blank/Null") {
            const pct = parseInt(row.querySelector(".blank-percentage-input").value, 10) || 0;
            if (pct < 0 || pct > 100) {
                throw new Error(t("error.blank_range", { name: fieldName }));
            }
            field.blank_percentage = pct;
        } else if (field.type === "Template") {
            const template = row.querySelector(".template-input").value.trim();
            if (!template) {
                throw new Error(t("error.template_missing", { name: fieldName }));
            }
            field.template = template;
        }

        const nullPct = parseInt(row.querySelector(".null-modifier").value, 10) || 0;
        if (nullPct > 0) {
            if (nullPct > 100) {
                throw new Error(t("error.null_range", { name: fieldName }));
            }
            field.blank_percentage = nullPct;
        }

        schema.fields.push(field);
    });

    return schema;
}

// ---- Persistence ----------------------------------------------------------

function getCurrentFields() {
    try {
        return collectSchema(1).fields;
    } catch {
        return Array.from(document.querySelectorAll(".field-row")).map(row => ({
            name: row.querySelector(".field-name")?.value || "",
            type: row.querySelector(".data-type")?.value || "Row Number",
        }));
    }
}

let persistTimer = null;
function persistSchema() {
    if (restoring) return;
    clearTimeout(persistTimer);
    persistTimer = setTimeout(() => {
        try {
            const fields = getCurrentFields();
            localStorage.setItem(STORAGE_KEY, JSON.stringify({ fields }));
        } catch (err) {
            console.warn("Failed to persist schema:", err);
        }
    }, 250);
}

function restoreSchema(fields) {
    restoring = true;
    try {
        fieldList.innerHTML = "";
        fields.forEach(f => addField(f));
    } finally {
        restoring = false;
    }
}

function encodeSchemaForUrl(fields) {
    const json = JSON.stringify({ fields });
    return btoa(unescape(encodeURIComponent(json)))
        .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function decodeSchemaFromUrl(encoded) {
    const padded = encoded.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(escape(atob(padded)));
    return JSON.parse(json);
}

function copyShareUrl() {
    const fields = getCurrentFields();
    const encoded = encodeSchemaForUrl(fields);
    const url = `${location.origin}${location.pathname}#s=${encoded}`;
    navigator.clipboard.writeText(url).then(
        () => showToast(t("toast.shared"), "success"),
        () => showToast(t("toast.copy_failed"))
    );
}

function exportSchema() {
    const fields = getCurrentFields();
    const blob = new Blob([JSON.stringify({ fields }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `schema_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
    showToast(t("toast.exported"), "success");
}

function importSchemaFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const parsed = JSON.parse(e.target.result);
            const fields = Array.isArray(parsed) ? parsed : parsed.fields;
            if (!Array.isArray(fields) || fields.length === 0) {
                throw new Error(t("toast.no_fields_in_file"));
            }
            restoreSchema(fields);
            persistSchema();
            const n = fields.length;
            showToast(n === 1 ? t("toast.imported_one") : t("toast.imported_many", { n }), "success");
        } catch (err) {
            showToast(t("toast.cannot_import", { message: err.message }));
        }
    };
    reader.readAsText(file);
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
    const toast = new bootstrap.Toast(toastEl, { delay: variant === "danger" ? 6000 : 3000 });
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

// ---- Schema inference UI --------------------------------------------------
async function runInfer() {
    const activeTab = document.querySelector("#inferTabs .nav-link.active");
    const kind = activeTab?.dataset.kind || "sql";
    const source = document.getElementById(`infer-${kind}`).value;
    if (!source.trim()) {
        showToast(t("toast.paste_first"));
        return;
    }
    const button = document.getElementById("inferParseBtn");
    await withBusy(button, async () => {
        try {
            const response = await postJson("/infer-schema", { kind, source });
            const { fields } = await response.json();
            if (!fields || fields.length === 0) {
                showToast(t("toast.no_recognized"));
                return;
            }
            restoreSchema(fields);
            persistSchema();
            bootstrap.Modal.getInstance(inferModalElement)?.hide();
            const n = fields.length;
            showToast(n === 1 ? t("toast.inferred_one") : t("toast.inferred_many", { n }), "success");
        } catch (err) {
            showToast(t("toast.infer_prefix") + err.message);
        }
    });
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
            const hint = error.message.includes("Failed to fetch") ? t("toast.flask_hint") : "";
            showToast(t("toast.preview_prefix") + error.message + hint);
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
            previewContent.textContent = t("preview.no_data");
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
        ? t("preview.note.excel")
        : t("preview.note.format", { format, n: numRows });
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
            showToast(t("toast.download_started"), "success");
        } catch (error) {
            showToast(t("toast.generate_prefix") + error.message);
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
    // Initial language: stored > browser preference > English.
    let initialLang = "en";
    try {
        const stored = localStorage.getItem(LANG_KEY);
        if (stored === "en" || stored === "zh") {
            initialLang = stored;
        } else if ((navigator.language || "").toLowerCase().startsWith("zh")) {
            initialLang = "zh";
        }
    } catch (_) { /* ignore */ }
    setLanguage(initialLang);

    ["numRows", "previewNumRows"].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener("input", function () {
            if (parseInt(this.value, 10) <= 0) this.value = 1;
        });
    });

    previewModalElement.addEventListener("hidden.bs.modal", () => {
        document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
        document.body.classList.remove("modal-open");
        document.body.style.overflow = "";
        document.body.style.paddingRight = "";
    });

    // ---- Restore: URL hash > localStorage > default ----
    let restored = false;
    const hashMatch = location.hash.match(/[#&]s=([^&]+)/);
    if (hashMatch) {
        try {
            const parsed = decodeSchemaFromUrl(hashMatch[1]);
            if (parsed.fields && parsed.fields.length) {
                restoreSchema(parsed.fields);
                showToast(t("toast.loaded_url"), "success");
                restored = true;
            }
        } catch (err) {
            console.warn("Bad hash schema:", err);
        }
    }
    if (!restored) {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (parsed.fields && parsed.fields.length) {
                    restoreSchema(parsed.fields);
                    restored = true;
                }
            }
        } catch (err) {
            console.warn("Bad stored schema:", err);
        }
    }

    if (!restored) {
        if (fieldList.children.length === 0) {
            addField();
        } else {
            document.querySelectorAll(".field-row").forEach(row => {
                const nameInput = row.querySelector(".field-name");
                if (nameInput) nameInput.dataset.userEdited = "true";
                handleDataTypeChange(row.querySelector(".data-type"));
            });
            renderTemplateHints();
        }
    }

    // Toolbar wiring
    addFieldBtn.addEventListener("click", () => addField());
    generateBtn.addEventListener("click", () => generateData(false));
    previewBtn.addEventListener("click", previewData);
    generateFromPreviewBtn.addEventListener("click", () => generateData(true));

    document.getElementById("exportBtn")?.addEventListener("click", exportSchema);
    document.getElementById("shareBtn")?.addEventListener("click", copyShareUrl);
    document.getElementById("importBtn")?.addEventListener("click", () => importFileInput.click());
    importFileInput?.addEventListener("change", (e) => {
        if (e.target.files[0]) {
            importSchemaFile(e.target.files[0]);
            e.target.value = "";
        }
    });

    document.getElementById("inferBtn")?.addEventListener("click", () => {
        bootstrap.Modal.getOrCreateInstance(inferModalElement).show();
    });
    document.getElementById("inferParseBtn")?.addEventListener("click", runInfer);

    // Tab switching in infer modal
    document.querySelectorAll("#inferTabs .nav-link").forEach(tab => {
        tab.addEventListener("click", (e) => {
            e.preventDefault();
            document.querySelectorAll("#inferTabs .nav-link").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".infer-pane").forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(`infer-pane-${tab.dataset.kind}`).classList.add("active");
        });
    });

    // Field interactions
    fieldList.addEventListener("change", event => {
        if (event.target.classList.contains("data-type")) {
            const typeSelect = event.target;
            const fieldRow = typeSelect.closest(".field-row");
            handleDataTypeChange(typeSelect);

            const nameInput = fieldRow?.querySelector(".field-name");
            if (nameInput && nameInput.dataset.userEdited !== "true") {
                nameInput.value = suggestFieldName(typeSelect.value);
            }
            persistSchema();
        }
    });

    fieldList.addEventListener("input", event => {
        const target = event.target;
        if (target.classList.contains("field-name")) {
            target.dataset.userEdited = "true";
        }
        if (target.classList.contains("field-name") ||
            target.classList.contains("template-input") ||
            target.classList.contains("custom-list-input") ||
            target.classList.contains("null-modifier") ||
            target.classList.contains("blank-percentage-input")) {
            persistSchema();
        }
    });

    fieldList.addEventListener("click", event => {
        const btn = event.target.closest(".remove-btn");
        if (btn) removeField(btn);
    });

    // Language toggle
    document.getElementById("langToggle")?.addEventListener("click", () => {
        setLanguage(currentLang === "zh" ? "en" : "zh");
    });

    // Theme
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
