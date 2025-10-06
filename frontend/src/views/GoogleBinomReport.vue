<template>
  <div class="card">
    <h2>Google Binom Report</h2>
    <div class="row">
      <div>
        <label class="label">Date From</label>
        <input class="input" v-model="dateFrom" type="date" />
      </div>
      <div>
        <label class="label">Date To</label>
        <input class="input" v-model="dateTo" type="date" />
      </div>
      <div>
        <label class="label">Report Type</label>
        <select v-model="reportType" class="input">
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <div>
        <label class="label">ROI Last Mode</label>
        <select v-model="roiLastMode" class="input">
          <option value="full">Full</option>
          <option value="cohort">Cohort</option>
        </select>
      </div>
      <button class="button" @click="loadReport" :disabled="!dateFrom || !dateTo">Load</button>
    </div>

    <table class="table" v-if="rows.length">
      <thead>
        <tr>
          <th>Campaign</th>
          <th>Name</th>
          <th>Spend</th>
          <th>Revenue</th>
          <th>P/L</th>
          <th>ROI %</th>
          <th>Leads</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, idx) in rows" :key="idx">
          <td>{{ r.campaign ?? '-' }}</td>
          <td>{{ r.name ?? '-' }}</td>
          <td>{{ r.spend?.toFixed(2) }}</td>
          <td>{{ r.revenue?.toFixed(2) }}</td>
          <td>{{ r.pl?.toFixed(2) }}</td>
          <td>{{ r.roi ?? '-' }}</td>
          <td>{{ r.leads }}</td>
        </tr>
      </tbody>
    </table>

    <div class="card" v-if="summary">
      <strong>Summary</strong>
      <div>Spend: {{ summary.spend?.toFixed(2) }} | Revenue: {{ summary.revenue?.toFixed(2) }} | P/L: {{ summary.pl?.toFixed(2) }} | ROI: {{ summary.roi ?? '-' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiGet } from '@/lib/api'

const dateFrom = ref('')
const dateTo = ref('')
const reportType = ref('weekly')
const roiLastMode = ref('full')
const rows = ref<any[]>([])
const summary = ref<any | null>(null)

async function loadReport() {
  const url = `/api/reports/google-binom?report_type=${reportType.value}&date_from=${dateFrom.value}&date_to=${dateTo.value}&roi_last_mode=${roiLastMode.value}`
  const data = await apiGet<any>(url)
  rows.value = data.rows ?? []
  summary.value = data.summary ?? null
}
</script>
