# Guía de Integración Frontend - Sistema de Citas Médicas

## Resumen de Cambios en el Backend

El sistema de citas ha sido actualizado para separar el registro de pacientes de la creación de citas. Ahora funcionan como **2 endpoints independientes**.

---

## Flujo Recomendado

```
┌─────────────────────────────────────────────────────────────────┐
│  1. BUSCAR/REGISTRAR PACIENTE                                   │
│     POST /api/pacientes                                         │
│     └── Retorna: { id, data: {...} }                           │
├─────────────────────────────────────────────────────────────────┤
│  2. CREAR CITA                                                  │
│     POST /api/citas                                             │
│     └── Usa: paciente_id del paso 1 + horario_id seleccionado  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Endpoints Actualizados

### 1. Registrar/Actualizar Paciente

**`POST /api/pacientes`**

Este endpoint **solo** crea o actualiza un paciente. Ya NO crea citas.

#### Request Body:
```json
{
    "dni": "12345678",
    "nombres": "JUAN CARLOS",
    "apellido_paterno": "PÉREZ",
    "apellido_materno": "GARCÍA",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "estado_civil": "S",
    "direccion": "Av. Principal 123",
    "telefono": "999888777",
    "email": "juan@email.com",
    "grado_instruccion": "universitario_completo",
    "religion": "Católica",
    "procedencia": "Lima",
    "seguro": "SIS"
}
```

#### Campos Requeridos:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `dni` | string(8) | DNI del paciente |
| `nombres` | string | Nombres completos |
| `apellido_paterno` | string | Apellido paterno |
| `apellido_materno` | string | Apellido materno |
| `fecha_nacimiento` | string | Formato YYYY-MM-DD |
| `sexo` | string(1) | 'M' o 'F' |
| `estado_civil` | string(1) | 'S', 'C', 'V', 'D' |
| `direccion` | string | Dirección completa |

#### Campos Opcionales:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `telefono` | string | Número de teléfono |
| `email` | string | Correo electrónico |
| `grado_instruccion` | string | Ver enum abajo |
| `religion` | string | Religión |
| `procedencia` | string | Lugar de procedencia |
| `seguro` | string | Tipo de seguro (SIS, ESSALUD) |

**Valores válidos para `grado_instruccion`:**
- `inicial_incompleta`, `inicial_completa`
- `primaria_incompleta`, `primaria_completa`
- `secundaria_incompleta`, `secundaria_completa`
- `tecnico_superior_incompleta`, `tecnico_superior_completa`
- `universitario_incompleto`, `universitario_completo`

#### Response (201 - Nuevo paciente):
```json
{
    "message": "Paciente registrado correctamente",
    "id": 15,
    "is_new": true,
    "data": {
        "id": 15,
        "dni": "12345678",
        "nombres": "JUAN CARLOS",
        // ... todos los datos del paciente
    }
}
```

#### Response (200 - Paciente actualizado):
```json
{
    "message": "Paciente actualizado correctamente",
    "id": 15,
    "is_new": false,
    "data": {
        // ... datos actualizados
    }
}
```

---

### 2. Crear Cita Médica

**`POST /api/citas`**

Este es el **nuevo endpoint** para crear citas.

#### Request Body:
```json
{
    "paciente_id": 15,
    "horario_id": 55,
    "fecha": "2025-12-01",
    "sintomas": "Tos, fiebre y dolor de cabeza",
    "area_id": 1,
    "dni_acompanante": "87654321",
    "nombre_acompanante": "MARÍA GARCÍA",
    "telefono_acompanante": "999111222"
}
```

#### Campos Requeridos:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `paciente_id` | int | ID del paciente (obtenido del paso 1) |
| `horario_id` | int | ID del horario seleccionado |
| `fecha` | string | Fecha de la cita en formato YYYY-MM-DD |
| `sintomas` | string | Descripción de los síntomas |

#### Campos Opcionales:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `area_id` | int | ID del área (se obtiene del horario si no se envía) |
| `dni_acompanante` | string | DNI del acompañante |
| `nombre_acompanante` | string | Nombre del acompañante |
| `telefono_acompanante` | string | Teléfono del acompañante |
| `datos_adicionales` | object | Cualquier dato extra en formato JSON |

#### Response (201 - Cita creada):
```json
{
    "message": "Cita creada exitosamente",
    "data": {
        "id": 10,
        "paciente_id": 15,
        "horario_id": 55,
        "doctor_id": 3,
        "area_id": 1,
        "area": "Medicina General",
        "fecha": "2025-12-01",
        "sintomas": "Tos, fiebre y dolor de cabeza",
        "estado": "pendiente",
        "doctor_nombre": "Dr. Juan Pérez",
        "area_nombre": "Medicina General",
        "horario_turno": "M",
        "horario_turno_nombre": "Mañana"
    },
    "cupos_restantes": 4
}
```

#### Posibles Errores:
| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 400 | `El campo 'X' es obligatorio` | Falta un campo requerido |
| 400 | `No hay cupos disponibles para este horario` | Sin disponibilidad |
| 400 | `La fecha no coincide con el horario seleccionado` | Fecha incorrecta |
| 404 | `Paciente no encontrado` | paciente_id inválido |
| 404 | `Horario no encontrado` | horario_id inválido |

---

### 3. Obtener Horarios con Disponibilidad

**`GET /api/horarios/`**

Ahora incluye `cupos_disponibles` calculado automáticamente.

#### Query Parameters:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `medico_id` | int | Filtrar por médico |
| `area_id` | int | Filtrar por área |
| `mes` | string | Filtrar por mes (YYYY-MM) |
| `fecha` | string | Filtrar por fecha (YYYY-MM-DD) |
| `turno` | string | Filtrar por turno ('M' o 'T') |

#### Response:
```json
[
    {
        "id": 55,
        "medico_id": 3,
        "area_id": 1,
        "fecha": "2025-12-01",
        "dia_semana": 0,
        "turno": "M",
        "turno_nombre": "Mañana",
        "hora_inicio": "07:30:00",
        "hora_fin": "13:30:00",
        "cupos": 5,
        "cupos_disponibles": 3,
        "medico_nombre": "Dr. Juan Pérez",
        "area_nombre": "Medicina General"
    }
]
```

> **NOTA:** `cupos_disponibles` = `cupos` - citas activas (no canceladas)

---

### 4. Listar Citas (Administración)

**`GET /api/citas/`**

Endpoint para listar citas con filtros y paginación. Ahora incluye información completa de paciente, horario y doctor.

#### Query Parameters:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | int | Página actual (default: 1) |
| `per_page` | int | Items por página (default: 10) |
| `fecha` | string | Filtrar por fecha de la cita (YYYY-MM-DD) |
| `fecha_registro` | string | Filtrar por fecha de registro (YYYY-MM-DD) |
| `doctor_id` | int | Filtrar por ID del doctor |
| `area` | string | Filtrar por nombre de área (búsqueda parcial) |
| `area_id` | int | Filtrar por ID de área |
| `estado` | string | Filtrar por estado |
| `paciente_dni` | string | Buscar por DNI del paciente (parcial) |
| `turno` | string | Filtrar por turno ('M' o 'T') |

**Estados válidos:** `pendiente`, `confirmada`, `atendida`, `cancelada`, `referido`

#### Response:
```json
{
    "total": 25,
    "pages": 3,
    "current_page": 1,
    "per_page": 10,
    "data": [
        {
            "id": 21,
            "paciente_id": 3,
            "horario_id": 55,
            "doctor_id": 23,
            "area_id": 1,
            "area": "Medicina general",
            "area_nombre": "Medicina general",
            "fecha": "2025-12-01",
            "fecha_registro": "2025-12-08 04:08:52.271029",
            "sintomas": "Tos, fiebre y dolor de cabeza",
            "estado": "pendiente",
            "doctor_nombre": "Dr. Carlos Alberto Sánchez Ruiz",
            "horario_turno": "M",
            "horario_turno_nombre": "Mañana",
            "dni_acompanante": null,
            "nombre_acompanante": null,
            "telefono_acompanante": null,
            "paciente": {
                "id": 3,
                "nombres": "JUAN CARLOS",
                "apellido_paterno": "PÉREZ",
                "apellido_materno": "GARCÍA",
                "dni": "12345678",
                "telefono": "999888777",
                "email": "juan@email.com"
            },
            "horario": {
                "id": 55,
                "turno": "M",
                "turno_nombre": "Mañana",
                "hora_inicio": "07:30:00",
                "hora_fin": "13:30:00"
            }
        }
    ]
}
```

---

### 5. Obtener Detalle de Cita

**`GET /api/citas/<id>`**

Obtiene el detalle completo de una cita incluyendo información del paciente y horario.

#### Response:
```json
{
    "id": 21,
    "paciente_id": 3,
    "horario_id": 55,
    "doctor_id": 23,
    "area_id": 1,
    "area": "Medicina general",
    "area_nombre": "Medicina general",
    "fecha": "2025-12-01",
    "fecha_registro": "2025-12-08 04:08:52.271029",
    "sintomas": "Tos, fiebre y dolor de cabeza",
    "estado": "pendiente",
    "doctor_nombre": "Dr. Carlos Alberto Sánchez Ruiz",
    "horario_turno": "M",
    "horario_turno_nombre": "Mañana",
    "paciente": {
        "id": 3,
        "nombres": "JUAN CARLOS",
        "apellido_paterno": "PÉREZ",
        "apellido_materno": "GARCÍA",
        "dni": "12345678",
        "telefono": "999888777",
        "email": "juan@email.com",
        "fecha_nacimiento": "1990-05-15",
        "sexo": "M",
        "direccion": "Av. Principal 123",
        "seguro": "SIS"
    },
    "horario": {
        "id": 55,
        "turno": "M",
        "turno_nombre": "Mañana",
        "hora_inicio": "07:30:00",
        "hora_fin": "13:30:00",
        "cupos": 10
    }
}
```

---

### 6. Actualizar Cita

**`PUT /api/citas/<id>`**

Actualiza el estado u otros campos de una cita.

#### Request Body (todos opcionales):
```json
{
    "estado": "confirmada",
    "sintomas": "Actualización de síntomas",
    "doctor_id": 5,
    "area": "Otra área"
}
```

#### Estados disponibles:
- `pendiente` - Cita creada, esperando confirmación
- `confirmada` - Cita confirmada
- `atendida` - Paciente fue atendido
- `cancelada` - Cita cancelada
- `referido` - Paciente referido a otro establecimiento

---

### 7. Eliminar Cita

**`DELETE /api/citas/<id>`**

Elimina permanentemente una cita.

---

### 8. Obtener Citas Confirmadas (Para Impresión)

**`GET /api/citas/confirmadas`**

Endpoint especializado para obtener citas confirmadas ordenadas por fecha de registro (orden de llegada) con numeración automática. Ideal para generar listas de impresión que se publican en la entrada del servicio.

#### Query Parameters (obligatorios):

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| `fecha` | string (YYYY-MM-DD) | ✅ Sí | Fecha de las citas a consultar |
| `area_id` | integer | ✅ Sí | ID del área/servicio |

#### Response (200 OK):
```json
{
    "success": true,
    "fecha": "2025-12-11",
    "area": {
        "id": 1,
        "nombre": "Medicina General"
    },
    "total": 15,
    "citas": [
        {
            "numero": 1,
            "id": 123,
            "paciente": {
                "id": 45,
                "nombres": "Juan Carlos",
                "apellido_paterno": "García",
                "apellido_materno": "López",
                "dni": "12345678",
                "telefono": "987654321"
            },
            "horario": {
                "id": 10,
                "hora_inicio": "08:00:00",
                "hora_fin": "08:15:00",
                "turno": "M",
                "turno_nombre": "Mañana"
            },
            "fecha_registro": "2025-12-10T14:30:00"
        },
        {
            "numero": 2,
            "id": 124,
            "paciente": {
                "id": 46,
                "nombres": "María Elena",
                "apellido_paterno": "Rodríguez",
                "apellido_materno": "Sánchez",
                "dni": "87654321",
                "telefono": "912345678"
            },
            "horario": {
                "id": 11,
                "hora_inicio": "08:15:00",
                "hora_fin": "08:30:00",
                "turno": "M",
                "turno_nombre": "Mañana"
            },
            "fecha_registro": "2025-12-10T15:45:00"
        }
    ]
}
```

#### Posibles Errores:

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 400 | `El parámetro fecha es requerido` | No se envió el parámetro fecha |
| 400 | `El parámetro area_id es requerido` | No se envió el parámetro area_id |
| 400 | `Formato de fecha inválido` | La fecha no tiene formato YYYY-MM-DD |
| 404 | `Área no encontrada` | El area_id no existe en la base de datos |

#### Ejemplo de uso con cURL:

```bash
curl -X GET "http://localhost:5000/api/citas/confirmadas?fecha=2025-12-11&area_id=1"
```

#### TypeScript Service (CitaService):

```typescript
// Interfaces para citas confirmadas
export interface CitaConfirmadaParams {
  fecha: string;       // YYYY-MM-DD
  area_id: number;
}

export interface CitaConfirmadaPaciente {
  id: number;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  dni: string;
  telefono?: string | null;
}

export interface CitaConfirmadaHorario {
  id: number;
  hora_inicio: string;
  hora_fin: string;
  turno: 'M' | 'T';
  turno_nombre: string;
}

export interface CitaConfirmadaItem {
  numero: number;
  id: number;
  paciente: CitaConfirmadaPaciente | null;
  horario: CitaConfirmadaHorario | null;
  fecha_registro: string | null;
}

export interface CitaConfirmadaResponse {
  success: boolean;
  fecha: string;
  area: {
    id: number;
    nombre: string;
  };
  total: number;
  citas: CitaConfirmadaItem[];
}

// Agregar al citaService
const citaService = {
  // ... otros métodos existentes

  // Obtener citas confirmadas para impresión
  getCitasConfirmadas(params: CitaConfirmadaParams) {
    return api.get<CitaConfirmadaResponse>('/citas/confirmadas', { params });
  }
}
```

#### Notas Importantes:

1. **Orden de registro**: La numeración refleja el orden cronológico en que los pacientes registraron su cita (primer registro = número 1).
2. **Estado confirmada**: Solo se incluyen citas que ya han sido confirmadas por el personal del centro de salud.
3. **Uso principal**: Esta lista está pensada para ser impresa y publicada en la entrada del servicio.
4. **Actualización**: Si se confirman más citas después de imprimir, se deberá generar una nueva lista actualizada.

---

### 9. Generar PDF de Citas Confirmadas

**`GET /api/citas/confirmadas/pdf`**

Genera y descarga un archivo PDF con la lista de citas confirmadas. El PDF incluye un diseño profesional con:
- Encabezado con nombre del centro de salud
- Información del área y fecha
- Tabla de citas con numeración, DNI, nombre del paciente, horario y turno
- Pie de página con fecha de generación

#### Query Parameters (obligatorios):

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| `fecha` | string (YYYY-MM-DD) | ✅ Sí | Fecha de las citas a consultar |
| `area_id` | integer | ✅ Sí | ID del área/servicio |

#### Response (200 OK):

Retorna directamente el archivo PDF con el header `Content-Type: application/pdf`.

El archivo se descarga con el nombre: `citas_confirmadas_{area}_{fecha}.pdf`

Por ejemplo: `citas_confirmadas_medicina_general_2025-12-11.pdf`

#### Posibles Errores:

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 400 | `El parámetro fecha es requerido` | No se envió el parámetro fecha |
| 400 | `El parámetro area_id es requerido` | No se envió el parámetro area_id |
| 400 | `Formato de fecha inválido` | La fecha no tiene formato YYYY-MM-DD |
| 404 | `Área no encontrada` | El area_id no existe en la base de datos |

#### Ejemplo de uso con cURL:

```bash
# Descargar PDF directamente
curl -X GET "http://localhost:5000/api/citas/confirmadas/pdf?fecha=2025-12-11&area_id=1" -o citas.pdf

# O abrir en navegador
open "http://localhost:5000/api/citas/confirmadas/pdf?fecha=2025-12-11&area_id=1"
```

#### TypeScript Service (CitaService):

```typescript
// Agregar al citaService
const citaService = {
  // ... otros métodos existentes

  // Descargar PDF de citas confirmadas
  descargarPDFCitasConfirmadas(params: CitaConfirmadaParams) {
    return api.get('/citas/confirmadas/pdf', {
      params,
      responseType: 'blob'  // Importante: recibir como blob para archivos
    });
  }
}

// Ejemplo de uso en un componente Vue
const descargarPDF = async () => {
  try {
    const response = await citaService.descargarPDFCitasConfirmadas({
      fecha: '2025-12-11',
      area_id: 1
    });
    
    // Crear URL del blob y descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `citas_confirmadas_${fecha}_${areaId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error al descargar PDF:', error);
  }
};
```

#### Diseño del PDF:

El PDF generado incluye:
- **Encabezado**: "CENTRO DE SALUD" y "Lista de Citas Confirmadas"
- **Información**: Área, Fecha formateada en español, Total de citas
- **Tabla**: Con columnas N°, DNI, Paciente (apellidos, nombres), Horario, Turno
- **Estilos**: Colores alternados en filas, encabezado azul, bordes suaves
- **Pie de página**: Fecha y hora de generación del documento

---

### 10. Listar Áreas (para filtros)

**`GET /api/areas/`**

Obtiene todas las áreas disponibles para usar en filtros.

#### Response:
```json
[
    {
        "id": 1,
        "nombre": "Medicina general",
        "descripcion": "Atención primaria",
        "activo": true
    },
    {
        "id": 2,
        "nombre": "Pediatría",
        "descripcion": "Atención a niños",
        "activo": true
    }
]
```

---

## Actualización del Frontend

### 1. Actualizar `citaService.ts`

```typescript
import api from './api'

// Interfaces
export interface Paciente {
    id: number
    nombres: string
    apellido_paterno: string
    apellido_materno: string
    dni: string
    telefono?: string | null
    email?: string | null
    fecha_nacimiento?: string | null
    sexo?: string
    direccion?: string
    seguro?: string | null
}

export interface Horario {
    id: number
    turno: 'M' | 'T'
    turno_nombre: string
    hora_inicio: string
    hora_fin: string
    cupos?: number
}

export interface Cita {
    id: number
    paciente_id: number
    horario_id: number | null
    doctor_id: number | null
    area_id: number | null
    area: string | null
    area_nombre: string | null
    fecha: string | null
    fecha_registro: string
    sintomas: string
    estado: string
    doctor_nombre: string | null
    horario_turno: 'M' | 'T' | null
    horario_turno_nombre: string | null
    dni_acompanante: string | null
    nombre_acompanante: string | null
    telefono_acompanante: string | null
    datos_adicionales: Record<string, any> | null
    paciente?: Paciente
    horario?: Horario
}

export interface CrearCitaPayload {
    paciente_id: number
    horario_id: number
    fecha: string  // YYYY-MM-DD
    sintomas: string
    area_id?: number
    dni_acompanante?: string
    nombre_acompanante?: string
    telefono_acompanante?: string
    datos_adicionales?: Record<string, any>
}

export interface ListarCitasParams {
    page?: number
    per_page?: number
    fecha?: string           // Fecha de la cita (YYYY-MM-DD)
    fecha_registro?: string  // Fecha de registro (YYYY-MM-DD)
    doctor_id?: number
    area?: string            // Búsqueda por nombre de área
    area_id?: number         // Filtrar por ID de área
    estado?: string          // pendiente, confirmada, atendida, cancelada, referido
    paciente_dni?: string    // Búsqueda parcial por DNI
    turno?: 'M' | 'T'        // Filtrar por turno
}

export interface ListarCitasResponse {
    total: number
    pages: number
    current_page: number
    per_page: number
    data: Cita[]
}

const citaService = {
    // Crear nueva cita
    crearCita(payload: CrearCitaPayload) {
        return api.post<{
            message: string
            data: Cita
            cupos_restantes: number
        }>('/citas/', payload)
    },

    // Listar citas con filtros y paginación
    getCitas(params?: ListarCitasParams) {
        return api.get<ListarCitasResponse>('/citas/', { params })
    },

    // Obtener cita por ID (detalle completo)
    getCita(id: number) {
        return api.get<Cita>(`/citas/${id}`)
    },

    // Actualizar cita (estado, sintomas, etc.)
    actualizarCita(id: number, data: Partial<Cita>) {
        return api.put<Cita>(`/citas/${id}`, data)
    },

    // Eliminar cita permanentemente
    eliminarCita(id: number) {
        return api.delete<{ message: string }>(`/citas/${id}`)
    }
}

export default citaService
```

### 2. Actualizar `pacienteService.ts`

```typescript
import api from './api'

export interface RegistrarPacientePayload {
    dni: string
    nombres: string
    apellido_paterno: string
    apellido_materno: string
    fecha_nacimiento: string
    sexo: string
    estado_civil: string
    direccion: string
    telefono?: string
    email?: string
    grado_instruccion?: string
    religion?: string
    procedencia?: string
    seguro?: string
}

export interface PacienteResponse {
    id: number
    dni: string
    nombres: string
    apellido_paterno: string
    apellidoPaterno: string  // Alias para compatibilidad
    apellido_materno: string
    apellidoMaterno: string  // Alias para compatibilidad
    fecha_nacimiento: string
    fechaNacimiento: string  // Alias para compatibilidad
    edad: number
    sexo: string
    estado_civil: string
    grado_instruccion: string | null
    religion: string | null
    procedencia: string | null
    telefono: string | null
    email: string | null
    direccion: string
    seguro: string | null
}

const pacienteService = {
    // Registrar o actualizar paciente
    crearPaciente(payload: RegistrarPacientePayload) {
        return api.post<{
            message: string
            id: number
            is_new: boolean
            data: PacienteResponse
        }>('/pacientes/', payload)
    },

    // Buscar paciente por DNI
    buscarPorDNI(dni: string) {
        return api.get<PacienteResponse>(`/pacientes/buscar/${dni}`)
    },

    // Listar pacientes
    listarPacientes(params?: {
        page?: number
        per_page?: number
        search?: string
    }) {
        return api.get('/pacientes/', { params })
    }
}

export default pacienteService
```

### 3. Actualizar el componente `PacienteRegistro.vue`

Mmodifica el método `onSubmit` para usar el nuevo flujo:

```typescript
const onSubmit = handleSubmit(async (values) => {
    if (!horarioSeleccionado.value || !diaSeleccionado.value) {
        alert("Por favor seleccione una fecha y horario para la cita.");
        return;
    }

    try {
        isSubmitting.value = true;

        // 1. Registrar o actualizar paciente
        const pacientePayload = {
            dni: values.dni,
            nombres: values.nombres,
            apellido_paterno: values.apellidoPaterno,
            apellido_materno: values.apellidoMaterno,
            fecha_nacimiento: values.fechaNacimiento,
            sexo: values.sexo,
            estado_civil: values.estado_civil,
            direccion: values.direccion,
            telefono: values.telefono,
            email: values.email,
            grado_instruccion: values.gradoInstruccion,
            religion: values.religion,
            procedencia: values.procedencia,
            seguro: values.tipoSeguro,
        };

        const { data: pacienteData } = await pacienteService.crearPaciente(pacientePayload);
        
        console.log('Paciente registrado:', pacienteData);

        // 2. Crear la cita usando el nuevo endpoint
        const citaPayload = {
            paciente_id: pacienteData.id,
            horario_id: horarioSeleccionado.value.id,
            fecha: diaSeleccionado.value.fecha,
            sintomas: values.sintomas,
            area_id: areaSeleccionada.value?.id,
            dni_acompanante: values.dniAcompanante,
            nombre_acompanante: values.nombreAcompanante,
            telefono_acompanante: values.telefonoAcompanante,
        };

        const { data: citaData } = await citaService.crearCita(citaPayload);
        
        console.log('Cita creada:', citaData);
        console.log('Cupos restantes:', citaData.cupos_restantes);

        // Mostrar mensaje de éxito
        showSuccess.value = true;
        setTimeout(() => {
            showSuccess.value = false;
        }, 3000);

        // Limpiar formulario después del registro
        resetForm();

    } catch (error: any) {
        console.error('Error:', error);
        
        // Mostrar error específico del backend
        const errorMessage = error.response?.data?.error 
            || error.response?.data?.message 
            || 'Hubo un error al registrar';
        
        alert(errorMessage);
    } finally {
        isSubmitting.value = false;
    }
}, () => {
    // Callback cuando hay errores de validación
    scrollToFirstError();
});
```

---

## Validaciones Importantes

### En el Frontend:
1. Asegurar que `horarioSeleccionado` tenga un `id` válido
2. La `fecha` debe coincidir con la fecha del horario
3. Los `sintomas` son obligatorios

### En el Backend:
1. Se valida que el paciente exista
2. Se valida que el horario exista
3. Se valida que la fecha coincida con el horario
4. Se validan los cupos disponibles
5. Las citas canceladas no cuentan para los cupos

---

## Estructura de Datos Actualizada

### Tabla `citas` (nuevos campos):
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `horario_id` | FK | Referencia a horarios_medicos |
| `area_id` | FK | Referencia a areas |
| `fecha` | DATE | Fecha específica de la cita |

### Respuesta de Horarios (nuevo campo):
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cupos_disponibles` | int | Cupos restantes (cupos - citas activas) |

---

## Migración de Base de Datos

Si aún no has ejecutado la migración, ejecuta:

```bash
cd /home/royer/Desktop/back-citas
source venv/bin/activate
python migrate_citas.py
```

---

## Prueba Rápida con cURL

### 1. Registrar Paciente:
```bash
curl -X POST http://localhost:5000/api/pacientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "nombres": "JUAN CARLOS",
    "apellido_paterno": "PÉREZ",
    "apellido_materno": "GARCÍA",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "estado_civil": "S",
    "direccion": "Av. Principal 123"
  }'
```

### 2. Crear Cita:
```bash
curl -X POST http://localhost:5000/api/citas/ \
  -H "Content-Type: application/json" \
  -d '{
    "paciente_id": 1,
    "horario_id": 55,
    "fecha": "2025-12-01",
    "sintomas": "Tos, fiebre y dolor de cabeza",
    "area_id": 1
  }'
```

---

## Resumen de Cambios

| Antes | Ahora |
|-------|-------|
| POST /pacientes creaba paciente + cita | POST /pacientes solo crea paciente |
| No existía POST /citas | POST /citas crea citas independientes |
| horarios no tenía cupos_disponibles | GET /horarios incluye cupos_disponibles |
| Cita sin relación a horario | Cita vinculada a horario_id específico |

---

## 4. Adaptación del Componente AdminCitas.vue

El componente de administración necesita los siguientes ajustes:

### Cambios en las interfaces:

```typescript
interface Paciente {
  id: number
  nombres: string
  apellido_paterno: string
  apellido_materno: string
  dni: string
  telefono?: string | null
  email?: string | null
}

interface Horario {
  id: number
  turno: 'M' | 'T'
  turno_nombre: string
  hora_inicio: string
  hora_fin: string
}

interface Cita {
  id: number
  fecha: string | null          // Fecha de la cita (YYYY-MM-DD)
  fecha_registro: string        // Cuando se registró
  estado: string
  area: string | null
  area_nombre: string | null
  area_id: number | null
  doctor_id: number | null
  doctor_nombre: string | null
  horario_id: number | null
  horario_turno: 'M' | 'T' | null
  horario_turno_nombre: string | null
  sintomas: string
  observaciones?: string
  paciente: Paciente
  horario?: Horario
  dni_acompanante?: string | null
  nombre_acompanante?: string | null
  telefono_acompanante?: string | null
}
```

### Cambios en el filtro de áreas:

Para cargar áreas dinámicamente desde el backend:

```typescript
import api from '../services/api'

interface Area {
  id: number
  nombre: string
  descripcion?: string
  activo: boolean
}

const areas = ref<Area[]>([])

const fetchAreas = async () => {
  try {
    const { data } = await api.get<Area[]>('/areas/')
    areas.value = data.filter(a => a.activo)
  } catch (error) {
    console.error('Error al cargar áreas', error)
  }
}

onMounted(() => {
  fetchAreas()
  fetchCitas()
})
```

### Actualizar el template de filtros:

```vue
<!-- Filtro por área (dinámico) -->
<div>
  <label for="filtroArea" class="block text-sm font-medium text-gray-700 mb-2">
    Área
  </label>
  <select id="filtroArea" v-model="filtros.area"
    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white">
    <option value="">Todas las áreas</option>
    <option v-for="area in areas" :key="area.id" :value="area.nombre">
      {{ area.nombre }}
    </option>
  </select>
</div>
```

### Mostrar fecha de cita y turno en la tabla:

```vue
<td class="px-6 py-4 whitespace-nowrap">
  <!-- Mostrar fecha de la cita (no fecha_registro) -->
  <div v-if="cita.fecha" class="text-sm font-medium text-gray-900">
    {{ formatFecha(cita.fecha) }}
  </div>
  <div v-else class="text-sm font-medium text-gray-500">
    Sin programar
  </div>
  <!-- Mostrar turno si existe -->
  <div v-if="cita.horario_turno" class="mt-1">
    <span :class="[
      'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
      cita.horario_turno === 'M' 
        ? 'bg-amber-100 text-amber-800' 
        : 'bg-indigo-100 text-indigo-800'
    ]">
      <i :class="cita.horario_turno === 'M' ? 'pi pi-sun' : 'pi pi-moon'" class="mr-1 text-[10px]"></i>
      {{ cita.horario_turno_nombre }}
    </span>
  </div>
</td>
```

### Función para formatear fecha:

```typescript
const formatFecha = (fechaStr: string): string => {
  if (!fechaStr) return ''
  const fecha = new Date(fechaStr + 'T00:00:00') // Evitar problemas de timezone
  return fecha.toLocaleDateString('es-PE', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatFechaHora = (fechaRegistro: string) => {
  if (!fechaRegistro) return { fecha: '', hora: '' }
  const date = new Date(fechaRegistro)
  return {
    fecha: date.toLocaleDateString('es-PE'),
    hora: date.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  }
}
```

### Usar fecha de cita en lugar de fecha_registro:

Si deseas mostrar la **fecha programada de la cita** en lugar de cuándo se registró:

```vue
<td class="px-6 py-4 whitespace-nowrap">
  <div class="text-sm font-medium text-gray-900">
    {{ cita.fecha ? formatFecha(cita.fecha) : formatFechaHora(cita.fecha_registro).fecha }}
  </div>
  <div v-if="cita.horario" class="text-sm text-gray-500">
    {{ cita.horario.hora_inicio?.slice(0,5) }} - {{ cita.horario.hora_fin?.slice(0,5) }}
  </div>
</td>
```

---

## Resumen de Nuevos Campos en Respuestas

### En cada cita ahora recibes:

| Campo | Descripción |
|-------|-------------|
| `fecha` | Fecha programada de la cita (YYYY-MM-DD) |
| `horario_id` | ID del horario seleccionado |
| `horario_turno` | 'M' o 'T' |
| `horario_turno_nombre` | "Mañana" o "Tarde" |
| `area_id` | ID del área |
| `area_nombre` | Nombre del área |
| `doctor_nombre` | Nombre completo del doctor |
| `paciente.telefono` | Teléfono del paciente |
| `paciente.email` | Email del paciente |
| `horario.hora_inicio` | Hora de inicio del turno |
| `horario.hora_fin` | Hora de fin del turno |


---

## Dashboard API

Estos endpoints están diseñados específicamente para alimentar el dashboard principal.

### 1. Obtener Estadísticas Generales

**`GET /api/dashboard/stats`**

Retorna los contadores para las tarjetas del dashboard.

#### Response:
```json
{
    "totalPacientes": 1248,
    "citasHoy": 42,
    "citasPendientesHoy": 15,
    "medicosActivos": 18,
    "citasPendientesTotal": 86
}
```

### 2. Obtener Próximas Citas

**`GET /api/dashboard/upcoming-appointments`**

Retorna una lista de las próximas citas (incluyendo las de hoy), ordenadas por fecha y hora. Limite: 10.

#### Response:
```json
[
    {
        "id": 21,
        "fecha": "2024-12-08",
        "hora": "07:30 AM",
        "paciente": "JUAN PÉREZ GARCÍA",
        "doctor": "DR. CARLOS MENDOZA",
        "especialidad": "Medicina general",
        "estado": "Pendiente"
    },
    {
        "id": 22,
        "fecha": "2024-12-08",
        "hora": "Tarde",
        "paciente": "MARÍA LÓPEZ",
        "doctor": "Sin asignar",
        "especialidad": "Pediatría",
        "estado": "Confirmada"
    }
]
```

### 3. Obtener Citas por Especialidad (Hoy)

**`GET /api/dashboard/appointments-by-specialty`**

Retorna la distribución de citas para el día actual agrupadas por especialidad (Área).

#### Response:
```json
[
    {
        "nombre": "Medicina general",
        "cantidad": 15,
        "porcentaje": 45.0
    },
    {
        "nombre": "Odontología",
        "cantidad": 12,
        "porcentaje": 35.0
    }
]
```

---

## Gestión de Usuarios del Sistema

Los siguientes endpoints permiten administrar los usuarios del sistema (administradores, médicos y asistentes).

> **Nota:** Todos los endpoints de gestión de usuarios requieren autenticación y rol de **administrador**.

---

### 1. Listar Usuarios

**`GET /api/auth/users`**

Lista todos los usuarios del sistema con filtros opcionales.

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Query Parameters:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `role` | string | Filtrar por rol ('admin', 'medico', 'asistente') |
| `search` | string | Buscar por nombre, username o DNI |

#### Response:
```json
[
    {
        "id": 1,
        "name": "Carlos Mendoza García",
        "username": "cmendoza",
        "role": "admin",
        "dni": "12345678",
        "activo": true,
        "createdAt": null
    },
    {
        "id": 2,
        "name": "María González Ruiz",
        "username": "mgonzalez",
        "role": "medico",
        "dni": "87654321",
        "activo": true,
        "createdAt": null
    }
]
```

---

### 2. Obtener Usuario por ID

**`GET /api/auth/users/<id>`**

Obtiene los detalles de un usuario específico.

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Response:
```json
{
    "id": 1,
    "name": "Carlos Mendoza García",
    "username": "cmendoza",
    "role": "admin",
    "dni": "12345678",
    "activo": true,
    "createdAt": null
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Usuario no encontrado` |

---

### 3. Crear Usuario

**`POST /api/auth/users`**

Crea un nuevo usuario en el sistema.

#### Headers:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body:
```json
{
    "name": "Juan Pérez López",
    "username": "jperez",
    "password": "password123",
    "role": "medico"
}
```

#### Campos:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ✅ | Nombre completo del usuario |
| `username` | string | ✅ | Nombre de usuario único |
| `password` | string | ✅ | Contraseña |
| `role` | string | ✅ | Rol: 'admin', 'medico', 'asistente' |
| `dni` | string | ❌ | DNI (si no se envía, se usa el username) |

#### Response (201):
```json
{
    "message": "Usuario creado correctamente",
    "usuario": {
        "id": 10,
        "name": "Juan Pérez López",
        "username": "jperez",
        "role": "medico",
        "dni": "jperez",
        "activo": true,
        "createdAt": null
    }
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 400 | `El campo 'X' es obligatorio` |
| 409 | `El nombre de usuario ya está registrado` |
| 409 | `El DNI ya está registrado` |

---

### 4. Actualizar Usuario

**`PUT /api/auth/users/<id>`**

Actualiza los datos de un usuario existente.

#### Headers:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body (todos los campos son opcionales):
```json
{
    "name": "Juan Carlos Pérez López",
    "username": "jcperez",
    "password": "nuevaPassword123",
    "role": "admin",
    "activo": true
}
```

#### Campos:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | string | Nuevo nombre completo |
| `username` | string | Nuevo nombre de usuario |
| `password` | string | Nueva contraseña (dejar vacío para no cambiar) |
| `role` | string | Nuevo rol: 'admin', 'medico', 'asistente' |
| `activo` | boolean | Estado del usuario |

#### Response (200):
```json
{
    "message": "Usuario actualizado correctamente",
    "usuario": {
        "id": 10,
        "name": "Juan Carlos Pérez López",
        "username": "jcperez",
        "role": "admin",
        "dni": "jperez",
        "activo": true
    }
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Usuario no encontrado` |
| 409 | `El nombre de usuario ya está en uso` |

---

### 5. Eliminar Usuario

**`DELETE /api/auth/users/<id>`**

Elimina permanentemente un usuario del sistema.

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Response (200):
```json
{
    "message": "Usuario eliminado correctamente"
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Usuario no encontrado` |
| 400 | `No se puede eliminar el único administrador del sistema` |

---

## Servicio TypeScript para Usuarios

### `userService.ts`

```typescript
import api from './api'

// Interfaces
export interface User {
    id: number
    name: string
    username: string
    role: 'admin' | 'medico' | 'asistente'
    dni?: string
    activo?: boolean
    createdAt?: string | null
}

export interface CreateUserPayload {
    name: string
    username: string
    password: string
    role: 'admin' | 'medico' | 'asistente'
    dni?: string
}

export interface UpdateUserPayload {
    name?: string
    username?: string
    password?: string
    role?: 'admin' | 'medico' | 'asistente'
    activo?: boolean
}

export interface ListUsersParams {
    role?: 'admin' | 'medico' | 'asistente'
    search?: string
}

const userService = {
    // Listar todos los usuarios
    getUsers(params?: ListUsersParams) {
        return api.get<User[]>('/auth/users', { params })
    },

    // Obtener usuario por ID
    getUser(id: number) {
        return api.get<User>(`/auth/users/${id}`)
    },

    // Crear nuevo usuario
    createUser(payload: CreateUserPayload) {
        return api.post<{
            message: string
            usuario: User
        }>('/auth/users', payload)
    },

    // Actualizar usuario
    updateUser(id: number, payload: UpdateUserPayload) {
        return api.put<{
            message: string
            usuario: User
        }>(`/auth/users/${id}`, payload)
    },

    // Eliminar usuario
    deleteUser(id: number) {
        return api.delete<{
            message: string
        }>(`/auth/users/${id}`)
    }
}

export default userService
```

---

## Mapeo de Roles

El backend usa nombres de roles diferentes al frontend:

| Frontend | Backend |
|----------|---------|
| `admin` | `administrador` |
| `medico` | `medico` |
| `asistente` | `asistente` |

> El mapeo se realiza automáticamente en el backend, por lo que el frontend siempre trabaja con los valores simplificados (`admin`, `medico`, `asistente`).

---

## Endpoints de Gestión de Pacientes (Nuevos)

### 9. Obtener Paciente por ID

**`GET /api/pacientes/<id>`**

Obtiene los datos completos de un paciente específico.

#### Response (200):
```json
{
    "id": 1,
    "dni": "12345678",
    "nombres": "JUAN CARLOS",
    "apellido_paterno": "PÉREZ",
    "apellidoPaterno": "PÉREZ",
    "apellido_materno": "GARCÍA",
    "apellidoMaterno": "GARCÍA",
    "fecha_nacimiento": "1990-05-15",
    "fechaNacimiento": "1990-05-15",
    "edad": 34,
    "sexo": "M",
    "estado_civil": "S",
    "grado_instruccion": "universitario_completo",
    "religion": "Católica",
    "procedencia": "Lima",
    "ocupacion": "Ingeniero de Sistemas",
    "telefono": "999888777",
    "email": "juan@email.com",
    "direccion": "Av. Principal 123",
    "seguro": "SIS",
    "numero_seguro": "123456789",
    "fecha_registro": "2025-12-01 10:30:00"
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Paciente no encontrado` |

---

### 10. Actualizar Paciente

**`PUT /api/pacientes/<id>`**

Actualiza los datos de un paciente existente. Solo se actualizan los campos enviados.

#### Request Body (todos opcionales):
```json
{
    "nombres": "JUAN CARLOS ACTUALIZADO",
    "apellido_paterno": "PÉREZ",
    "apellido_materno": "GARCÍA",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "estado_civil": "C",
    "grado_instruccion": "universitario_completo",
    "religion": "Católica",
    "procedencia": "Lima",
    "ocupacion": "Gerente de TI",
    "telefono": "999888777",
    "email": "nuevo@email.com",
    "direccion": "Nueva dirección 456",
    "seguro": "ESSALUD",
    "numero_seguro": "987654321"
}
```

#### Response (200):
```json
{
    "message": "Paciente actualizado correctamente",
    "data": {
        "id": 1,
        "dni": "12345678",
        "nombres": "JUAN CARLOS ACTUALIZADO",
        // ... todos los campos actualizados
    }
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Paciente no encontrado` |

---

### 11. Historial de Citas de un Paciente

**`GET /api/pacientes/<id>/historial`**

Obtiene el historial completo de citas de un paciente con paginación.

#### Query Parameters:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | int | Página actual (default: 1) |
| `per_page` | int | Items por página (default: 10) |
| `estado` | string | Filtrar por estado (pendiente, confirmada, atendida, cancelada, referido) |

#### Response (200):
```json
{
    "paciente": {
        "id": 1,
        "dni": "12345678",
        "nombre_completo": "PÉREZ GARCÍA, JUAN CARLOS"
    },
    "total": 15,
    "pages": 2,
    "current_page": 1,
    "per_page": 10,
    "data": [
        {
            "id": 45,
            "paciente_id": 1,
            "horario_id": 55,
            "doctor_id": 3,
            "area_id": 1,
            "area": "Medicina General",
            "area_nombre": "Medicina General",
            "fecha": "2025-12-08",
            "sintomas": "Control mensual",
            "estado": "atendida",
            "doctor_nombre": "Dr. Juan Pérez",
            "horario_turno": "M",
            "horario_turno_nombre": "Mañana",
            "fecha_registro": "2025-12-08 10:30:00",
            "dni_acompanante": null,
            "nombre_acompanante": null,
            "telefono_acompanante": null,
            "horario": {
                "id": 55,
                "turno": "M",
                "turno_nombre": "Mañana",
                "hora_inicio": "07:30:00",
                "hora_fin": "13:30:00"
            }
        },
        {
            "id": 32,
            "fecha": "2025-11-15",
            "sintomas": "Dolor de cabeza intenso",
            "estado": "atendida",
            "area_nombre": "Neurología",
            "doctor_nombre": "Dra. María López",
            // ... más campos
        }
    ]
}
```

#### Errores:
| Código | Mensaje |
|--------|---------|
| 404 | `Paciente no encontrado` |

---

## Guía de Implementación Frontend - Directorio de Pacientes

A continuación se detalla cómo implementar las funcionalidades de **historial de citas** y **edición de paciente** en el componente `DirectorioPacientes.vue`.

### 1. Actualizar `pacienteService.ts`

Agregar los nuevos métodos al servicio:

```typescript
import api from './api'

export interface Paciente {
    id: number
    dni: string
    nombres: string
    apellido_paterno: string
    apellidoPaterno: string
    apellido_materno: string
    apellidoMaterno: string
    fecha_nacimiento: string
    fechaNacimiento: string
    edad: number
    sexo: string
    estado_civil: string
    grado_instruccion: string | null
    religion: string | null
    procedencia: string | null
    ocupacion: string | null
    telefono: string | null
    email: string | null
    direccion: string
    seguro: string | null
    numero_seguro: string | null
    fecha_registro: string
}

export interface HistorialCita {
    id: number
    paciente_id: number
    horario_id: number | null
    doctor_id: number | null
    area_id: number | null
    area: string | null
    area_nombre: string | null
    fecha: string | null
    sintomas: string
    estado: string
    doctor_nombre: string | null
    horario_turno: 'M' | 'T' | null
    horario_turno_nombre: string | null
    fecha_registro: string
    dni_acompanante: string | null
    nombre_acompanante: string | null
    telefono_acompanante: string | null
    horario?: {
        id: number
        turno: 'M' | 'T'
        turno_nombre: string
        hora_inicio: string
        hora_fin: string
    }
}

export interface HistorialResponse {
    paciente: {
        id: number
        dni: string
        nombre_completo: string
    }
    total: number
    pages: number
    current_page: number
    per_page: number
    data: HistorialCita[]
}

export interface UpdatePacientePayload {
    nombres?: string
    apellido_paterno?: string
    apellido_materno?: string
    fecha_nacimiento?: string
    sexo?: string
    estado_civil?: string
    grado_instruccion?: string
    religion?: string
    procedencia?: string
    ocupacion?: string
    telefono?: string
    email?: string
    direccion?: string
    seguro?: string
    numero_seguro?: string
}

const pacienteService = {
    // Listar pacientes con paginación y búsqueda
    getPacientes(params?: {
        page?: number
        per_page?: number
        search?: string
    }) {
        return api.get<{
            total: number
            pages: number
            current_page: number
            per_page: number
            data: Paciente[]
        }>('/pacientes/', { params })
    },

    // Obtener paciente por ID
    getPaciente(id: number) {
        return api.get<Paciente>(`/pacientes/${id}`)
    },

    // Buscar paciente por DNI
    buscarPorDNI(dni: string) {
        return api.get<Paciente>(`/pacientes/buscar/${dni}`)
    },

    // Registrar nuevo paciente
    crearPaciente(payload: any) {
        return api.post<{
            message: string
            id: number
            is_new: boolean
            data: Paciente
        }>('/pacientes/', payload)
    },

    // Actualizar paciente existente
    updatePaciente(id: number, payload: UpdatePacientePayload) {
        return api.put<{
            message: string
            data: Paciente
        }>(`/pacientes/${id}`, payload)
    },

    // Obtener historial de citas de un paciente
    getHistorialCitas(pacienteId: number, params?: {
        page?: number
        per_page?: number
        estado?: string
    }) {
        return api.get<HistorialResponse>(`/pacientes/${pacienteId}/historial`, { params })
    }
}

export default pacienteService
```

---

### 2. Actualizar `DirectorioPacientes.vue`

Agregar las nuevas funcionalidades y modales:

```vue
<template>
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <!-- Buscador y Filtros (sin cambios) -->
        <div class="p-6 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center gap-4">
            <h2 class="text-lg font-semibold text-gray-800">Directorio de Pacientes</h2>
            <div class="relative w-full md:w-96">
                <input type="text" v-model="busquedaPaciente" placeholder="Buscar por DNI o Nombre..."
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent">
                <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-3 text-gray-400" />
            </div>
        </div>

        <!-- Tabla (con handlers actualizados) -->
        <div class="overflow-x-auto">
            <table class="w-full">
                <!-- ... thead sin cambios ... -->
                <tbody class="bg-white divide-y divide-gray-200">
                    <!-- ... estados de carga y vacío sin cambios ... -->
                    <template v-else>
                        <tr v-for="paciente in pacientes" :key="paciente.id" class="hover:bg-gray-50">
                            <!-- ... celdas sin cambios hasta acciones ... -->
                            <td class="px-6 py-4 text-sm font-medium">
                                <button 
                                    @click="verHistorial(paciente)" 
                                    class="text-teal-600 hover:text-teal-900 mr-3" 
                                    title="Ver Historial">
                                    <ClockIcon class="w-5 h-5" />
                                </button>
                                <button 
                                    @click="editarPaciente(paciente)" 
                                    class="text-blue-600 hover:text-blue-900" 
                                    title="Editar">
                                    <PencilIcon class="w-5 h-5" />
                                </button>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>

        <!-- Paginación (sin cambios) -->
        <!-- ... -->
    </div>

    <!-- MODAL: Historial de Citas -->
    <Teleport to="body">
        <div v-if="showHistorialModal" 
            class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
                <!-- Header -->
                <div class="bg-teal-600 text-white p-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-bold">Historial de Citas</h3>
                        <p class="text-teal-100 text-sm">{{ historialData?.paciente?.nombre_completo }}</p>
                    </div>
                    <button @click="closeHistorialModal" class="text-white hover:text-teal-200">
                        <XMarkIcon class="w-6 h-6" />
                    </button>
                </div>

                <!-- Filtros del historial -->
                <div class="p-4 border-b bg-gray-50 flex gap-4">
                    <select v-model="historialFiltroEstado" @change="fetchHistorial"
                        class="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                        <option value="">Todos los estados</option>
                        <option value="pendiente">Pendiente</option>
                        <option value="confirmada">Confirmada</option>
                        <option value="atendida">Atendida</option>
                        <option value="cancelada">Cancelada</option>
                        <option value="referido">Referido</option>
                    </select>
                </div>

                <!-- Lista de citas -->
                <div class="overflow-y-auto max-h-[60vh] p-4">
                    <div v-if="loadingHistorial" class="text-center py-8">
                        <ArrowPathIcon class="w-8 h-8 animate-spin text-teal-500 mx-auto mb-2" />
                        <span class="text-gray-500">Cargando historial...</span>
                    </div>

                    <div v-else-if="historialCitas.length === 0" class="text-center py-8 text-gray-500">
                        <ClockIcon class="w-12 h-12 mx-auto mb-2 text-gray-300" />
                        <p>No hay citas registradas</p>
                    </div>

                    <div v-else class="space-y-4">
                        <div v-for="cita in historialCitas" :key="cita.id" 
                            class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="flex items-center gap-2 mb-1">
                                        <span class="font-semibold text-gray-800">{{ cita.fecha || 'Sin fecha' }}</span>
                                        <span :class="getEstadoClass(cita.estado)" 
                                            class="px-2 py-0.5 text-xs font-medium rounded-full">
                                            {{ cita.estado }}
                                        </span>
                                    </div>
                                    <p class="text-sm text-gray-600">{{ cita.area_nombre }}</p>
                                    <p class="text-sm text-gray-500">Dr(a). {{ cita.doctor_nombre || 'No asignado' }}</p>
                                </div>
                                <div class="text-right text-sm text-gray-500">
                                    <p>{{ cita.horario_turno_nombre || 'N/A' }}</p>
                                    <p v-if="cita.horario">
                                        {{ cita.horario.hora_inicio }} - {{ cita.horario.hora_fin }}
                                    </p>
                                </div>
                            </div>
                            <div v-if="cita.sintomas" class="mt-2 pt-2 border-t">
                                <p class="text-sm text-gray-600"><strong>Síntomas:</strong> {{ cita.sintomas }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Paginación del historial -->
                <div v-if="historialData && historialData.pages > 1" 
                    class="p-4 border-t bg-gray-50 flex justify-between items-center">
                    <span class="text-sm text-gray-600">
                        Página {{ historialData.current_page }} de {{ historialData.pages }}
                    </span>
                    <div class="flex gap-2">
                        <button @click="historialPage--; fetchHistorial()" 
                            :disabled="historialPage === 1"
                            class="px-3 py-1 border rounded text-sm disabled:opacity-50">
                            Anterior
                        </button>
                        <button @click="historialPage++; fetchHistorial()" 
                            :disabled="historialPage >= historialData.pages"
                            class="px-3 py-1 border rounded text-sm disabled:opacity-50">
                            Siguiente
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

    <!-- MODAL: Editar Paciente -->
    <Teleport to="body">
        <div v-if="showEditModal" 
            class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
                <!-- Header -->
                <div class="bg-blue-600 text-white p-4 flex justify-between items-center">
                    <h3 class="text-lg font-bold">Editar Paciente</h3>
                    <button @click="closeEditModal" class="text-white hover:text-blue-200">
                        <XMarkIcon class="w-6 h-6" />
                    </button>
                </div>

                <!-- Formulario -->
                <form @submit.prevent="guardarPaciente" class="overflow-y-auto max-h-[70vh] p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- DNI (solo lectura) -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">DNI</label>
                            <input type="text" :value="editForm.dni" disabled
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed">
                        </div>

                        <!-- Nombres -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nombres *</label>
                            <input type="text" v-model="editForm.nombres" required
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Apellido Paterno -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Apellido Paterno *</label>
                            <input type="text" v-model="editForm.apellido_paterno" required
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Apellido Materno -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Apellido Materno *</label>
                            <input type="text" v-model="editForm.apellido_materno" required
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Fecha de Nacimiento -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de Nacimiento</label>
                            <input type="date" v-model="editForm.fecha_nacimiento"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Sexo -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
                            <select v-model="editForm.sexo" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="M">Masculino</option>
                                <option value="F">Femenino</option>
                            </select>
                        </div>

                        <!-- Estado Civil -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Estado Civil</label>
                            <select v-model="editForm.estado_civil" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="S">Soltero(a)</option>
                                <option value="C">Casado(a)</option>
                                <option value="V">Viudo(a)</option>
                                <option value="D">Divorciado(a)</option>
                            </select>
                        </div>

                        <!-- Ocupación -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ocupación</label>
                            <input type="text" v-model="editForm.ocupacion"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Teléfono -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                            <input type="tel" v-model="editForm.telefono"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Email -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input type="email" v-model="editForm.email"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Dirección (ancho completo) -->
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                            <input type="text" v-model="editForm.direccion"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>

                        <!-- Seguro -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Seguro</label>
                            <select v-model="editForm.seguro" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                <option value="">Particular</option>
                                <option value="SIS">SIS</option>
                                <option value="ESSALUD">ESSALUD</option>
                            </select>
                        </div>

                        <!-- Número de Seguro -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Número de Seguro</label>
                            <input type="text" v-model="editForm.numero_seguro"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>

                    <!-- Botones -->
                    <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
                        <button type="button" @click="closeEditModal"
                            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                            Cancelar
                        </button>
                        <button type="submit" :disabled="savingEdit"
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                            <span v-if="savingEdit">Guardando...</span>
                            <span v-else>Guardar Cambios</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import pacienteService, { 
    type Paciente, 
    type HistorialCita, 
    type HistorialResponse 
} from "../../services/pacienteService";
import {
    MagnifyingGlassIcon,
    ArrowPathIcon,
    ClockIcon,
    PencilIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    XMarkIcon
} from '@heroicons/vue/24/outline'

// Estado principal
const busquedaPaciente = ref('');
const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalPages = ref(0);
const totalItems = ref(0);
const pacientes = ref<Paciente[]>([]);
const isLoading = ref(false);

// Estado del modal de historial
const showHistorialModal = ref(false);
const loadingHistorial = ref(false);
const historialCitas = ref<HistorialCita[]>([]);
const historialData = ref<HistorialResponse | null>(null);
const historialPage = ref(1);
const historialFiltroEstado = ref('');
const pacienteSeleccionado = ref<Paciente | null>(null);

// Estado del modal de edición
const showEditModal = ref(false);
const savingEdit = ref(false);
const editForm = ref({
    id: 0,
    dni: '',
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    sexo: '',
    estado_civil: '',
    ocupacion: '',
    telefono: '',
    email: '',
    direccion: '',
    seguro: '',
    numero_seguro: ''
});

// Función para cargar pacientes
const fetchPacientes = async () => {
    isLoading.value = true;
    try {
        const params = {
            page: currentPage.value,
            per_page: itemsPerPage.value,
            search: busquedaPaciente.value
        };

        const { data } = await pacienteService.getPacientes(params);

        pacientes.value = data.data;
        totalPages.value = data.pages;
        totalItems.value = data.total;
    } catch (error) {
        console.error("Error al cargar pacientes:", error);
    } finally {
        isLoading.value = false;
    }
};

// === HISTORIAL DE CITAS ===
const verHistorial = async (paciente: Paciente) => {
    pacienteSeleccionado.value = paciente;
    historialPage.value = 1;
    historialFiltroEstado.value = '';
    showHistorialModal.value = true;
    await fetchHistorial();
};

const fetchHistorial = async () => {
    if (!pacienteSeleccionado.value) return;
    
    loadingHistorial.value = true;
    try {
        const params = {
            page: historialPage.value,
            per_page: 10,
            estado: historialFiltroEstado.value || undefined
        };

        const { data } = await pacienteService.getHistorialCitas(
            pacienteSeleccionado.value.id, 
            params
        );

        historialData.value = data;
        historialCitas.value = data.data;
    } catch (error) {
        console.error("Error al cargar historial:", error);
    } finally {
        loadingHistorial.value = false;
    }
};

const closeHistorialModal = () => {
    showHistorialModal.value = false;
    pacienteSeleccionado.value = null;
    historialCitas.value = [];
    historialData.value = null;
};

const getEstadoClass = (estado: string) => {
    const clases: Record<string, string> = {
        'pendiente': 'bg-yellow-100 text-yellow-800',
        'confirmada': 'bg-blue-100 text-blue-800',
        'atendida': 'bg-green-100 text-green-800',
        'cancelada': 'bg-red-100 text-red-800',
        'referido': 'bg-purple-100 text-purple-800'
    };
    return clases[estado] || 'bg-gray-100 text-gray-800';
};

// === EDITAR PACIENTE ===
const editarPaciente = (paciente: Paciente) => {
    editForm.value = {
        id: paciente.id,
        dni: paciente.dni,
        nombres: paciente.nombres,
        apellido_paterno: paciente.apellido_paterno,
        apellido_materno: paciente.apellido_materno,
        fecha_nacimiento: paciente.fecha_nacimiento,
        sexo: paciente.sexo,
        estado_civil: paciente.estado_civil,
        ocupacion: paciente.ocupacion || '',
        telefono: paciente.telefono || '',
        email: paciente.email || '',
        direccion: paciente.direccion,
        seguro: paciente.seguro || '',
        numero_seguro: paciente.numero_seguro || ''
    };
    showEditModal.value = true;
};

const guardarPaciente = async () => {
    savingEdit.value = true;
    try {
        const payload = {
            nombres: editForm.value.nombres,
            apellido_paterno: editForm.value.apellido_paterno,
            apellido_materno: editForm.value.apellido_materno,
            fecha_nacimiento: editForm.value.fecha_nacimiento,
            sexo: editForm.value.sexo,
            estado_civil: editForm.value.estado_civil,
            ocupacion: editForm.value.ocupacion,
            telefono: editForm.value.telefono,
            email: editForm.value.email,
            direccion: editForm.value.direccion,
            seguro: editForm.value.seguro,
            numero_seguro: editForm.value.numero_seguro
        };

        await pacienteService.updatePaciente(editForm.value.id, payload);
        
        // Mostrar notificación de éxito
        alert('Paciente actualizado correctamente');
        
        // Cerrar modal y recargar lista
        closeEditModal();
        await fetchPacientes();
    } catch (error: any) {
        console.error("Error al guardar:", error);
        alert(error.response?.data?.error || 'Error al actualizar paciente');
    } finally {
        savingEdit.value = false;
    }
};

const closeEditModal = () => {
    showEditModal.value = false;
};

// Observadores
watch(busquedaPaciente, () => {
    currentPage.value = 1;
    fetchPacientes();
});

watch(currentPage, () => {
    fetchPacientes();
});

// Cargar al inicio
onMounted(() => {
    fetchPacientes();
});

// Funciones de paginación
const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--;
};
</script>
```

---

## Resumen de Endpoints Implementados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/pacientes/<id>` | Obtener paciente por ID |
| `PUT` | `/api/pacientes/<id>` | Actualizar datos del paciente |
| `GET` | `/api/pacientes/<id>/historial` | Historial de citas del paciente |

---

## Pruebas con cURL

### Obtener paciente por ID:
```bash
curl http://localhost:5000/api/pacientes/1
```

### Actualizar paciente:
```bash
curl -X PUT http://localhost:5000/api/pacientes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "999111222",
    "ocupacion": "Profesor",
    "email": "nuevo@email.com"
  }'
```

### Obtener historial de citas:
```bash
curl "http://localhost:5000/api/pacientes/1/historial?page=1&per_page=10&estado=atendida"
```
