const STORAGE_KEY = 'whc-state-v1';
const DAY_LABELS = [
  'Week 1 - Mon',
  'Week 1 - Tue',
  'Week 1 - Wed',
  'Week 1 - Thu',
  'Week 1 - Fri',
  'Week 2 - Mon',
  'Week 2 - Tue',
  'Week 2 - Wed',
  'Week 2 - Thu',
  'Week 2 - Fri'
];

const settingsInputs = {
  hoursPerWeek: document.getElementById('hours-per-week'),
  targetFortnight: document.getElementById('target-fortnight'),
  defaultBreak: document.getElementById('default-break'),
  resetTarget: document.getElementById('reset-target')
};
const heroStats = {
  weekly: document.getElementById('stat-weekly'),
  target: document.getElementById('stat-target'),
  break: document.getElementById('stat-break'),
  patterns: document.getElementById('stat-patterns')
};
const addPatternButton = document.getElementById('add-pattern');
const patternsContainer = document.getElementById('patterns');
const comparisonBody = document.getElementById('comparison-body');

function loadState() {
  const defaults = {
    settings: {
      hoursPerWeek: 37.5,
      targetFortnightHours: 75,
      defaultBreak: 60,
      autoTarget: true
    },
    patterns: []
  };

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return defaults;
    }
    const parsed = JSON.parse(stored);
    return {
      settings: {
        ...defaults.settings,
        ...parsed.settings,
        autoTarget: parsed.settings?.autoTarget ?? true
      },
      patterns: parsed.patterns?.length ? parsed.patterns : []
    };
  } catch (error) {
    console.warn('Falling back to defaults due to load error', error);
    return defaults;
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function minutesToDecimalHours(minutes) {
  return Math.round((minutes / 60) * 100) / 100;
}

function parseTimeToMinutes(timeString) {
  if (!timeString || !/^\d{2}:\d{2}$/.test(timeString)) return null;
  const [hours, minutes] = timeString.split(':').map(Number);
  return hours * 60 + minutes;
}

function calculateDayHours(day) {
  const startMinutes = parseTimeToMinutes(day.start);
  const endMinutes = parseTimeToMinutes(day.end);
  const breakMinutes = Number(day.breakMinutes);

  if (startMinutes === null || endMinutes === null || Number.isNaN(breakMinutes)) {
    return { valid: false, hours: null, message: 'Add start, end, and break' };
  }

  if (endMinutes <= startMinutes) {
    return { valid: false, hours: null, message: 'End must be after start' };
  }

  const duration = endMinutes - startMinutes;
  if (breakMinutes < 0 || breakMinutes >= duration) {
    return { valid: false, hours: null, message: 'Break must be less than shift length' };
  }

  const workMinutes = duration - breakMinutes;
  return {
    valid: true,
    hours: minutesToDecimalHours(workMinutes)
  };
}

function calculatePatternTotals(pattern, settings) {
  let week1 = 0;
  let week2 = 0;
  let hasInvalid = false;

  const dailyHours = pattern.days.map((day, index) => {
    const result = calculateDayHours(day);
    if (result.valid && typeof result.hours === 'number') {
      if (index < 5) {
        week1 += result.hours;
      } else {
        week2 += result.hours;
      }
    } else if (day.start || day.end || day.breakMinutes !== '') {
      hasInvalid = true;
    }
    return result;
  });

  const fortnight = Math.round((week1 + week2) * 100) / 100;
  const gap = Math.round((fortnight - Number(settings.targetFortnightHours || 0)) * 100) / 100;

  return {
    week1: Math.round(week1 * 100) / 100,
    week2: Math.round(week2 * 100) / 100,
    fortnight,
    gap,
    dailyHours,
    hasInvalid
  };
}

function createDefaultPattern(name) {
  const defaultDay = () => ({
    start: '09:00',
    end: '17:30',
    breakMinutes: state.settings.defaultBreak
  });

  return {
    id: crypto.randomUUID ? crypto.randomUUID() : `pattern-${Date.now()}-${Math.random()}`,
    name,
    days: Array.from({ length: 10 }, defaultDay)
  };
}

const state = loadState();
if (state.patterns.length === 0) {
  state.patterns.push(createDefaultPattern('Pattern 1'));
  saveState();
}

function renderSettings() {
  settingsInputs.hoursPerWeek.value = state.settings.hoursPerWeek;
  settingsInputs.targetFortnight.value = state.settings.targetFortnightHours;
  settingsInputs.defaultBreak.value = state.settings.defaultBreak;
  updateHeroStats();
}

function updateTargetFromWeekly() {
  state.settings.autoTarget = true;
  state.settings.targetFortnightHours = Math.round((Number(state.settings.hoursPerWeek) * 2) * 100) / 100;
}

function renderPatterns() {
  patternsContainer.innerHTML = '';
  updateHeroStats();

  state.patterns.forEach((pattern, patternIndex) => {
    const metrics = calculatePatternTotals(pattern, state.settings);
    const patternTemplate = document.getElementById('pattern-template');
    const node = patternTemplate.content.cloneNode(true);
    const card = node.querySelector('.pattern-card');

    const nameInput = node.querySelector('.pattern-name');
    nameInput.value = pattern.name;
    nameInput.addEventListener('input', (event) => {
      state.patterns[patternIndex].name = event.target.value;
      saveAndRender();
    });

    const duplicateBtn = node.querySelector('.duplicate');
    duplicateBtn.addEventListener('click', () => {
      const copy = JSON.parse(JSON.stringify(pattern));
      copy.id = crypto.randomUUID ? crypto.randomUUID() : `pattern-${Date.now()}-${Math.random()}`;
      copy.name = `${pattern.name} (copy)`;
      state.patterns.splice(patternIndex + 1, 0, copy);
      saveAndRender();
    });

    const deleteBtn = node.querySelector('.delete');
    deleteBtn.disabled = state.patterns.length === 1;
    deleteBtn.addEventListener('click', () => {
      if (state.patterns.length === 1) return;
      state.patterns.splice(patternIndex, 1);
      saveAndRender();
    });

    const dayRowsContainer = node.querySelector('.day-rows');
    const dayRowTemplate = document.getElementById('day-row-template');

    pattern.days.forEach((day, dayIndex) => {
      const dayNode = dayRowTemplate.content.cloneNode(true);
      const dayLabel = dayNode.querySelector('.day-label');
      dayLabel.textContent = DAY_LABELS[dayIndex];

      const startInput = dayNode.querySelector('.day-start');
      const endInput = dayNode.querySelector('.day-end');
      const breakInput = dayNode.querySelector('.day-break');
      const hoursCell = dayNode.querySelector('.day-hours');

      startInput.value = day.start;
      endInput.value = day.end;
      breakInput.value = day.breakMinutes;

      const renderDaily = () => {
        const result = metrics.dailyHours[dayIndex];
        if (result.valid) {
          hoursCell.textContent = `${result.hours.toFixed(2)} h`;
          hoursCell.classList.remove('invalid');
        } else {
          hoursCell.textContent = result.message || 'Invalid';
          hoursCell.classList.add('invalid');
        }
      };

      startInput.addEventListener('change', (event) => {
        pattern.days[dayIndex].start = event.target.value;
        saveAndRender();
      });

      endInput.addEventListener('change', (event) => {
        pattern.days[dayIndex].end = event.target.value;
        saveAndRender();
      });

      breakInput.addEventListener('change', (event) => {
        const value = Number(event.target.value);
        pattern.days[dayIndex].breakMinutes = Number.isNaN(value) ? '' : value;
        saveAndRender();
      });

      renderDaily();
      dayRowsContainer.appendChild(dayNode);
    });

    const summary = node.querySelector('.summary-values');
    summary.innerHTML = `
      <div class="helper-row"><strong>Week 1:</strong> ${metrics.week1.toFixed(2)} hrs</div>
      <div class="helper-row"><strong>Week 2:</strong> ${metrics.week2.toFixed(2)} hrs</div>
      <div class="helper-row"><strong>Fortnight:</strong> ${metrics.fortnight.toFixed(2)} hrs</div>
      <div class="helper-row"><strong>Gap:</strong> ${formatGap(metrics.gap)}</div>
    `;

    const statusText = node.querySelector('.status-text');
    const badges = node.querySelector('.badges');
    badges.innerHTML = '';

    if (metrics.hasInvalid) {
      statusText.textContent = 'Contains invalid days (excluded from totals).';
      const badge = document.createElement('span');
      badge.className = 'badge info';
      badge.textContent = 'Fix entries to include them in totals';
      badges.appendChild(badge);
    } else {
      statusText.textContent = 'All days valid and counted in totals.';
    }

    const gapBadge = document.createElement('span');
    gapBadge.classList.add('badge', classifyGap(metrics.gap));
    gapBadge.textContent = `Gap: ${formatGap(metrics.gap)}`;
    badges.appendChild(gapBadge);

    card.dataset.patternId = pattern.id;
    patternsContainer.appendChild(node);
  });
}

function renderComparison() {
  comparisonBody.innerHTML = '';
  const totals = state.patterns.map((pattern) => calculatePatternTotals(pattern, state.settings));
  const bestIndex = totals.reduce((best, current, idx) => {
    if (best === -1) return idx;
    const currentGap = Math.abs(current.gap);
    const bestGap = Math.abs(totals[best].gap);
    return currentGap < bestGap ? idx : best;
  }, totals.length ? 0 : -1);

  state.patterns.forEach((pattern, idx) => {
    const metrics = totals[idx];
    const row = document.createElement('tr');
    if (idx === bestIndex) {
      row.classList.add('best-match');
    }

    const cells = [
      pattern.name,
      metrics.week1.toFixed(2),
      metrics.week2.toFixed(2),
      metrics.fortnight.toFixed(2),
      formatGap(metrics.gap)
    ];

    cells.forEach((value, cellIndex) => {
      const td = document.createElement('td');
      td.textContent = value;
      if (cellIndex === 4) {
        td.classList.add(classifyGap(metrics.gap));
      }
      row.appendChild(td);
    });

    comparisonBody.appendChild(row);
  });
}

function classifyGap(gap) {
  if (gap === 0) return 'gap-zero';
  return gap > 0 ? 'gap-positive' : 'gap-negative';
}

function formatGap(gap) {
  if (gap === 0) return '0.00 hrs';
  return `${gap > 0 ? '+' : ''}${gap.toFixed(2)} hrs`;
}

function updateHeroStats() {
  if (heroStats.weekly) {
    heroStats.weekly.textContent = `${Number(state.settings.hoursPerWeek || 0).toFixed(2)} hrs`;
  }
  if (heroStats.target) {
    heroStats.target.textContent = `${Number(state.settings.targetFortnightHours || 0).toFixed(2)} hrs`;
  }
  if (heroStats.break) {
    heroStats.break.textContent = `${Number(state.settings.defaultBreak || 0)} min`;
  }
  if (heroStats.patterns) {
    heroStats.patterns.textContent = state.patterns.length.toString();
  }
}

function saveAndRender() {
  saveState();
  renderSettings();
  renderPatterns();
  renderComparison();
}

function bindSettingsListeners() {
  settingsInputs.hoursPerWeek.addEventListener('change', (event) => {
    const value = Number(event.target.value);
    state.settings.hoursPerWeek = Number.isNaN(value) ? 0 : value;
    if (state.settings.autoTarget) {
      updateTargetFromWeekly();
    }
    saveAndRender();
  });

  settingsInputs.targetFortnight.addEventListener('change', (event) => {
    const value = Number(event.target.value);
    state.settings.targetFortnightHours = Number.isNaN(value) ? 0 : value;
    state.settings.autoTarget = false;
    saveAndRender();
  });

  settingsInputs.defaultBreak.addEventListener('change', (event) => {
    const value = Number(event.target.value);
    state.settings.defaultBreak = Number.isNaN(value) ? 0 : value;
    saveAndRender();
  });

  settingsInputs.resetTarget.addEventListener('click', () => {
    updateTargetFromWeekly();
    saveAndRender();
  });
}

function bindGlobalActions() {
  addPatternButton.addEventListener('click', () => {
    const newIndex = state.patterns.length + 1;
    state.patterns.push(createDefaultPattern(`Pattern ${newIndex}`));
    saveAndRender();
  });
}

bindSettingsListeners();
bindGlobalActions();
saveAndRender();
