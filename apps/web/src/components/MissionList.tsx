'use client'

import { useRobot } from '@/context/RobotContext'
import { MISSION_STATUS_CONFIG } from '@/types'
import {
  Play,
  X,
  ListChecks,
  ArrowRight,
  Clock,
  Inbox
} from 'lucide-react'

export default function MissionList() {
  const { state, cancelMission, simulateMission } = useRobot()

  const activeMissions = state.missions.filter(m =>
    !['COMPLETED', 'CANCELLED', 'FAILED', 'EMERGENCY_STOPPED'].includes(m.status)
  )
  const completedMissions = state.missions.filter(m =>
    ['COMPLETED', 'CANCELLED', 'FAILED', 'EMERGENCY_STOPPED'].includes(m.status)
  )

  return (
    <div className="glass-panel h-full flex flex-col min-h-0">
      <div className="panel-header justify-between">
        <span className="flex items-center gap-2">
          <ListChecks className="w-4 h-4 text-primary" />
          Liste des Missions
        </span>
        <span className="badge bg-surface-highlight text-text-secondary border-border">
          {state.missions.length} Total
        </span>
      </div>

      <div className="p-4 flex-1 overflow-y-auto space-y-6 custom-scrollbar">
        {state.missions.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-50">
            <div className="w-16 h-16 rounded-full bg-surface-highlight flex items-center justify-center mb-4">
              <Inbox className="w-8 h-8 text-text-tertiary" />
            </div>
            <p className="text-sm font-medium text-text-secondary">Aucune mission</p>
            <p className="text-xs text-text-tertiary mt-1">Le journal d&apos;activité est vide</p>
          </div>
        ) : (
          <>
            {/* Active missions */}
            {activeMissions.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-[10px] font-bold text-text-tertiary uppercase tracking-widest pl-2">En cours ({activeMissions.length})</h3>
                <div className="space-y-3">
                  {activeMissions.map(mission => {
                    const cfg = MISSION_STATUS_CONFIG[mission.status]
                    return (
                      <div
                        key={mission.id}
                        className="bg-surface/50 border border-border hover:border-primary/30 rounded-xl p-4 transition-all duration-300 group"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className={`badge ${cfg.bgColor} ${cfg.color} border-transparent bg-opacity-10`}>
                            {cfg.icon} <span className="ml-1">{cfg.label}</span>
                          </div>
                          <span className="text-[10px] text-text-tertiary font-mono tracking-wider">#{mission.id.slice(0, 8)}</span>
                        </div>

                        <div className="flex items-center gap-3 text-xs text-text-secondary mb-3 bg-black/20 p-2 rounded-lg">
                          <span className="font-medium text-white">{mission.origin.name}</span>
                          <ArrowRight className="w-3 h-3 text-text-tertiary" />
                          <span className="font-medium text-white">{mission.destination.name}</span>
                        </div>

                        <p className="text-xs text-text-secondary mb-4 flex items-center gap-2">
                          <span className="w-1 h-1 rounded-full bg-text-tertiary"></span>
                          {mission.objectDescription}
                        </p>

                        {/* Progress bar */}
                        {mission.progress !== undefined && mission.progress > 0 && (
                          <div className="w-full h-1 bg-surface-highlight rounded-full overflow-hidden mb-4">
                            <div
                              className="h-full bg-primary rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                              style={{ width: `${mission.progress}%` }}
                            />
                          </div>
                        )}

                        <div className="flex gap-2 mt-2">
                          {mission.status === 'CREATED' && (
                            <button
                              onClick={() => simulateMission(mission.id)}
                              className="flex-1 btn bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 text-xs py-2"
                              disabled={state.robot.isEmergencyStopped || state.isSimulating}
                            >
                              <Play className="w-3 h-3" />
                              Lancer
                            </button>
                          )}
                          {(mission.status === 'CREATED' || mission.status === 'ASSIGNED') && (
                            <button
                              onClick={() => cancelMission(mission.id)}
                              className="flex-1 btn bg-surface hover:bg-surface-highlight text-text-secondary border border-border text-xs py-2"
                            >
                              <X className="w-3 h-3" />
                              Annuler
                            </button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Completed/History */}
            {completedMissions.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-[10px] font-bold text-text-tertiary uppercase tracking-widest pl-2">Historique ({completedMissions.length})</h3>
                <div className="space-y-2 opacity-60 hover:opacity-100 transition-opacity">
                  {completedMissions.slice(0, 5).map(mission => {
                    const cfg = MISSION_STATUS_CONFIG[mission.status]
                    return (
                      <div
                        key={mission.id}
                        className="bg-surface/30 border border-border/50 rounded-lg p-3 flex items-center justify-between"
                      >
                         <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${mission.status === 'COMPLETED' ? 'bg-success shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-danger'}`} />
                            <div className="flex flex-col">
                              <span className="text-xs font-medium text-text-secondary">{mission.objectDescription}</span>
                              <span className="text-[10px] text-text-tertiary">{mission.destination.name}</span>
                            </div>
                         </div>
                         <span className={`text-[10px] px-2 py-0.5 rounded-full ${mission.status === 'COMPLETED' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                           {mission.status === 'COMPLETED' ? 'Terminé' : 'Échoué'}
                         </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
