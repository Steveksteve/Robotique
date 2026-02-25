'use client'

import { useRobot } from '@/context/RobotContext'
import { Activity, CheckCircle, AlertTriangle, Clock } from 'lucide-react'

export default function StatsCards() {
  const { state } = useRobot()

  const totalMissions = state.missions.length
  const activeMissions = state.missions.filter(m =>
    !['COMPLETED', 'CANCELLED', 'FAILED', 'EMERGENCY_STOPPED'].includes(m.status)
  ).length
  const completedMissions = state.missions.filter(m => m.status === 'COMPLETED').length
  const failedMissions = state.missions.filter(m =>
    ['FAILED', 'EMERGENCY_STOPPED', 'CANCELLED'].includes(m.status)
  ).length

  const stats = [
    {
      label: 'Total missions',
      value: totalMissions,
      icon: Activity,
      color: 'text-primary',
      bg: 'bg-primary/10',
      border: 'border-primary/20',
      shadow: 'shadow-glow',
    },
    {
      label: 'En cours',
      value: activeMissions,
      icon: Clock,
      color: 'text-warning',
      bg: 'bg-warning/10',
      border: 'border-warning/20',
      shadow: 'shadow-glow',
    },
    {
      label: 'Terminées',
      value: completedMissions,
      icon: CheckCircle,
      color: 'text-success',
      bg: 'bg-success/10',
      border: 'border-success/20',
      shadow: 'shadow-glow-success',
    },
    {
      label: 'Échouées',
      value: failedMissions,
      icon: AlertTriangle,
      color: 'text-danger',
      bg: 'bg-danger/10',
      border: 'border-danger/20',
      shadow: 'shadow-glow-danger',
    },
  ]

  return (
    <div className="flex flex-wrap lg:flex-nowrap gap-4">
      {stats.map(s => (
        <div key={s.label} className={`glass-panel px-6 py-3 flex items-center gap-4 group hover:bg-surface-highlight transition-all duration-300 min-w-[200px] flex-1`}>
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${s.bg} ${s.color} bg-opacity-50`}>
            <s.icon className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-text-secondary font-medium leading-none mb-1">{s.label}</p>
            <p className="text-xl font-bold text-text-primary tracking-tight leading-none">{s.value}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
