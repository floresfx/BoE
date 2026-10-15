import type { FieldConfig } from './AdminCrudModal'

// ---------------------------------------------------------------------------
// Configuraciones de campos por entidad
// ---------------------------------------------------------------------------

export const PLANS_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'mpr_base', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'price', label: 'Precio', type: 'number', required: true, step: 0.01, min: 0 },
  { name: 'currency_id', label: 'Moneda (ID)', type: 'text', required: true, helpText: 'UUID de la moneda (ej: USD)' },
  { name: 'interval', label: 'Intervalo', type: 'select', required: true, options: [
    { value: 'monthly', label: 'Mensual' },
    { value: 'quarterly', label: 'Trimestral' },
    { value: 'yearly', label: 'Anual' },
  ]},
  { name: 'trial_days', label: 'Días de trial', type: 'number', required: true, min: 0, max: 90 },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const FEATURES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'nuevo_modulo', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'description', label: 'Descripción', type: 'textarea', required: true },
  { name: 'applies_to', label: 'Aplica a', type: 'select', required: true, options: [
    { value: 'mpr', label: 'MPR' },
    { value: 'marketplace', label: 'Marketplace' },
    { value: 'both', label: 'Ambos' },
  ]},
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const VERTICALS_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'nuevo_vertical', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'description', label: 'Descripción', type: 'textarea', required: true },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const ATTRIBUTES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'nuevo_atributo', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'type_code', label: 'Tipo', type: 'select', required: true, options: [
    { value: 'boolean', label: 'Booleano' },
    { value: 'numeric', label: 'Numérico' },
    { value: 'text', label: 'Texto' },
    { value: 'list', label: 'Lista' },
  ]},
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const TAXES_FIELDS: FieldConfig[] = [
  { name: 'country_code', label: 'País (código)', type: 'text', required: true, placeholder: 'VE', editableInEdit: false },
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'IVA', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'rate', label: 'Tasa (%)', type: 'number', required: true, step: 0.01, min: 0, max: 100 },
  { name: 'applies_to', label: 'Aplica a', type: 'text', required: true, placeholder: 'general' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const SERVICES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'nuevo_servicio', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'description', label: 'Descripción', type: 'textarea', required: true },
  { name: 'category_id', label: 'Categoría (ID)', type: 'text', helpText: 'UUID de categoría (opcional)' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const CURRENCIES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código ISO', type: 'text', required: true, placeholder: 'USD', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'symbol', label: 'Símbolo', type: 'text', required: true, placeholder: '$' },
  { name: 'decimals', label: 'Decimales', type: 'number', required: true, min: 0, max: 8 },
  { name: 'is_base', label: 'Es moneda base', type: 'checkbox' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const UNITS_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, placeholder: 'kg', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'symbol', label: 'Símbolo', type: 'text', required: true },
  { name: 'category_id', label: 'Categoría (ID)', type: 'text', required: true, helpText: 'UUID de unit_category' },
  { name: 'is_base', label: 'Es unidad base', type: 'checkbox' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const CATEGORIES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const COUNTRIES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código ISO', type: 'text', required: true, placeholder: 'VE', editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'timezone_id', label: 'Zona horaria (ID)', type: 'text', required: true },
  { name: 'currency_id', label: 'Moneda (ID)', type: 'text', required: true },
  { name: 'phone_prefix', label: 'Prefijo teléfono', type: 'text', required: true, placeholder: '+58' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]

export const DOCUMENT_TYPES_FIELDS: FieldConfig[] = [
  { name: 'code', label: 'Código', type: 'text', required: true, editableInEdit: false },
  { name: 'name', label: 'Nombre', type: 'text', required: true },
  { name: 'country_id', label: 'País (ID)', type: 'text', helpText: 'UUID (opcional para tipos globales)' },
  { name: 'format', label: 'Formato', type: 'text', placeholder: 'V-12345678' },
  { name: 'regex', label: 'Regex', type: 'text', placeholder: '^[VE]-\\d{7,8}$' },
  { name: 'is_active', label: 'Activo', type: 'checkbox' },
]