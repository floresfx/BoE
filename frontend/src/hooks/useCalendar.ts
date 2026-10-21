import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export interface CalendarEvent {
  id: string
  title: string
  start: string
  end: string | null
  type: 'production_order' | 'purchase_request'
  status: string
  color: string
}

export interface CalendarResponse {
  events: CalendarEvent[]
}

export function useCalendarEvents(from: Date, to: Date) {
  return useQuery({
    queryKey: ['calendar', from.toISOString(), to.toISOString()],
    queryFn: async () => {
      const { data } = await api.get<CalendarResponse>('/calendar', {
        params: {
          from: from.toISOString(),
          to: to.toISOString(),
        },
      })
      return data
    },
  })
}