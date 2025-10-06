<template>
  <div class="app">
    <header class="header">
      <h1>Reports Admin</h1>
      <nav class="nav">
        <div class="menu" tabindex="0">
          <a href="#" class="menu-title" @click.prevent>
            Google and Binom Reports Only ▾
          </a>
          <div class="dropdown">
            <RouterLink to="/google">Google Data</RouterLink>
            <RouterLink to="/binom-google">Binom Google Spent Data</RouterLink>
            <RouterLink to="/google-binom-report">Google Binom Report</RouterLink>
          </div>
        </div>
      </nav>
    </header>
    <main class="container">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts"></script>

<style>
:root {
  color-scheme: dark;
  --bg: #0f172a;
  --fg: #e2e8f0;
  --muted: #94a3b8;
  --primary: #22d3ee;
  --card: #111827;
}
html, body, #app { height: 100%; margin: 0; }
body { background: var(--bg); color: var(--fg); font-family: Inter, system-ui, Arial, sans-serif; }
.header { display:flex; align-items:center; justify-content:space-between; padding: 12px 16px; border-bottom: 1px solid #1f2937; }
.header h1 { font-size: 18px; margin: 0; }
.nav { display:flex; gap: 12px; position: relative; }
.nav a { color: var(--muted); text-decoration: none; }
.nav a.router-link-active { color: var(--primary); }
.menu { position: relative; }
.menu-title { display:inline-block; padding: 8px 10px; border: 1px solid #1f2937; border-radius: 6px; background: #0b1220; color: var(--fg); }
.menu:hover .menu-title, .menu:focus-within .menu-title { border-color: #374151; }
.dropdown { display:none; position: absolute; top: 120%; left: 0; min-width: 260px; background: var(--card); border: 1px solid #1f2937; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,.35); padding: 6px 0; z-index: 50; }
.menu:hover .dropdown, .menu:focus-within .dropdown { display:block; }
.dropdown a { display:block; padding: 8px 12px; color: var(--fg); }
.dropdown a:hover, .dropdown a.router-link-active { background: #1f2937; color: var(--primary); }
.container { padding: 16px; }
.card { background: var(--card); border: 1px solid #1f2937; border-radius: 8px; padding: 16px; }
.label { display:block; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
.input, select { padding: 8px; border-radius: 6px; border: 1px solid #334155; background: #0b1220; color: var(--fg); }
.button { padding: 8px 12px; background: #0ea5e9; color: white; border: none; border-radius: 6px; cursor: pointer; }
.button.secondary { background: #334155; }
.table { width: 100%; border-collapse: collapse; margin-top: 12px; }
.table th, .table td { padding: 8px; border-bottom: 1px solid #273041; text-align: right; }
.table th:first-child, .table td:first-child { text-align: left; }
.badge { padding: 2px 6px; border: 1px solid #374151; border-radius: 999px; font-size: 12px; color: var(--muted); }
.row { display:flex; gap:12px; align-items:end; flex-wrap: wrap; }
</style>
