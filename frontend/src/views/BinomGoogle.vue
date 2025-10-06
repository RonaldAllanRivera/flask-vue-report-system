<template>
  <div class="card">
    <h2>Binom Google Spent</h2>
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
        <label class="label">CSV File (semicolon + quoted)</label>
        <input class="input" type="file" @change="onFile" />
      </div>
      <button class="button" @click="upload" :disabled="!file || !dateFrom || !dateTo">Upload</button>
      <button class="button secondary" @click="loadBatches">Refresh Batches</button>
    </div>

    <table class="table" v-if="batches.length">
      <thead>
        <tr>
          <th>Date From</th>
          <th>Date To</th>
          <th>Report Type</th>
          <th>Count</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in batches" :key="b.date_from + b.report_type">
          <td>{{ b.date_from }}</td>
          <td>{{ b.date_to }}</td>
          <td><span class="badge">{{ b.report_type }}</span></td>
          <td>{{ b.count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiGet, apiPostForm } from '@/lib/api'

const dateFrom = ref('')
const dateTo = ref('')
const reportType = ref('weekly')
const file = ref<File | null>(null)
const batches = ref<any[]>([])

function onFile(e: Event) {
  const t = e.target as HTMLInputElement
  file.value = t.files?.[0] ?? null
}

async function upload() {
  if (!file.value) return
  const form = new FormData()
  form.append('file', file.value)
  form.append('date_from', dateFrom.value)
  form.append('date_to', dateTo.value)
  form.append('report_type', reportType.value)
  await apiPostForm(`/api/uploads/binom-google`, form)
  await loadBatches()
}

async function loadBatches() {
  batches.value = await apiGet<any[]>(`/api/binom-google/batches`).then(r => (r as any).batches ?? [])
}

loadBatches()
</script>
