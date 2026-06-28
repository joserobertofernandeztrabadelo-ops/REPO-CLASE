const MONTHS = [
  'Enero','Febrero','Marzo','Abril','Mayo','Junio',
  'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'
];

const EXTRA_MONTHS = new Set([6, 12]);

let donutChart = null;
let budgetChart = null;

function app() {
  const now = new Date();
  return {
    view: 'resumen',
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    loading: false,
    importing: false,
    toast: null,
    _toastTimer: null,

    // Data
    summary: null,
    movements: [],
    accounts: [],
    budget: {},
    categories: [],
    categoryMeta: {},
    tennis: null,
    authStatus: null,
    importResult: null,
    selectedAccount: null,

    // Forms
    filters: { account: '', category: '' },
    newMovement: { date: '', description: '', concepto: '', amount: '', notes: '' },

    // Computed
    get monthName() { return MONTHS[this.month - 1]; },
    get isExtraMonth() { return EXTRA_MONTHS.has(this.month); },

    get categoryRows() {
      return Object.entries(this.categoryMeta).map(([name, meta]) => ({
        name,
        color: meta.color,
        income: this.summary?.by_category?.[name]?.income || 0,
        expenses: this.summary?.by_category?.[name]?.expenses || 0,
        count: this.summary?.by_category?.[name]?.count || 0,
      })).filter(r => r.income > 0 || r.expenses > 0);
    },

    async init() {
      await this.loadCategories();
      await this.loadAuthStatus();
      await this.refresh();
      await this.loadAccounts();
    },

    async navigate(v) {
      this.view = v;
      if (v === 'resumen') await this.refresh();
      if (v === 'movimientos') await this.loadMovements();
      if (v === 'cuentas') { await this.loadAccounts(); this.selectedAccount = null; }
      if (v === 'presupuesto') { await this.loadSummary(); await this.loadBudget(); }
      if (v === 'tenis') await this.loadTennis();
      if (v === 'importar') await this.loadAuthStatus();
    },

    async refresh() {
      await Promise.all([this.loadSummary(), this.loadBudget()]);
      this.$nextTick(() => this.renderCharts());
    },

    prevMonth() {
      if (this.month === 1) { this.month = 12; this.year--; }
      else this.month--;
      this.refresh();
      if (this.view === 'movimientos') this.loadMovements();
      if (this.view === 'tenis') this.loadTennis();
    },

    nextMonth() {
      if (this.month === 12) { this.month = 1; this.year++; }
      else this.month++;
      this.refresh();
      if (this.view === 'movimientos') this.loadMovements();
      if (this.view === 'tenis') this.loadTennis();
    },

    // ── API calls ──────────────────────────────────────────────────

    async loadCategories() {
      const r = await fetch('/api/categories');
      const data = await r.json();
      this.categories = data.categories;
      this.categoryMeta = data.meta;
    },

    async loadSummary() {
      const r = await fetch(`/api/movements/summary/${this.year}/${this.month}`);
      this.summary = await r.json();
    },

    async loadBudget() {
      const r = await fetch(`/api/budget/${this.year}/${this.month}`);
      this.budget = await r.json();
    },

    async loadMovements() {
      this.loading = true;
      try {
        const params = new URLSearchParams({ year: this.year, month: this.month });
        if (this.filters.account) params.set('account', this.filters.account);
        if (this.filters.category) params.set('category', this.filters.category);
        const r = await fetch(`/api/movements/?${params}`);
        this.movements = await r.json();
      } finally {
        this.loading = false;
      }
    },

    async loadAccounts() {
      const r = await fetch('/api/accounts/');
      this.accounts = await r.json();
    },

    async selectAccount(code) {
      const r = await fetch(`/api/accounts/${code}/movements?year=${this.year}&month=${this.month}`);
      this.selectedAccount = await r.json();
    },

    async loadTennis() {
      const r = await fetch(`/api/movements/tennis/${this.year}/${this.month}`);
      this.tennis = await r.json();
    },

    async loadAuthStatus() {
      const r = await fetch('/api/import/status');
      this.authStatus = await r.json();
    },

    async importSheets() {
      this.importing = true;
      this.importResult = null;
      try {
        const r = await fetch('/api/import/sheets', { method: 'POST' });
        this.importResult = await r.json();
        const total = (this.importResult.caixabank?.imported || 0) + (this.importResult.santander?.imported || 0);
        this.showToast(`Importados ${total} movimientos nuevos`, 'success');
        await this.loadAccounts();
        await this.refresh();
      } catch (e) {
        this.showToast('Error al importar: ' + e.message, 'error');
      } finally {
        this.importing = false;
      }
    },

    async addManualMovement() {
      if (!this.newMovement.date || !this.newMovement.description || !this.newMovement.amount) return;
      const body = {
        account_code: 'revolut',
        date: this.newMovement.date,
        description: this.newMovement.description,
        concepto: this.newMovement.concepto || null,
        amount: parseFloat(this.newMovement.amount),
        notes: this.newMovement.notes || null,
      };
      const r = await fetch('/api/movements/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        this.newMovement = { date: '', description: '', concepto: '', amount: '', notes: '' };
        this.showToast('Movimiento añadido', 'success');
        await this.loadAccounts();
        await this.refresh();
      } else {
        this.showToast('Error al guardar', 'error');
      }
    },

    async updateCategory(id, category) {
      await fetch(`/api/movements/${id}/category?category=${encodeURIComponent(category)}`, { method: 'PATCH' });
      await this.refresh();
    },

    async deleteMovement(id) {
      if (!confirm('¿Eliminar este movimiento?')) return;
      await fetch(`/api/movements/${id}`, { method: 'DELETE' });
      this.movements = this.movements.filter(m => m.id !== id);
      await this.refresh();
      this.showToast('Movimiento eliminado', 'success');
    },

    async saveBudget(category, value) {
      const amount = parseFloat(value);
      if (isNaN(amount) || amount < 0) return;
      if (amount === 0) {
        await fetch(`/api/budget/${this.year}/${this.month}/${encodeURIComponent(category)}`, { method: 'DELETE' });
        delete this.budget[category];
      } else {
        await fetch('/api/budget/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ year: this.year, month: this.month, category, amount }),
        });
        this.budget[category] = amount;
      }
      this.$nextTick(() => this.renderCharts());
    },

    exportCsv() {
      window.location.href = `/api/export/csv?year=${this.year}&month=${this.month}`;
    },

    // ── Helpers ──────────────────────────────────────────────────

    fmt(v) {
      if (v == null) return '—';
      return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 }).format(v);
    },

    formatDate(iso) {
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    },

    categoryColor(cat) {
      return this.categoryMeta[cat]?.color || '#6b7280';
    },

    showToast(msg, type = 'success') {
      clearTimeout(this._toastTimer);
      this.toast = { msg, type };
      this._toastTimer = setTimeout(() => { this.toast = null; }, 3500);
    },

    // ── Charts ────────────────────────────────────────────────────

    renderCharts() {
      this.renderDonut();
      this.renderBudgetBar();
    },

    renderDonut() {
      const ctx = document.getElementById('donutChart');
      if (!ctx || !this.summary) return;

      const expenseCategories = Object.entries(this.summary.by_category || {})
        .filter(([, v]) => v.expenses > 0)
        .sort((a, b) => b[1].expenses - a[1].expenses);

      const labels = expenseCategories.map(([k]) => k);
      const data = expenseCategories.map(([, v]) => v.expenses);
      const colors = labels.map(l => this.categoryMeta[l]?.color || '#6b7280');

      if (donutChart) donutChart.destroy();
      donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: '#fff' }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { font: { size: 11 }, boxWidth: 12, padding: 8 } },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.label}: ${this.fmt(ctx.raw)}`,
              },
            },
          },
        },
      });
    },

    renderBudgetBar() {
      const ctx = document.getElementById('budgetChart');
      if (!ctx || !this.summary) return;

      const cats = Object.keys(this.budget).filter(c => c !== 'Ingresos');
      if (cats.length === 0) {
        if (budgetChart) budgetChart.destroy();
        return;
      }

      const real = cats.map(c => this.summary.by_category?.[c]?.expenses || 0);
      const bud = cats.map(c => this.budget[c] || 0);
      const colors = cats.map((c, i) => {
        const r = real[i], b = bud[i];
        return b > 0 && r > b ? '#ef4444' : '#10b981';
      });

      if (budgetChart) budgetChart.destroy();
      budgetChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: cats.map(c => c.length > 12 ? c.slice(0, 12) + '…' : c),
          datasets: [
            { label: 'Real', data: real, backgroundColor: colors, borderRadius: 4 },
            { label: 'Presupuesto', data: bud, backgroundColor: '#e5e7eb', borderRadius: 4 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { font: { size: 11 } } } },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 10 } } },
            y: {
              grid: { color: '#f3f4f6' },
              ticks: { font: { size: 10 }, callback: v => `${v}€` },
            },
          },
        },
      });
    },
  };
}
