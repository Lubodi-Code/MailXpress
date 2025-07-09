<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const subject = ref('')
const body = ref('')
const emailColumn = ref('')
const excelFile = ref(null)
const message = ref('')

function validate() {
  if (!email.value || !password.value) {
    message.value = 'Ingresa correo y contraseña.'
    return false
  }
  message.value = 'Credenciales validadas (simulado).'
  return true
}

function handleFile(event) {
  const file = event.target.files[0]
  excelFile.value = file || null
}

function sendEmails() {
  if (!validate()) return
  if (!excelFile.value) {
    message.value = 'Selecciona un archivo Excel.'
    return
  }
  if (!subject.value || !body.value || !emailColumn.value) {
    message.value = 'Completa todos los campos del correo.'
    return
  }
  message.value = `Envío masivo iniciado para columna ${emailColumn.value} (simulado).`
}
</script>

<template>
  <div class="p-4 space-y-6 max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold">Inicio</h1>

    <section class="space-y-2">
      <h2 class="text-lg font-semibold">Cuenta de envío</h2>
      <input
        v-model="email"
        type="email"
        placeholder="Correo"
        class="w-full border rounded p-2"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Contraseña"
        class="w-full border rounded p-2"
      />
      <button
        @click="validate"
        class="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Validar
      </button>
    </section>

    <section class="space-y-2">
      <h2 class="text-lg font-semibold">Archivo Excel</h2>
      <input
        type="file"
        accept=".xls,.xlsx"
        @change="handleFile"
        class="w-full"
      />
    </section>

    <section class="space-y-2">
      <h2 class="text-lg font-semibold">Contenido del correo</h2>
      <input
        v-model="subject"
        type="text"
        placeholder="Asunto"
        class="w-full border rounded p-2"
      />
      <textarea
        v-model="body"
        placeholder="Cuerpo del correo"
        class="w-full border rounded p-2 h-32"
      ></textarea>
      <input
        v-model="emailColumn"
        type="text"
        placeholder="Columna con correos (por ejemplo A)"
        class="w-full border rounded p-2"
      />
      <button
        @click="sendEmails"
        class="bg-green-600 text-white px-4 py-2 rounded"
      >
        Enviar correos
      </button>
    </section>

    <p class="text-red-600">{{ message }}</p>
  </div>
</template>

<style scoped>
</style>
