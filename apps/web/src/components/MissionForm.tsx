'use client'

import { useState } from 'react'
import { useRobot } from '@/context/RobotContext'
import { MAP_POINTS, type MapPoint } from '@/types'
import { Plus, MapPin, Package, ArrowRight, MousePointerClick } from 'lucide-react'

interface MissionFormProps {
  selectedOrigin: MapPoint | null
  selectedDestination: MapPoint | null
  onSetOrigin: (p: MapPoint | null) => void
  onSetDestination: (p: MapPoint | null) => void
}

export default function MissionForm({ selectedOrigin, selectedDestination, onSetOrigin, onSetDestination }: MissionFormProps) {
  const { createMission, state } = useRobot()
  const [objectDesc, setObjectDesc] = useState('')

  const pickupPoints = MAP_POINTS.filter(p => p.type === 'pickup')
  const dropoffPoints = MAP_POINTS.filter(p => p.type === 'dropoff')

  const canSubmit = selectedOrigin && selectedDestination && objectDesc.trim() && !state.robot.isEmergencyStopped

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return
    createMission(selectedOrigin!, selectedDestination!, objectDesc.trim())
    setObjectDesc('')
    onSetOrigin(null)
    onSetDestination(null)
  }

  return (
    <div className="glass-panel h-full flex flex-col">
      <div className="panel-header">
        <Plus className="w-4 h-4 text-primary" />
        Nouvelle Mission
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1">
        {/* Origin */}
        <div className="space-y-2">
          <label className="text-[10px] uppercase tracking-wider text-text-secondary font-bold flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></span>
            Point de départ
          </label>
          <div className="relative group">
            <select
              className="w-full bg-surface-highlight border border-border rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all appearance-none cursor-pointer hover:bg-white/5"
              value={selectedOrigin?.id ?? ''}
              onChange={e => onSetOrigin(MAP_POINTS.find(p => p.id === e.target.value) ?? null)}
            >
              <option value="">-- Sélectionner sur la carte ou ici --</option>
              {pickupPoints.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <MapPin className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary pointer-events-none group-hover:text-primary transition-colors" />
          </div>
        </div>

        {/* Arrow Divider */}
        <div className="flex justify-center -my-2">
          <div className="w-8 h-8 rounded-full bg-surface border border-border flex items-center justify-center shadow-lg z-10">
            <ArrowRight className="w-4 h-4 text-text-tertiary" />
          </div>
        </div>

        {/* Destination */}
        <div className="space-y-2">
          <label className="text-[10px] uppercase tracking-wider text-text-secondary font-bold flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-500 shadow-[0_0_8px_rgba(139,92,246,0.8)]"></span>
            Destination
          </label>
          <div className="relative group">
            <select
              className="w-full bg-surface-highlight border border-border rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all appearance-none cursor-pointer hover:bg-white/5"
              value={selectedDestination?.id ?? ''}
              onChange={e => onSetDestination(MAP_POINTS.find(p => p.id === e.target.value) ?? null)}
            >
              <option value="">-- Sélectionner sur la carte ou ici --</option>
              {dropoffPoints.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <MapPin className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary pointer-events-none group-hover:text-primary transition-colors" />
          </div>
        </div>

        {/* Object description */}
        <div className="space-y-2">
          <label className="text-[10px] uppercase tracking-wider text-text-secondary font-bold">Objet à transporter</label>
          <div className="relative group">
            <input
              type="text"
              className="w-full bg-surface-highlight border border-border rounded-xl px-4 py-3 text-sm text-white placeholder:text-text-tertiary focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
              placeholder="ex: Dossier confidentiel, Colis #404..."
              value={objectDesc}
              onChange={e => setObjectDesc(e.target.value)}
            />
            <Package className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary pointer-events-none group-focus-within:text-primary transition-colors" />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!canSubmit}
          className={`w-full py-4 rounded-xl font-bold text-sm tracking-wide transition-all duration-300 shadow-lg flex items-center justify-center gap-2 ${
            canSubmit
              ? 'bg-primary hover:bg-blue-600 text-white shadow-glow hover:scale-[1.02] active:scale-[0.98]'
              : 'bg-surface-highlight text-text-tertiary cursor-not-allowed border border-border'
          }`}
        >
          <MousePointerClick className="w-4 h-4" />
          LANCER LA MISSION
        </button>

        {state.robot.isEmergencyStopped && (
          <p className="text-center text-xs text-danger font-medium animate-pulse">
            ⚠️ Robot en arrêt d&apos;urgence
          </p>
        )}
      </form>
    </div>
  )
}
