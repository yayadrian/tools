const STORAGE_KEY = "working-hours-calculator:v1";
const DAY_LABELS = [
  "Week 1 - Monday",
  "Week 1 - Tuesday",
  "Week 1 - Wednesday",
  "Week 1 - Thursday",
  "Week 1 - Friday",
  "Week 2 - Monday",
  "Week 2 - Tuesday",
  "Week 2 - Wednesday",
  "Week 2 - Thursday",
  "Week 2 - Friday",
];

const defaultSettings = () => ({
  hoursPerWeek: 37.5,
  targetFortnightHours: 75,
  defaultBreakMinutes: 60,
});

const defaultDay = (breakMinutes) => ({
  start: "09:00",
  end: "17:30",
  breakMinutes,
});

const defaultPattern = (settings) => ({
  id: crypto.randomUUID(),
  name: "Standard",
  days: Array.from({ length: 10 }, () => defaultDay(settings.defaultBreakMinutes)),
});

let state = loadState();
const _patternNameDebounceTimers = new Map();

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      const settings = defaultSettings();
      return { settings, patterns: [defaultPattern(settings)] };
    }
    const parsed = JSON.parse(raw);
    // Basic shape validation and defaults
    const settings = {
      ...defaultSettings(),
      ...(parsed.settings || {}),
    };
    const patterns = Array.isArray(parsed.patterns) && parsed.patterns.length
      ? parsed.patterns
      : [defaultPattern(settings)];
    return { settings, patterns };
  } catch (err) {
    console.error("Failed to load state, using defaults", err);
    const settings = defaultSettings();
    return { settings, patterns: [defaultPattern(settings)] };
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function parseTimeToMinutes(value) {
  if (typeof value !== "string") return null;
  const match = /^([01]?\d|2[0-3]):([0-5]\d)$/.exec(value.trim());
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  return hours * 60 + minutes;
}

function minutesToHoursDecimal(minutes) {
  return (minutes / 60).toFixed(2);
}

function calcDaily(day) {
  const start = parseTimeToMinutes(day.start);
  const end = parseTimeToMinutes(day.end);
  const breakMinutes = Number(day.breakMinutes);

  if (Number.isNaN(breakMinutes) || breakMinutes < 0) {
    return { valid: false, hours: null, message: "Break must be non-negative" };
  }
  // Treat a day with no times as a zero-hour (valid) day off
  if (start === null && end === null) {
    return { valid: true, hours: 0 };
  }
  if (start === null || end === null) {
    return { valid: false, hours: null, message: "Enter start and end time" };
  }
  if (end <= start) {
    return { valid: false, hours: null, message: "End must be after start" };
  }
  const totalMinutes = end - start;
  if (breakMinutes >= totalMinutes) {
    return { valid: false, hours: null, message: "Break too long for shift" };
  }
  const workMinutes = totalMinutes - breakMinutes;
  return { valid: true, hours: Number(minutesToHoursDecimal(workMinutes)) };
}

function calcPattern(pattern, settings) {
  const dayResults = pattern.days.map(calcDaily);

  const week1 = dayResults.slice(0, 5).reduce((sum, d) => (d.valid ? sum + d.hours : sum), 0);
  const week2 = dayResults.slice(5).reduce((sum, d) => (d.valid ? sum + d.hours : sum), 0);
  const fortnight = week1 + week2;
  const gap = Number((fortnight - settings.targetFortnightHours).toFixed(2));
  const hasInvalid = dayResults.some((d) => !d.valid);

  return { dayResults, week1, week2, fortnight, gap, hasInvalid };
}

function updateSettings(key, value) {
  const newSettings = { ...state.settings, [key]: value };

  // If hoursPerWeek changes and target matches prior derived, update target too
  if (key === "hoursPerWeek") {
    const priorDerived = Number((state.settings.hoursPerWeek * 2).toFixed(2));
    const currentTarget = Number(state.settings.targetFortnightHours);
    const newDerived = Number((value * 2).toFixed(2));
    if (currentTarget === priorDerived) {
      newSettings.targetFortnightHours = newDerived;
    }
  }

  state = { ...state, settings: newSettings };
  persist();
  render();
}

function addPattern(prefill = true) {
  const settings = state.settings;
  const pattern = prefill
    ? defaultPattern(settings)
    : {
        id: crypto.randomUUID(),
        name: "New pattern",
        days: Array.from({ length: 10 }, () => ({
          start: "",
          end: "",
          breakMinutes: settings.defaultBreakMinutes,
        })),
      };

  state = { ...state, patterns: [...state.patterns, pattern] };
  persist();
  render();
  showToast("Pattern added");
}

function duplicatePattern(id) {
  const existing = state.patterns.find((p) => p.id === id);
  if (!existing) return;
  const copy = {
    ...existing,
    id: crypto.randomUUID(),
    name: `${existing.name} (copy)`,
    days: existing.days.map((d) => ({ ...d })),
  };
  state = { ...state, patterns: [...state.patterns, copy] };
  persist();
  render();
  showToast("Pattern duplicated");
}

function deletePattern(id) {
  const pattern = state.patterns.find((p) => p.id === id);
  if (!pattern) return;
  if (!confirm(`Delete pattern "${pattern.name}"?`)) return;
  state = { ...state, patterns: state.patterns.filter((p) => p.id !== id) };
  if (state.patterns.length === 0) {
    state.patterns.push(defaultPattern(state.settings));
  }
  persist();
  render();
  showToast("Pattern deleted");
}

function renamePattern(id, name) {
  state = {
    ...state,
    patterns: state.patterns.map((p) => (p.id === id ? { ...p, name } : p)),
  };
  persist();
  render();
}

function saveFocus() {
  const el = document.activeElement;
  if (!el || el.tagName !== "INPUT") return null;
  const card = el.closest(".pattern-card");
  return {
    patternId: card?.dataset.patternId ?? null,
    role: el.dataset.role ?? null,
    idx: el.dataset.idx ?? null,
    selectionStart: typeof el.selectionStart === "number" ? el.selectionStart : null,
    selectionEnd: typeof el.selectionEnd === "number" ? el.selectionEnd : null,
  };
}

function restoreFocus(saved) {
  if (!saved?.patternId || !saved?.role) return;
  const card = document.querySelector(`[data-pattern-id="${saved.patternId}"]`);
  if (!card) return;
  const selector =
    saved.idx != null
      ? `[data-role="${saved.role}"][data-idx="${saved.idx}"]`
      : `[data-role="${saved.role}"]`;
  const el = card.querySelector(selector);
  if (!el) return;
  el.focus();
  if (el.setSelectionRange && saved.selectionStart != null) {
    el.setSelectionRange(saved.selectionStart, saved.selectionEnd ?? saved.selectionStart);
  }
}

function updateDayField(patternId, dayIndex, field, value) {
  state = {
    ...state,
    patterns: state.patterns.map((p) =>
      p.id === patternId
        ? {
            ...p,
            days: p.days.map((d, idx) =>
              idx === dayIndex ? { ...d, [field]: field === "breakMinutes" ? Number(value) : value } : d
            ),
          }
        : p
    ),
  };
  persist();
  render();
}

function renderSettings() {
  const { hoursPerWeek, targetFortnightHours, defaultBreakMinutes } = state.settings;
  const hoursInput = document.querySelector("#hoursPerWeek");
  const targetInput = document.querySelector("#targetFortnightHours");
  const breakInput = document.querySelector("#defaultBreakMinutes");
  const errorsEl = document.querySelector("#settings-errors");

  hoursInput.value = hoursPerWeek;
  targetInput.value = targetFortnightHours;
  breakInput.value = defaultBreakMinutes;

  const errors = [];
  if (!(hoursPerWeek > 0)) errors.push("Hours per week must be greater than 0");
  if (!(targetFortnightHours > 0)) errors.push("Target fortnight hours must be greater than 0");
  if (!(defaultBreakMinutes >= 0)) errors.push("Default break must be non-negative");
  errorsEl.textContent = errors.join(" • ");
}

function renderPatterns() {
  const container = document.querySelector("#patterns-container");
  container.innerHTML = "";

  state.patterns.forEach((pattern) => {
    const { dayResults, week1, week2, fortnight, gap, hasInvalid } = calcPattern(
      pattern,
      state.settings
    );

    const card = document.createElement("article");
    card.className = "pattern-card";
    card.dataset.patternId = pattern.id;

    const header = document.createElement("div");
    header.className = "pattern-header";

    header.innerHTML = `
      <div class="pattern-name">
        <label class="field">
          <span>Name</span>
          <input type="text" value="${pattern.name}" data-role="pattern-name" />
        </label>
        ${hasInvalid ? '<span class="error-text">Pattern has invalid days</span>' : ""}
      </div>
      <div class="button-group">
        <button class="btn ghost small" data-role="duplicate">Duplicate</button>
        <button class="btn ghost small" data-role="delete">Delete</button>
      </div>
    `;

    const tableWrapper = document.createElement("div");
    tableWrapper.className = "table-wrapper";

    const table = document.createElement("table");
    table.className = "day-grid";
    const tbody = document.createElement("tbody");

    // Header
    table.innerHTML = `
      <thead>
        <tr>
          <th>Day</th>
          <th>Start</th>
          <th>End</th>
          <th>Break (min)</th>
          <th>Hours</th>
        </tr>
      </thead>
    `;

    pattern.days.forEach((day, idx) => {
      const result = dayResults[idx];
      const row = document.createElement("tr");
      if (!result.valid) row.classList.add("invalid-row");

      row.innerHTML = `
        <td>${DAY_LABELS[idx]}</td>
        <td><input type="time" value="${day.start || ""}" data-role="start" data-idx="${idx}" /></td>
        <td><input type="time" value="${day.end || ""}" data-role="end" data-idx="${idx}" /></td>
        <td><input type="number" min="0" step="5" value="${day.breakMinutes ?? ""}" data-role="break" data-idx="${idx}" /></td>
        <td class="hours-cell">${result.valid ? result.hours.toFixed(2) : "—"}</td>
      `;

      if (!result.valid && result.message) {
        const msgRow = document.createElement("tr");
        msgRow.className = "invalid-row";
        msgRow.innerHTML = `<td colspan="5" class="error-text">${result.message}</td>`;
        tbody.appendChild(row);
        tbody.appendChild(msgRow);
      } else {
        tbody.appendChild(row);
      }
    });

    const summaryRow = document.createElement("tr");
    summaryRow.className = "summary-row";
    summaryRow.innerHTML = `
      <td>Totals</td>
      <td colspan="1">Week 1: ${week1.toFixed(2)}</td>
      <td colspan="1">Week 2: ${week2.toFixed(2)}</td>
      <td colspan="1">Fortnight: ${fortnight.toFixed(2)}</td>
      <td>${formatGap(gap)}</td>
    `;
    tbody.appendChild(summaryRow);

    table.appendChild(tbody);
    tableWrapper.appendChild(table);

    card.appendChild(header);
    const body = document.createElement("div");
    body.className = "panel-body";
    body.appendChild(tableWrapper);
    card.appendChild(body);
    container.appendChild(card);
  });

  bindPatternEvents();
}

function formatGap(gap) {
  const cls = gap === 0 ? "gap-zero" : gap > 0 ? "gap-positive" : "gap-negative";
  const sign = gap > 0 ? "+" : "";
  return `<span class="${cls}">${sign}${gap.toFixed(2)}</span>`;
}

function bindPatternEvents() {
  document.querySelectorAll("[data-role='pattern-name']").forEach((input) => {
    input.addEventListener("input", (e) => {
      const patternId = e.target.closest(".pattern-card").dataset.patternId;
      // Update in-memory immediately so other updates see latest name,
      // but debounce persistence + re-render to avoid nuking focus on every keystroke.
      state = {
        ...state,
        patterns: state.patterns.map((p) => (p.id === patternId ? { ...p, name: e.target.value } : p)),
      };

      clearTimeout(_patternNameDebounceTimers.get(patternId));
      _patternNameDebounceTimers.set(
        patternId,
        setTimeout(() => {
          persist();
          render();
        }, 300)
      );
    });
  });

  document.querySelectorAll("[data-role='duplicate']").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const patternId = e.target.closest(".pattern-card").dataset.patternId;
      duplicatePattern(patternId);
    });
  });

  document.querySelectorAll("[data-role='delete']").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const patternId = e.target.closest(".pattern-card").dataset.patternId;
      deletePattern(patternId);
    });
  });

  document.querySelectorAll(".pattern-card input[type='time']").forEach((input) => {
    input.addEventListener("change", (e) => {
      const patternId = e.target.closest(".pattern-card").dataset.patternId;
      const dayIndex = Number(e.target.dataset.idx);
      const field = e.target.dataset.role;
      updateDayField(patternId, dayIndex, field, e.target.value);
    });
  });

  document.querySelectorAll(".pattern-card input[type='number']").forEach((input) => {
    input.addEventListener("change", (e) => {
      const patternId = e.target.closest(".pattern-card").dataset.patternId;
      const dayIndex = Number(e.target.dataset.idx);
      updateDayField(patternId, dayIndex, "breakMinutes", Number(e.target.value));
    });
  });
}

function renderComparison() {
  const tbody = document.querySelector("#comparison-table tbody");
  tbody.innerHTML = "";

  const rows = state.patterns.map((p) => {
    const { week1, week2, fortnight, gap, hasInvalid } = calcPattern(p, state.settings);
    return { id: p.id, name: p.name, week1, week2, fortnight, gap, hasInvalid };
  });

  const validRows = rows.filter((r) => !r.hasInvalid);
  let highlightId = null;
  if (validRows.length) {
    highlightId = validRows.reduce((best, r) => {
      const bestAbs = Math.abs(rows.find((x) => x.id === best)?.gap ?? Infinity);
      const currentAbs = Math.abs(r.gap);
      return currentAbs < bestAbs ? r.id : best;
    }, validRows[0].id);
  }

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    if (r.id === highlightId) tr.classList.add("highlight");
    tr.innerHTML = `
      <td>${r.name}</td>
      <td>${r.hasInvalid ? "—" : r.week1.toFixed(2)}</td>
      <td>${r.hasInvalid ? "—" : r.week2.toFixed(2)}</td>
      <td>${r.hasInvalid ? "—" : r.fortnight.toFixed(2)}</td>
      <td>${r.hasInvalid ? '<span class="gap-negative">Invalid</span>' : formatGap(r.gap)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("toast-visible");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => toast.classList.remove("toast-visible"), 1800);
}

function bindSettingsEvents() {
  document.querySelector("#hoursPerWeek").addEventListener("change", (e) => {
    updateSettings("hoursPerWeek", Number(e.target.value));
  });
  document.querySelector("#targetFortnightHours").addEventListener("change", (e) => {
    updateSettings("targetFortnightHours", Number(e.target.value));
  });
  document.querySelector("#defaultBreakMinutes").addEventListener("change", (e) => {
    updateSettings("defaultBreakMinutes", Number(e.target.value));
  });
}

function bindGlobalActions() {
  document.querySelector("#addPatternBtn").addEventListener("click", () => addPattern(true));
}

function render() {
  const focused = saveFocus();
  renderSettings();
  renderPatterns();
  renderComparison();
  restoreFocus(focused);
}

function runInlineChecks() {
  // 37.5h per week pattern totals
  const pattern = defaultPattern(defaultSettings());
  const res = calcPattern(pattern, defaultSettings());
  if (res.fortnight !== 75) {
    console.warn("Check failed: expected 75 hours fortnight, got", res.fortnight);
  }

  // Week 2 Friday off scenario
  const custom = defaultPattern(defaultSettings());
  custom.days[9] = { ...custom.days[9], start: "", end: "", breakMinutes: 60 };
  const res2 = calcPattern(custom, defaultSettings());
  if (res2.hasInvalid || res2.fortnight !== 67.5) {
    console.warn("Check: Week2 Friday off expected 67.5 hours, got", res2.fortnight);
  }
}

function init() {
  bindSettingsEvents();
  bindGlobalActions();
  render();
  runInlineChecks();
}

init();
