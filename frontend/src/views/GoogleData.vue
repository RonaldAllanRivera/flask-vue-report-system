<template>
  <div class="rounded-lg border border-slate-800 bg-slate-900 p-4 md:p-6">
    <h2 class="text-lg font-semibold mb-3">Google Data</h2>
    <div class="flex flex-wrap items-end gap-3">
      <div>
        <label class="block text-xs text-slate-400 mb-1">Date From</label>
        <input class="px-3 h-10 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100" v-model="dateFrom" type="date" :disabled="preset!=='custom'" />
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">Date To</label>
        <input class="px-3 h-10 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100" v-model="dateTo" type="date" :disabled="preset!=='custom'" />
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">Report Type</label>
        <select v-model="reportType" class="px-3 h-10 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100">
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">Date Preset</label>
        <select v-model="preset" class="px-3 h-10 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100">
          <option value="yesterday">Yesterday</option>
          <option value="last7">Last 7 Days (ends yesterday)</option>
          <option value="last14">Last 14 Days (ends yesterday)</option>
          <option value="last30">Last 30 Days (ends yesterday)</option>
          <option value="this_month">This Month to Date</option>
          <option value="last_month">Last Month</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      <div>
        <label class="block text-xs text-slate-400 mb-1">CSV File</label>
        <input class="px-3 h-10 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100 file:mr-3 file:px-3 file:py-2 file:text-sm file:rounded-md file:border-0 file:bg-slate-700 file:text-slate-100" type="file" accept=".csv,text/csv" @change="onFile" />
      </div>
      <div class="mt-6">
        <a href="/samples/google_sample.csv" download
           class="inline-flex items-center h-10 px-3 text-sm rounded-md border border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700">
          Download Sample
        </a>
      </div>
      <button class="px-3 h-10 text-sm rounded-md bg-sky-600 hover:bg-sky-500 text-white disabled:opacity-50" @click="upload" :disabled="isUploading || !file || !hasValidRange">
        <span v-if="isUploading">Uploading...</span>
        <span v-else>Upload</span>
      </button>
      <button class="px-3 h-10 text-sm rounded-md bg-slate-700 hover:bg-slate-600 text-slate-100 disabled:opacity-50" @click="loadBatches" :disabled="isRefreshing">
        <span v-if="isRefreshing">Refreshing...</span>
        <span v-else>Refresh Batches</span>
      </button>
    </div>

    <table class="min-w-full text-sm mt-3" v-if="batches.length">
      <thead class="text-left text-slate-300">
        <tr>
          <th class="px-3 py-2 border-b border-slate-800">Date From</th>
          <th class="px-3 py-2 border-b border-slate-800">Date To</th>
          <th class="px-3 py-2 border-b border-slate-800">Report Type</th>
          <th class="px-3 py-2 border-b border-slate-800">Count</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in batches" :key="b.date_from + b.report_type">
          <td class="px-3 py-2 border-b border-slate-800">{{ b.date_from }}</td>
          <td class="px-3 py-2 border-b border-slate-800">{{ b.date_to }}</td>
          <td class="px-3 py-2 border-b border-slate-800"><span class="inline-block px-2 py-0.5 text-xs rounded-full border border-slate-600 text-slate-300">{{ b.report_type }}</span></td>
          <td class="px-3 py-2 border-b border-slate-800">{{ b.count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { apiGet, apiPostForm } from '@/lib/api'
import { useToastStore } from '@/stores/toast'

const dateFrom = ref('')
const dateTo = ref('')
const reportType = ref('weekly')
const file = ref<File | null>(null)
const batches = ref<any[]>([])
const isUploading = ref(false)
const isRefreshing = ref(false)
const toast = useToastStore()
const preset = ref<'yesterday'|'last7'|'last14'|'last30'|'this_month'|'last_month'|'custom'>('last7')
const hasValidRange = ref(false)

async function onFile(e: Event) {
  const t = e.target as HTMLInputElement
  const f = t.files?.[0] ?? null
  if (!f) { file.value = null; return }
  const ok = await validateSelectedFile(f)
  file.value = ok ? f : null
  if (!ok) t.value = ''
}

function isJSONText(s: string): boolean {
  const i = s.search(/\S/)
  if (i === -1) return false
  const ch = s[i]
  return ch === '{' || ch === '['
}

function normalize(s: string): string { return s.trim().toLowerCase() }

async function validateSelectedFile(f: File): Promise<boolean> {
  // Only CSV is supported for Google uploads
  if (f.name.toLowerCase().endsWith('.json')) {
    toast.error('JSON file detected. Please upload a CSV for Google Data.')
    return false
  }
  // Read a small chunk to detect header
  const chunk = await f.slice(0, 4096).text()
  if (isJSONText(chunk)) {
    toast.error('JSON content detected. Please upload a CSV for Google Data.')
    return false
  }
  const lines = chunk.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
  // Skip possible title/date lines
  const isDateRange = (l: string) => /\d{1,2} \w+ \d{4} - \d{1,2} \w+ \d{4}/i.test(l)
  const dataLines = lines.filter(l => !/^new\s+weekly\s+reports/i.test(l) && !isDateRange(l))
  const header = dataLines.find(l => l.includes(',') || l.includes(';')) || ''
  const hl = normalize(header)
  // If it looks like Binom CSV, warn and block
  if (header.includes(';') && (hl.includes('name') && hl.includes('revenue'))) {
    toast.error('This looks like a Binom Google CSV. Please use the Binom Google Spent page.')
    return false
  }
  // Expect Google CSV headers to include campaign and cost (comma-separated)
  if (!header.includes(',')) {
    toast.error('CSV appears malformed or not comma-separated. Expected Google CSV with commas.')
    return false
  }
  if (!(hl.includes('campaign') && hl.includes('cost'))) {
    toast.error('CSV header must include Campaign and Cost columns for Google Data.')
    return false
  }
  return true
}

async function upload() {
  if (!file.value) return
  isUploading.value = true
  try {
    const form = new FormData()
    form.append('file', file.value)
    form.append('date_from', dateFrom.value)
    form.append('date_to', dateTo.value)
    form.append('report_type', reportType.value)
    const res: any = await apiPostForm(`/api/uploads/google`, form)
    if (res?.status === 'ok' && (res?.inserted ?? 0) > 0) {
      toast.success(`Uploaded: ${res.inserted} row(s)`) 
    } else {
      toast.error(`Upload accepted but no rows inserted`) 
    }
    await loadBatches()
  } catch (e: any) {
    toast.error(`Upload failed: ${e?.message ?? e}`)
  } finally {
    isUploading.value = false
  }
}

async function loadBatches() {
  isRefreshing.value = true
  try {
    batches.value = await apiGet<any[]>(`/api/google/batches`).then(r => (r as any).batches ?? [])
    if (batches.value.length) toast.info(`Loaded ${batches.value.length} batch group(s)`) 
  } catch (e: any) {
    toast.error(`Failed to load batches: ${e?.message ?? e}`)
  } finally {
    isRefreshing.value = false
  }
}

loadBatches()

function fmt(d: Date): string {
  return d.toISOString().slice(0, 10)
}
function startOfMonth(d: Date): Date { return new Date(d.getFullYear(), d.getMonth(), 1) }
function endOfMonth(d: Date): Date { return new Date(d.getFullYear(), d.getMonth()+1, 0) }

function applyPreset() {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  let from = ''
  let to = ''
  switch (preset.value) {
    case 'yesterday':
      from = fmt(yesterday); to = fmt(yesterday); break
    case 'last7': {
      const f = new Date(yesterday); f.setDate(yesterday.getDate() - 6); from = fmt(f); to = fmt(yesterday); break }
    case 'last14': {
      const f = new Date(yesterday); f.setDate(yesterday.getDate() - 13); from = fmt(f); to = fmt(yesterday); break }
    case 'last30': {
      const f = new Date(yesterday); f.setDate(yesterday.getDate() - 29); from = fmt(f); to = fmt(yesterday); break }
    case 'this_month':
      from = fmt(startOfMonth(today)); to = fmt(today); break
    case 'last_month': {
      const lm = new Date(today.getFullYear(), today.getMonth()-1, 1)
      from = fmt(startOfMonth(lm)); to = fmt(endOfMonth(lm)); break }
    case 'custom':
      // leave as-is
      break
  }
  if (preset.value !== 'custom') {
    dateFrom.value = from
    dateTo.value = to
  }
  hasValidRange.value = !!dateFrom.value && !!dateTo.value
}

watch(preset, applyPreset, { immediate: true })
watch([dateFrom, dateTo], () => { hasValidRange.value = !!dateFrom.value && !!dateTo.value })
</script>
