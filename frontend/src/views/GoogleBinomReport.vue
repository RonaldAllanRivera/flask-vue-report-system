<template>
  <div class="rounded-lg border border-slate-800 bg-slate-900 p-4 md:p-6">
    <h2 class="text-lg font-semibold mb-3">Google Binom Report</h2>
    <div class="flex flex-wrap items-end gap-3">
      <div>
        <label class="block text-xs text-slate-400 mb-1">Date From</label>
        <input class="px-3 py-2 rounded-md border border-slate-700 bg-slate-800 text-slate-100" v-model="dateFrom" type="date" />
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">Date To</label>
        <input class="px-3 py-2 rounded-md border border-slate-700 bg-slate-800 text-slate-100" v-model="dateTo" type="date" />
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">Report Type</label>
        <select v-model="reportType" class="px-3 py-2 rounded-md border border-slate-700 bg-slate-800 text-slate-100">
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">ROI Last Mode</label>
        <select v-model="roiLastMode" class="px-3 py-2 rounded-md border border-slate-700 bg-slate-800 text-slate-100">
          <option value="full">Full</option>
          <option value="cohort">Cohort</option>
        </select>
      </div>
      <button class="px-3 py-2 rounded-md bg-sky-600 hover:bg-sky-500 text-white disabled:opacity-50" @click="loadReport" :disabled="isLoading || !dateFrom || !dateTo">
        <span v-if="isLoading">Loading...</span>
        <span v-else>Load</span>
      </button>
      <button class="px-3 py-2 rounded-md bg-slate-700 hover:bg-slate-600 text-slate-100 disabled:opacity-50" @click="copyTSV" :disabled="!rows.length || isCopyingTable">
        <span v-if="isCopyingTable">Copying...</span>
        <span v-else>Copy Table (TSV)</span>
      </button>
      <button class="px-3 py-2 rounded-md bg-slate-700 hover:bg-slate-600 text-slate-100 disabled:opacity-50" @click="copySummary" :disabled="!summary || isCopyingSummary">
        <span v-if="isCopyingSummary">Copying...</span>
        <span v-else>Copy Summary</span>
      </button>
    </div>

    <table class="min-w-full text-sm mt-3" v-if="rows.length">
      <thead class="text-left text-slate-300">
        <tr>
          <th class="px-3 py-2 border-b border-slate-800">Campaign</th>
          <th class="px-3 py-2 border-b border-slate-800">Name</th>
          <th class="px-3 py-2 border-b border-slate-800">Spend</th>
          <th class="px-3 py-2 border-b border-slate-800">Revenue</th>
          <th class="px-3 py-2 border-b border-slate-800">P/L</th>
          <th class="px-3 py-2 border-b border-slate-800">ROI %</th>
          <th class="px-3 py-2 border-b border-slate-800">Leads</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, idx) in rows" :key="idx">
          <td class="px-3 py-2 border-b border-slate-800">{{ r.campaign ?? '-' }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.name ?? '-' }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.spend?.toFixed(2) }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.revenue?.toFixed(2) }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.pl?.toFixed(2) }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.roi ?? '-' }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ r.leads }}</td>
        </tr>
      </tbody>
    </table>

    <div class="rounded-lg border border-slate-800 bg-slate-900 p-3 mt-3" v-if="summary">
      <strong class="block mb-1">Summary</strong>
      <div>Spend: {{ summary.spend?.toFixed(2) }} | Revenue: {{ summary.revenue?.toFixed(2) }} | P/L: {{ summary.pl?.toFixed(2) }} | ROI: {{ summary.roi ?? '-' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiGet } from '@/lib/api'
import { useToastStore } from '@/stores/toast'

const dateFrom = ref('')
const dateTo = ref('')
const reportType = ref('weekly')
const roiLastMode = ref('full')
const rows = ref<any[]>([])
const summary = ref<any | null>(null)
const isLoading = ref(false)
const isCopyingTable = ref(false)
const isCopyingSummary = ref(false)
const toast = useToastStore()

async function loadReport() {
  isLoading.value = true
  try {
    const url = `/api/reports/google-binom?report_type=${reportType.value}&date_from=${dateFrom.value}&date_to=${dateTo.value}&roi_last_mode=${roiLastMode.value}`
    const data = await apiGet<any>(url)
    rows.value = data.rows ?? []
    summary.value = data.summary ?? null
    toast.info(`Loaded ${rows.value.length} row(s)`) 
  } catch (e: any) {
    toast.error(`Failed to load report: ${e?.message ?? e}`)
  } finally {
    isLoading.value = false
  }
}

function buildTSV(): string {
  const header = ['Campaign','Name','Spend','Revenue','P/L','ROI %','Leads']
  const lines = [header.join('\t')]
  for (const r of rows.value) {
    const line = [
      r.campaign ?? '-',
      r.name ?? '-',
      (r.spend ?? 0).toFixed?.(2) ?? String(r.spend ?? ''),
      (r.revenue ?? 0).toFixed?.(2) ?? String(r.revenue ?? ''),
      (r.pl ?? 0).toFixed?.(2) ?? String(r.pl ?? ''),
      r.roi ?? '-',
      r.leads ?? 0,
    ].join('\t')
    lines.push(line)
  }
  return lines.join('\n')
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (_) {
    try {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      const ok = document.execCommand('copy')
      document.body.removeChild(ta)
      return ok
    } catch {
      return false
    }
  }
}

async function copyTSV() {
  if (!rows.value.length) return
  isCopyingTable.value = true
  const ok = await copyText(buildTSV())
  isCopyingTable.value = false
  if (ok) toast.success('Table copied (TSV)')
  else toast.error('Copy failed')
}

async function copySummary() {
  if (!summary.value) return
  isCopyingSummary.value = true
  const s = summary.value
  const text = `Spend: ${Number(s.spend ?? 0).toFixed(2)} | Revenue: ${Number(s.revenue ?? 0).toFixed(2)} | P/L: ${Number(s.pl ?? 0).toFixed(2)} | ROI: ${s.roi ?? '-'}`
  const ok = await copyText(text)
  isCopyingSummary.value = false
  if (ok) toast.success('Summary copied')
  else toast.error('Copy failed')
}
</script>
