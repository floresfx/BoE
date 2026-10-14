// Unidades de medida
export interface UnitCategory {
  id: string
  code: string
  name: string
}

export interface Unit {
  id: string
  code: string
  name: string
  symbol: string
  category_id: string
  is_base: boolean
}

// Categorías y subcategorías
export interface Category {
  id: string
  code: string
  name: string
}

export interface Subcategory {
  id: string
  category_id: string
  code: string
  name: string
}

// Atributos
export interface AttributeType {
  id: string
  code: string
  name: string
}

export interface Attribute {
  id: string
  code: string
  name: string
  type_id: string
}

// Impuestos
export interface Tax {
  id: string
  country_id: string
  code: string
  name: string
  rate: string
  applies_to: string
}