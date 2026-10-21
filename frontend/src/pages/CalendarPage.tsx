import { useState } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { es } from 'date-fns/locale'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import { useCalendarEvents } from '../hooks/useCalendar'

const locales = { 'es': es }

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
})

export function CalendarPage() {
  const [view, setView] = useState<'month' | 'week' | 'day'>('month')
  const [date, setDate] = useState(new Date())

  const from = new Date(date.getFullYear(), date.getMonth(), 1)
  const to = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59)

  const { data, isLoading } = useCalendarEvents(from, to)

  const events = (data?.events || []).map((e) => ({
    title: e.title,
    start: new Date(e.start),
    end: e.end ? new Date(e.end) : new Date(e.start),
    allDay: true,
    resource: e,
  }))

  if (isLoading) return <div className="p-8 text-center">Cargando calendario...</div>

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Calendario</h1>
        <p className="text-sm text-slate-500 mt-1">Órdenes de producción y entregas de compras.</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow h-full">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          view={view}
          onView={(v) => setView(v as any)}
          date={date}
          onNavigate={(newDate) => setDate(newDate)}
          culture="es"
          messages={{
            next: 'Sig',
            previous: 'Ant',
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
          }}
          eventPropGetter={(event: any) => ({
            style: {
              backgroundColor: event.resource.color,
              borderColor: event.resource.color,
              color: 'white',
            },
          })}
        />
      </div>
    </div>
  )
}
