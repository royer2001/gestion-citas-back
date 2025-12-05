# Guía de Actualización del Frontend - Gestión de Horarios Médicos

## Resumen de Cambios en el Backend

El sistema de horarios médicos ha sido actualizado para soportar **dos turnos por día** (mañana y tarde) con cupos independientes para cada turno.

### Cambios Principales:
1. **Horarios fijos por turno:**
   - **Mañana:** 07:30 - 13:30
   - **Tarde:** 13:30 - 19:30

2. **Cupos independientes:** Cada turno puede tener diferente cantidad de cupos (ej: 5 mañana, 7 tarde)

3. **Gestión mensual:** Los horarios se gestionan por mes completo

---

## Nuevos Endpoints de la API

### 1. Crear Horarios Mensuales
```
POST /api/horarios/mensual
```

**Request Body:**
```json
{
    "medico_id": 1,
    "area_id": 1,
    "mes": "2025-01",
    "dias_seleccionados": [0, 1, 2, 3, 4],
    "turnos": {
        "manana": {
            "activo": true,
            "cupos": 5
        },
        "tarde": {
            "activo": true,
            "cupos": 7
        }
    }
}
```

**Notas:**
- `dias_seleccionados`: Array de días de la semana (0=Lunes, 1=Martes, ..., 6=Domingo)
- Al menos un turno debe estar activo
- Si un horario ya existe para esa fecha/turno, se actualiza

**Response (201):**
```json
{
    "message": "Horarios procesados correctamente",
    "creados": 20,
    "actualizados": 0,
    "horarios": [...]
}
```

### 2. Obtener Horarios
```
GET /api/horarios/
```

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `medico_id` | int | Filtrar por médico |
| `area_id` | int | Filtrar por área |
| `mes` | string | Filtrar por mes (YYYY-MM) |
| `fecha` | string | Filtrar por fecha (YYYY-MM-DD) |
| `turno` | string | Filtrar por turno ('M' o 'T') |

**Response:**
```json
[
    {
        "id": 1,
        "medico_id": 1,
        "area_id": 1,
        "fecha": "2025-01-06",
        "dia_semana": 0,
        "turno": "M",
        "turno_nombre": "Mañana",
        "hora_inicio": "07:30:00",
        "hora_fin": "13:30:00",
        "cupos": 5,
        "medico_nombre": "Dr. Juan Pérez",
        "area_nombre": "Medicina General"
    }
]
```

### 3. Obtener Resumen por Mes (para Calendario)
```
GET /api/horarios/resumen?medico_id=1&mes=2025-01
```

**Response:**
```json
{
    "medico_id": 1,
    "mes": "2025-01",
    "dias": [
        {
            "fecha": "2025-01-06",
            "dia_semana": 0,
            "turnos": {
                "M": {
                    "id": 1,
                    "turno": "M",
                    "turno_nombre": "Mañana",
                    "hora_inicio": "07:30:00",
                    "hora_fin": "13:30:00",
                    "cupos": 5,
                    "area_id": 1,
                    "area_nombre": "Medicina General"
                },
                "T": {
                    "id": 2,
                    "turno": "T",
                    "turno_nombre": "Tarde",
                    "hora_inicio": "13:30:00",
                    "hora_fin": "19:30:00",
                    "cupos": 7,
                    "area_id": 1,
                    "area_nombre": "Medicina General"
                }
            }
        }
    ]
}
```

### 4. Eliminar Horarios del Mes
```
DELETE /api/horarios/mensual?medico_id=1&mes=2025-01&turno=M
```

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `medico_id` | int | (Requerido) ID del médico |
| `mes` | string | (Requerido) Mes (YYYY-MM) |
| `turno` | string | (Opcional) 'M' o 'T' para eliminar solo un turno |

---

## Cambios Requeridos en el Frontend

### 1. Actualizar `horarioService.ts`

```typescript
import api from './api'

export interface Turno {
    id?: number
    turno: 'M' | 'T'
    turno_nombre: string
    hora_inicio: string
    hora_fin: string
    cupos: number
    area_id?: number
    area_nombre?: string
}

export interface HorarioDia {
    fecha: string
    dia_semana: number
    turnos: {
        M?: Turno
        T?: Turno
    }
}

export interface Horario {
    id?: number
    medico_id?: number
    area_id?: number
    fecha?: string
    dia_semana: number
    turno: 'M' | 'T'
    turno_nombre?: string
    hora_inicio: string
    hora_fin: string
    cupos: number
    medico_nombre?: string
    area_nombre?: string
}

export interface TurnoConfig {
    activo: boolean
    cupos: number
}

export interface CrearHorariosMensualesPayload {
    medico_id: number
    area_id: number
    mes: string  // YYYY-MM
    dias_seleccionados: number[]  // 0-6
    turnos: {
        manana: TurnoConfig
        tarde: TurnoConfig
    }
}

export interface ResumenMes {
    medico_id: number
    mes: string
    dias: HorarioDia[]
}

const horarioService = {
    // Crear horarios para todo el mes
    crearHorariosMensuales(payload: CrearHorariosMensualesPayload) {
        return api.post('/horarios/mensual', payload)
    },

    // Obtener horarios con filtros
    getHorarios(params?: {
        medico_id?: number | null
        area_id?: number | null
        mes?: string
        fecha?: string
        turno?: 'M' | 'T'
    }) {
        return api.get<Horario[]>('/horarios/', { params })
    },

    // Obtener resumen del mes para calendario
    getResumenMes(medico_id: number, mes: string) {
        return api.get<ResumenMes>('/horarios/resumen', {
            params: { medico_id, mes }
        })
    },

    // Eliminar un horario específico
    eliminarHorario(id: number) {
        return api.delete(`/horarios/${id}`)
    },

    // Eliminar horarios de un mes
    eliminarHorariosMes(medico_id: number, mes: string, turno?: 'M' | 'T') {
        return api.delete('/horarios/mensual', {
            params: { medico_id, mes, turno }
        })
    },

    // Crear horario individual (legacy compatible)
    crearHorario(data: any) {
        return api.post('/horarios/', data)
    }
}

export default horarioService
```

### 2. Actualizar el Formulario del Modal en `AdminHorarios.vue`

Reemplazar la sección de "Horarios y Cupos" en el modal por los dos turnos:

```vue
<template>
    <!-- ... resto del template ... -->

    <!-- Modal Configurar Horario Mensual -->
    <div v-if="modalVisible" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full shadow-2xl">
            <!-- Header del modal -->
            <div class="bg-gradient-to-r from-teal-600 to-teal-700 px-6 py-4 text-white">
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-xl font-bold">Configurar Horario Mensual</h3>
                        <p class="text-teal-100 text-sm mt-1">Programa los turnos del médico para el mes</p>
                    </div>
                    <button @click="cerrarModal" class="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center">
                        <i class="pi pi-times"></i>
                    </button>
                </div>
            </div>

            <!-- Contenido del modal -->
            <div class="p-6 overflow-y-auto max-h-[70vh]">
                <form @submit.prevent="guardarHorarioMensual" class="space-y-5">
                    
                    <!-- Médico y Área -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="pi pi-user mr-1 text-teal-600"></i>
                                Médico <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.medico_id" required class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500">
                                <option :value="null">Seleccione un médico</option>
                                <option v-for="medico in medicos" :key="medico.id" :value="medico.id">
                                    {{ medico.name }}
                                </option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                <i class="pi pi-building mr-1 text-teal-600"></i>
                                Área <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.area_id" required class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500">
                                <option :value="null">Seleccione un área</option>
                                <option v-for="area in areas" :key="area.id" :value="area.id">
                                    {{ area.nombre }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <!-- Mes -->
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">
                            <i class="pi pi-calendar mr-1 text-teal-600"></i>
                            Mes <span class="text-red-500">*</span>
                        </label>
                        <input type="month" v-model="form.mes" required 
                            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500" />
                    </div>

                    <!-- Días de la semana -->
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-3">
                            <i class="pi pi-calendar-plus mr-1 text-teal-600"></i>
                            Días de Atención <span class="text-red-500">*</span>
                        </label>
                        <div class="grid grid-cols-4 md:grid-cols-7 gap-2">
                            <label v-for="(dia, index) in diasSemana" :key="index" 
                                :class="[
                                    'flex flex-col items-center p-3 border-2 rounded-xl cursor-pointer transition-all',
                                    form.dias_seleccionados.includes(index)
                                        ? 'bg-teal-50 border-teal-500 text-teal-700'
                                        : 'border-gray-200 hover:border-gray-300 text-gray-600'
                                ]">
                                <input type="checkbox" :value="index" v-model="form.dias_seleccionados" class="sr-only" />
                                <span class="font-bold text-lg">{{ dia }}</span>
                                <i v-if="form.dias_seleccionados.includes(index)" class="pi pi-check-circle text-teal-600 mt-1"></i>
                                <i v-else class="pi pi-circle text-gray-300 mt-1"></i>
                            </label>
                        </div>
                        <div class="flex gap-2 mt-3">
                            <button type="button" @click="seleccionarDiasLaborables" class="text-xs text-teal-600 hover:text-teal-700 font-medium">
                                Lun-Vie
                            </button>
                            <span class="text-gray-300">|</span>
                            <button type="button" @click="seleccionarTodosDias" class="text-xs text-teal-600 hover:text-teal-700 font-medium">
                                Todos
                            </button>
                            <span class="text-gray-300">|</span>
                            <button type="button" @click="form.dias_seleccionados = []" class="text-xs text-gray-500 hover:text-gray-700 font-medium">
                                Ninguno
                            </button>
                        </div>
                    </div>

                    <!-- NUEVA SECCIÓN: Configuración de Turnos -->
                    <div class="space-y-4">
                        <label class="block text-sm font-semibold text-gray-700">
                            <i class="pi pi-clock mr-1 text-teal-600"></i>
                            Configuración de Turnos
                        </label>

                        <!-- Turno Mañana -->
                        <div :class="[
                            'border-2 rounded-xl p-4 transition-all',
                            form.turnos.manana.activo 
                                ? 'border-amber-400 bg-amber-50' 
                                : 'border-gray-200 bg-gray-50'
                        ]">
                            <div class="flex items-center justify-between mb-3">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                                        <i class="pi pi-sun text-amber-600 text-lg"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-gray-800">Turno Mañana</h4>
                                        <p class="text-sm text-gray-500">07:30 - 13:30</p>
                                    </div>
                                </div>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" v-model="form.turnos.manana.activo" class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-amber-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                                </label>
                            </div>
                            
                            <div v-if="form.turnos.manana.activo" class="flex items-center gap-3">
                                <label class="text-sm text-gray-600">Cupos:</label>
                                <input type="number" v-model.number="form.turnos.manana.cupos" min="1" max="50"
                                    class="w-20 px-3 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 text-center font-semibold" />
                                <span class="text-sm text-gray-500">citas disponibles</span>
                            </div>
                        </div>

                        <!-- Turno Tarde -->
                        <div :class="[
                            'border-2 rounded-xl p-4 transition-all',
                            form.turnos.tarde.activo 
                                ? 'border-indigo-400 bg-indigo-50' 
                                : 'border-gray-200 bg-gray-50'
                        ]">
                            <div class="flex items-center justify-between mb-3">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                                        <i class="pi pi-moon text-indigo-600 text-lg"></i>
                                    </div>
                                    <div>
                                        <h4 class="font-semibold text-gray-800">Turno Tarde</h4>
                                        <p class="text-sm text-gray-500">13:30 - 19:30</p>
                                    </div>
                                </div>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" v-model="form.turnos.tarde.activo" class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-500"></div>
                                </label>
                            </div>
                            
                            <div v-if="form.turnos.tarde.activo" class="flex items-center gap-3">
                                <label class="text-sm text-gray-600">Cupos:</label>
                                <input type="number" v-model.number="form.turnos.tarde.cupos" min="1" max="50"
                                    class="w-20 px-3 py-2 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-center font-semibold" />
                                <span class="text-sm text-gray-500">citas disponibles</span>
                            </div>
                        </div>
                    </div>

                    <!-- Resumen visual -->
                    <div v-if="form.dias_seleccionados.length > 0 && form.mes && (form.turnos.manana.activo || form.turnos.tarde.activo)"
                        class="bg-gradient-to-r from-blue-50 to-teal-50 border border-blue-200 rounded-xl p-4">
                        <h4 class="font-bold text-blue-900 mb-3 flex items-center gap-2">
                            <i class="pi pi-info-circle"></i>
                            Resumen de Configuración
                        </h4>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <i class="pi pi-calendar text-blue-600"></i>
                                </div>
                                <div>
                                    <p class="text-gray-500 text-xs">Días</p>
                                    <p class="font-bold text-blue-800">{{ contarDiasLaborables() }}</p>
                                </div>
                            </div>
                            <div v-if="form.turnos.manana.activo" class="flex items-center gap-2">
                                <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
                                    <i class="pi pi-sun text-amber-600"></i>
                                </div>
                                <div>
                                    <p class="text-gray-500 text-xs">Mañana</p>
                                    <p class="font-bold text-amber-800">{{ contarDiasLaborables() * form.turnos.manana.cupos }} cupos</p>
                                </div>
                            </div>
                            <div v-if="form.turnos.tarde.activo" class="flex items-center gap-2">
                                <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                                    <i class="pi pi-moon text-indigo-600"></i>
                                </div>
                                <div>
                                    <p class="text-gray-500 text-xs">Tarde</p>
                                    <p class="font-bold text-indigo-800">{{ contarDiasLaborables() * form.turnos.tarde.cupos }} cupos</p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center">
                                    <i class="pi pi-ticket text-teal-600"></i>
                                </div>
                                <div>
                                    <p class="text-gray-500 text-xs">Total</p>
                                    <p class="font-bold text-teal-800">{{ calcularTotalCupos() }} cupos</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Validación: al menos un turno activo -->
                    <div v-if="!form.turnos.manana.activo && !form.turnos.tarde.activo" 
                        class="bg-red-50 border border-red-200 rounded-lg p-3 text-red-600 text-sm flex items-center gap-2">
                        <i class="pi pi-exclamation-triangle"></i>
                        Debe activar al menos un turno (mañana o tarde)
                    </div>

                    <!-- Botones -->
                    <div class="flex gap-3 pt-2">
                        <button type="submit" 
                            :disabled="isLoading || form.dias_seleccionados.length === 0 || (!form.turnos.manana.activo && !form.turnos.tarde.activo)"
                            class="flex-1 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-xl transition flex items-center justify-center gap-2">
                            <i v-if="isLoading" class="pi pi-spin pi-spinner"></i>
                            <i v-else class="pi pi-check-circle"></i>
                            {{ isLoading ? 'Guardando...' : 'Crear Horarios' }}
                        </button>
                        <button type="button" @click="cerrarModal"
                            class="px-6 py-3 border-2 border-gray-300 text-gray-600 hover:bg-gray-50 font-semibold rounded-xl transition">
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
```

### 3. Actualizar el Script del Componente

```typescript
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import horarioService, { type Horario, type HorarioDia } from '../../services/horarioService'

const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const diasSemanaCompletos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const areas = ref<any[]>([])
const medicos = ref<any[]>([])
const horariosList = ref<Horario[]>([])
const filtroAreaId = ref<number | null>(null)
const filtroMedicoId = ref<number | null>(null)
const filtroMes = ref('')
const filtroTurno = ref<'M' | 'T' | null>(null)  // NUEVO: filtro por turno
const vistaActual = ref<'tabla' | 'tarjetas' | 'calendario'>('tabla')

const modalVisible = ref(false)
const isLoading = ref(false)
const isLoadingList = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')

// NUEVO: Estructura del formulario con turnos
const form = ref({
    medico_id: null as number | null,
    area_id: null as number | null,
    mes: '',
    dias_seleccionados: [] as number[],
    turnos: {
        manana: {
            activo: true,
            cupos: 5
        },
        tarde: {
            activo: true,
            cupos: 7
        }
    }
})

// Calcular total de cupos
const calcularTotalCupos = () => {
    const dias = contarDiasLaborables()
    let total = 0
    if (form.value.turnos.manana.activo) {
        total += dias * form.value.turnos.manana.cupos
    }
    if (form.value.turnos.tarde.activo) {
        total += dias * form.value.turnos.tarde.cupos
    }
    return total
}

// Contar días laborables del mes
const contarDiasLaborables = () => {
    if (!form.value.mes || form.value.dias_seleccionados.length === 0) return 0

    const parts = form.value.mes.split('-').map(Number)
    if (parts.length < 2 || parts[0] === undefined || parts[1] === undefined) return 0
    const year = parts[0]
    const month = parts[1]
    const ultimoDia = new Date(year, month, 0).getDate()
    let contador = 0

    for (let dia = 1; dia <= ultimoDia; dia++) {
        const fecha = new Date(year, month - 1, dia)
        const diaSemana = fecha.getDay() === 0 ? 6 : fecha.getDay() - 1
        if (form.value.dias_seleccionados.includes(diaSemana)) {
            contador++
        }
    }

    return contador
}

// Abrir modal con valores por defecto
const abrirModalHorario = () => {
    modalVisible.value = true
    const hoy = new Date()
    const mesActual = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`

    form.value = {
        medico_id: null,
        area_id: null,
        mes: mesActual,
        dias_seleccionados: [0, 1, 2, 3, 4],  // Lun-Vie por defecto
        turnos: {
            manana: {
                activo: true,
                cupos: 5
            },
            tarde: {
                activo: true,
                cupos: 7
            }
        }
    }
}

// ACTUALIZADO: Guardar horarios mensuales con nuevo endpoint
const guardarHorarioMensual = async () => {
    if (!form.value.medico_id || !form.value.area_id || form.value.dias_seleccionados.length === 0) return
    if (!form.value.turnos.manana.activo && !form.value.turnos.tarde.activo) return

    isLoading.value = true
    try {
        const payload = {
            medico_id: form.value.medico_id,
            area_id: form.value.area_id,
            mes: form.value.mes,
            dias_seleccionados: form.value.dias_seleccionados,
            turnos: form.value.turnos
        }

        const { data } = await horarioService.crearHorariosMensuales(payload)
        
        mostrarToast(`${data.creados} horarios creados, ${data.actualizados} actualizados`, 'success')
        cerrarModal()
        cargarHorariosFiltrados()
    } catch (error: any) {
        console.error('Error al guardar horarios', error)
        const mensaje = error.response?.data?.error || 'Error al guardar los horarios'
        mostrarToast(mensaje, 'error')
    } finally {
        isLoading.value = false
    }
}

// ACTUALIZADO: Cargar horarios con filtro de turno
const cargarHorariosFiltrados = async () => {
    isLoadingList.value = true
    try {
        const params = {
            area_id: filtroAreaId.value,
            medico_id: filtroMedicoId.value,
            mes: filtroMes.value || undefined,
            turno: filtroTurno.value || undefined
        }
        const { data } = await horarioService.getHorarios(params)
        horariosList.value = data

    } catch (error) {
        console.error('Error al cargar horarios', error)
        horariosList.value = []
    } finally {
        isLoadingList.value = false
    }
}

// Resto de funciones...
const seleccionarDiasLaborables = () => {
    form.value.dias_seleccionados = [0, 1, 2, 3, 4]
}

const seleccionarTodosDias = () => {
    form.value.dias_seleccionados = [0, 1, 2, 3, 4, 5, 6]
}

const cerrarModal = () => {
    modalVisible.value = false
}

const eliminarHorario = async (id: number | undefined) => {
    if (!id) return
    if (!confirm('¿Está seguro de eliminar este horario?')) return

    try {
        await horarioService.eliminarHorario(id)
        mostrarToast('Horario eliminado exitosamente', 'success')
        cargarHorariosFiltrados()
    } catch (error) {
        console.error('Error al eliminar horario', error)
        mostrarToast('Error al eliminar horario', 'error')
    }
}

const mostrarToast = (mensaje: string, tipo: 'success' | 'error' = 'success') => {
    toastMessage.value = mensaje
    toastType.value = tipo
    showToast.value = true
    setTimeout(() => {
        showToast.value = false
    }, 3000)
}

// Helpers para la tabla
const getTurnoBadgeClass = (turno: string) => {
    return turno === 'M' 
        ? 'bg-amber-100 text-amber-800' 
        : 'bg-indigo-100 text-indigo-800'
}

onMounted(() => {
    fetchAreas()
    fetchMedicos()
    const hoy = new Date()
    filtroMes.value = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`
    cargarHorariosFiltrados()
})
</script>
```

### 4. Actualizar la Tabla de Horarios

Añadir columna de turno en la tabla:

```vue
<thead class="bg-gray-50 border-b border-gray-200">
    <tr>
        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
            <div class="flex items-center gap-2">
                <i class="pi pi-user text-teal-500"></i>
                Médico
            </div>
        </th>
        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
            <div class="flex items-center gap-2">
                <i class="pi pi-building text-teal-500"></i>
                Área
            </div>
        </th>
        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
            <div class="flex items-center gap-2">
                <i class="pi pi-calendar text-teal-500"></i>
                Fecha
            </div>
        </th>
        <!-- NUEVA COLUMNA -->
        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
            <div class="flex items-center gap-2">
                <i class="pi pi-clock text-teal-500"></i>
                Turno
            </div>
        </th>
        <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">
            <div class="flex items-center gap-2">
                <i class="pi pi-ticket text-teal-500"></i>
                Cupos
            </div>
        </th>
        <th class="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">
            Acciones
        </th>
    </tr>
</thead>
<tbody class="bg-white divide-y divide-gray-100">
    <tr v-for="horario in horariosList" :key="horario.id" class="hover:bg-gray-50 transition-colors">
        <td class="px-6 py-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center font-semibold">
                    {{ getInitials(horario.medico_nombre || '') }}
                </div>
                <span class="font-medium text-gray-900">{{ horario.medico_nombre }}</span>
            </div>
        </td>
        <td class="px-6 py-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {{ horario.area_nombre }}
            </span>
        </td>
        <td class="px-6 py-4">
            <div class="text-gray-700">
                {{ formatearFecha(horario.fecha) }}
            </div>
            <div class="text-xs text-gray-500">
                {{ diasSemanaCompletos[horario.dia_semana] }}
            </div>
        </td>
        <!-- NUEVA CELDA DE TURNO -->
        <td class="px-6 py-4">
            <div class="flex items-center gap-2">
                <span :class="[
                    'px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1',
                    getTurnoBadgeClass(horario.turno)
                ]">
                    <i :class="horario.turno === 'M' ? 'pi pi-sun' : 'pi pi-moon'" class="text-xs"></i>
                    {{ horario.turno_nombre }}
                </span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
                {{ horario.hora_inicio?.slice(0, 5) }} - {{ horario.hora_fin?.slice(0, 5) }}
            </div>
        </td>
        <td class="px-6 py-4">
            <div class="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-lg flex items-center justify-center font-bold">
                {{ horario.cupos }}
            </div>
        </td>
        <td class="px-6 py-4">
            <div class="flex items-center justify-center gap-2">
                <button @click="eliminarHorario(horario.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition">
                    <i class="pi pi-trash"></i>
                </button>
            </div>
        </td>
    </tr>
</tbody>
```

### 5. Añadir Filtro por Turno

En la sección de filtros, añadir:

```vue
<div>
    <label class="block text-sm font-medium text-gray-600 mb-2">
        <i class="pi pi-clock mr-1"></i> Turno
    </label>
    <select v-model="filtroTurno" @change="cargarHorariosFiltrados"
        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500">
        <option :value="null">Todos los turnos</option>
        <option value="M">🌞 Mañana (07:30-13:30)</option>
        <option value="T">🌙 Tarde (13:30-19:30)</option>
    </select>
</div>
```

### 6. Helper para Formatear Fecha

```typescript
const formatearFecha = (fecha: string | undefined) => {
    if (!fecha) return ''
    const date = new Date(fecha + 'T00:00:00')
    return date.toLocaleDateString('es-PE', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric' 
    })
}
```

---

## Resumen de Estadísticas Actualizado

Actualizar el cómputo de `totalCupos` para mostrar desglose por turno:

```typescript
const totalCuposManana = computed(() => {
    return horariosList.value
        .filter(h => h.turno === 'M')
        .reduce((sum, h) => sum + h.cupos, 0)
})

const totalCuposTarde = computed(() => {
    return horariosList.value
        .filter(h => h.turno === 'T')
        .reduce((sum, h) => sum + h.cupos, 0)
})

const totalCupos = computed(() => {
    return totalCuposManana.value + totalCuposTarde.value
})
```

---

## Vista de Calendario Actualizada

Para mostrar ambos turnos en el calendario:

```vue
<div v-for="dia in diasDelMes" :key="dia.fecha" 
    :class="[
        'p-2 rounded-lg border min-h-[100px]',
        dia.esDelMes ? 'bg-white border-gray-200' : 'bg-gray-50 border-gray-100',
        (dia.turnos?.M || dia.turnos?.T) ? 'border-teal-400 border-2' : ''
    ]">
    <div v-if="dia.esDelMes">
        <div class="font-bold text-gray-700 mb-2 text-sm">{{ dia.numero }}</div>
        
        <!-- Turno Mañana -->
        <div v-if="dia.turnos?.M" 
            class="text-xs bg-amber-500 text-white px-2 py-1 rounded mb-1 flex items-center gap-1">
            <i class="pi pi-sun text-[10px]"></i>
            <span>{{ dia.turnos.M.cupos }} cupos</span>
        </div>
        
        <!-- Turno Tarde -->
        <div v-if="dia.turnos?.T" 
            class="text-xs bg-indigo-500 text-white px-2 py-1 rounded flex items-center gap-1">
            <i class="pi pi-moon text-[10px]"></i>
            <span>{{ dia.turnos.T.cupos }} cupos</span>
        </div>
        
        <div v-if="!dia.turnos?.M && !dia.turnos?.T" class="text-xs text-gray-400 italic">
            Sin horario
        </div>
    </div>
</div>
```

---

## Notas Importantes

1. **Horarios Fijos:** Los horarios de inicio/fin ya no se configuran manualmente. Son fijos:
   - Mañana: 07:30 - 13:30
   - Tarde: 13:30 - 19:30

2. **Migración:** El backend ya está actualizado. Solo necesitas adaptar el frontend.

3. **Compatibilidad:** Los endpoints legacy siguen funcionando pero devuelven el nuevo formato.

4. **Constraint Único:** No puede haber dos horarios para el mismo médico, fecha y turno.
