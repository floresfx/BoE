import { api } from '../lib/api'

export function useDownloadReport() {
  const downloadFile = async (endpoint: string, filename: string) => {
    try {
      // Usamos api (que ya tiene el interceptor del token)
      const response = await api.get(endpoint, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error al descargar el reporte:', error)
      alert('Error al descargar el reporte.')
    }
  }

  const downloadExcel = () => downloadFile('/reports/stock/excel', 'stock_consolidado.xlsx')
  const downloadPdf = () => downloadFile('/reports/stock/pdf', 'stock_consolidado.pdf')

  return { downloadExcel, downloadPdf }
}