import { useTenantSettings } from './useSettings';
import { api } from '../lib/api';
import { useQuery } from '@tanstack/react-query';

interface CatalogItem {
  id: string;
  code: string;
  name: string;
  symbol?: string;
}

// Hook base para traer un catálogo completo (reutilizable)
const useGlobalCatalog = (endpoint: string) => {
  return useQuery({
    queryKey: ['catalogs', endpoint],
    queryFn: async () => (await api.get<CatalogItem[]>(`/catalogs/${endpoint}`)).data,
  });
};

export const useFilteredCatalogs = () => {
  // 1. Traemos la configuración del tenant (qué tiene activo)
  const { data: settings } = useTenantSettings();

  // 2. Traemos los catálogos globales
  const { data: allUnits, isLoading: loadingUnits } = useGlobalCatalog('units');
  const { data: allCategories, isLoading: loadingCategories } = useGlobalCatalog('categories');
  const { data: allAttributes, isLoading: loadingAttributes } = useGlobalCatalog('attributes');

  // 3. Filtramos los catálogos según lo que el tenant ha activado
  // Si el tenant no ha configurado nada (active_ids vacío), mostramos todo como fallback (opcional).
  const activeUnitIds = settings?.active_unit_ids || [];
  const activeCategoryIds = settings?.active_category_ids || [];
  const activeAttributeIds = settings?.active_attribute_ids || [];

  const filteredUnits = allUnits?.filter(u => 
    activeUnitIds.length === 0 ? true : activeUnitIds.includes(u.id)
  ) || [];

  const filteredCategories = allCategories?.filter(c => 
    activeCategoryIds.length === 0 ? true : activeCategoryIds.includes(c.id)
  ) || [];

  const filteredAttributes = allAttributes?.filter(a => 
    activeAttributeIds.length === 0 ? true : activeAttributeIds.includes(a.id)
  ) || [];

  const isLoading = loadingUnits || loadingCategories || loadingAttributes;

  return {
    units: filteredUnits,
    categories: filteredCategories,
    attributes: filteredAttributes,
    isLoading
  };
};