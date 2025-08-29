(function () {
  const ingredientBody = document.getElementById('ingredient-body');
  const addBtn = document.getElementById('add-ingredient');
  const calcBtn = document.getElementById('calculate');
  const form = document.getElementById('recipe-form');
  const loafResults = document.getElementById('loaf-results');
  const sliceResults = document.getElementById('slice-results');
  const slicesInput = document.getElementById('slices');

  const DEFAULT_INGREDIENTS = [
    { name: 'Strong white bread flour', weight_g: 500, kcal_per_100g: 361, protein_per_100g: 12, fibre_per_100g: 2.4 },
    { name: 'Salt', weight_g: 12, kcal_per_100g: 0, protein_per_100g: 0, fibre_per_100g: 0 },
    { name: 'Sugar', weight_g: 9, kcal_per_100g: 375, protein_per_100g: 0, fibre_per_100g: 0 },
    { name: 'Dried yeast', weight_g: 14, kcal_per_100g: 325, protein_per_100g: 40.4, fibre_per_100g: 26.9 },
    { name: 'Vegetable oil', weight_g: 27, kcal_per_100g: 857, protein_per_100g: 0, fibre_per_100g: 0 },
    { name: 'Water', weight_g: 300, kcal_per_100g: 0, protein_per_100g: 0, fibre_per_100g: 0 },
    { name: 'Skimmed milk powder', weight_g: 13, kcal_per_100g: 348, protein_per_100g: 34.8, fibre_per_100g: 0 }
  ];

  function addIngredientRow(data = {}) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" class="name" value="${data.name || ''}"></td>
      <td><input type="number" class="weight" min="0" step="any" value="${data.weight_g || ''}"></td>
      <td><input type="number" class="kcal" min="0" step="any" value="${data.kcal_per_100g || ''}"></td>
      <td><input type="number" class="protein" min="0" step="any" value="${data.protein_per_100g || ''}"></td>
      <td><input type="number" class="fibre" min="0" step="any" value="${data.fibre_per_100g || ''}"></td>
      <td><button type="button" class="remove">Remove</button></td>
    `;
    tr.querySelector('.remove').addEventListener('click', () => {
      tr.remove();
      saveToLocalStorage(readStateFromDOM());
    });
    ingredientBody.appendChild(tr);
  }

  function readStateFromDOM() {
    const slices = parseInt(slicesInput.value, 10);
    const ingredients = [];
    ingredientBody.querySelectorAll('tr').forEach(row => {
      const name = row.querySelector('.name').value.trim();
      let weight = parseFloat(row.querySelector('.weight').value);
      let kcal = parseFloat(row.querySelector('.kcal').value);
      let protein = parseFloat(row.querySelector('.protein').value);
      let fibre = parseFloat(row.querySelector('.fibre').value);

      if (isNaN(weight) || weight < 0) {
        weight = 0; row.querySelector('.weight').classList.add('invalid');
      } else {
        row.querySelector('.weight').classList.remove('invalid');
      }
      if (isNaN(kcal) || kcal < 0) { kcal = 0; row.querySelector('.kcal').classList.add('invalid'); } else { row.querySelector('.kcal').classList.remove('invalid'); }
      if (isNaN(protein) || protein < 0) { protein = 0; row.querySelector('.protein').classList.add('invalid'); } else { row.querySelector('.protein').classList.remove('invalid'); }
      if (isNaN(fibre) || fibre < 0) { fibre = 0; row.querySelector('.fibre').classList.add('invalid'); } else { row.querySelector('.fibre').classList.remove('invalid'); }

      ingredients.push({ name, weight_g: weight, kcal_per_100g: kcal, protein_per_100g: protein, fibre_per_100g: fibre });
    });
    return { slices: isNaN(slices) ? null : slices, ingredients };
  }

  function calculateTotals(state) {
    const loaf = { kcal: 0, protein: 0, fibre: 0, weight: 0 };
    state.ingredients.forEach(ing => {
      const factor = ing.weight_g / 100;
      loaf.kcal += factor * ing.kcal_per_100g;
      loaf.protein += factor * ing.protein_per_100g;
      loaf.fibre += factor * ing.fibre_per_100g;
      loaf.weight += ing.weight_g;
    });
    let perSlice = null;
    if (state.slices && state.slices > 0) {
      perSlice = {
        kcal: loaf.kcal / state.slices,
        protein: loaf.protein / state.slices,
        fibre: loaf.fibre / state.slices
      };
    }
    return { loaf, perSlice };
  }

  function renderResults(totals) {
    const loaf = totals.loaf;
    loafResults.innerHTML = `
      <h2>Whole loaf</h2>
      <p>Calories: ${Math.round(loaf.kcal)} kcal</p>
      <p>Protein: ${Math.round(loaf.protein * 10) / 10} g</p>
      <p>Fibre: ${Math.round(loaf.fibre * 10) / 10} g</p>
      <p>Total weight: ${Math.round(loaf.weight * 10) / 10} g</p>
    `;
    if (totals.perSlice) {
      const slice = totals.perSlice;
      sliceResults.style.display = '';
      sliceResults.innerHTML = `
        <h2>Per slice</h2>
        <p>Calories: ${Math.round(slice.kcal)} kcal</p>
        <p>Protein: ${Math.round(slice.protein * 10) / 10} g</p>
        <p>Fibre: ${Math.round(slice.fibre * 10) / 10} g</p>
      `;
    } else {
      sliceResults.style.display = 'none';
      sliceResults.innerHTML = '';
    }
  }

  function saveToLocalStorage(state) {
    try {
      localStorage.setItem('nutri-calculator', JSON.stringify(state));
    } catch (e) {
      // ignore
    }
  }

  function loadFromLocalStorage() {
    try {
      const raw = localStorage.getItem('nutri-calculator');
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  addBtn.addEventListener('click', () => {
    addIngredientRow();
    saveToLocalStorage(readStateFromDOM());
  });

  calcBtn.addEventListener('click', () => {
    const state = readStateFromDOM();
    if (!state.slices || state.slices < 1) {
      slicesInput.classList.add('invalid');
    } else {
      slicesInput.classList.remove('invalid');
    }
    const totals = calculateTotals(state);
    renderResults(totals);
    saveToLocalStorage(state);
  });

  form.addEventListener('reset', () => {
    setTimeout(() => {
      ingredientBody.innerHTML = '';
      addIngredientRow();
      loafResults.innerHTML = '';
      sliceResults.innerHTML = '';
      localStorage.removeItem('nutri-calculator');
    }, 0);
  });

  // initialization
  const saved = loadFromLocalStorage();
  if (saved) {
    slicesInput.value = saved.slices || 12;
    saved.ingredients.forEach(ing => addIngredientRow(ing));
  } else {
    slicesInput.value = 12;
    DEFAULT_INGREDIENTS.forEach(ing => addIngredientRow(ing));
    saveToLocalStorage(readStateFromDOM());
  }
})();
