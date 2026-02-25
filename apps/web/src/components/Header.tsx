'use client'

import { useRobot } from '@/context/RobotContext'
import { Bell, Bot, Wifi, WifiOff, BatteryWarning } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const { state } = useRobot()
  const [showNotifs, setShowNotifs] = useState(false)
  const unreadCount = state.notifications.filter(n => !n.read).length

  return (
    <header className="fixed top-4 left-4 right-4 z-50 glass-panel px-6 py-3 flex items-center justify-between shadow-glass">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary shadow-glow">
          <Bot className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-widest text-white uppercase">RAA Dashboard</h1>
          <p className="text-[10px] font-medium text-text-secondary tracking-wider">Robot d&apos;Assistance Autonome</p>
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Connection status */}
        <div className="flex items-center gap-2">
          {state.robot.connectionStatus === 'connected' ? (
            <div className="w-2 h-2 rounded-full bg-success shadow-glow-success animate-pulse" />
          ) : (
            <div className="w-2 h-2 rounded-full bg-danger shadow-glow-danger" />
          )}
          <span className={`text-xs font-medium tracking-wide ${state.robot.connectionStatus === 'connected' ? 'text-success' : 'text-danger'}`}>
            {state.robot.connectionStatus === 'connected' ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        <div className="h-4 w-[1px] bg-border" />

        {/* Battery */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end">
            <span className={`text-xs font-bold font-mono ${state.robot.batteryLevel < 20 ? 'text-danger' : 'text-white'}`}>
              {Math.round(state.robot.batteryLevel)}%
            </span>
          </div>
          <div className={`w-10 h-1.5 rounded-full bg-surface-highlight overflow-hidden relative`}>
             <div
              className={`h-full rounded-full transition-all duration-500 ${
                state.robot.batteryLevel < 20
                  ? 'bg-danger shadow-glow-danger'
                  : state.robot.batteryLevel < 50
                  ? 'bg-warning'
                  : 'bg-success shadow-glow-success'
              }`}
              style={{ width: `${state.robot.batteryLevel}%` }}
            />
          </div>
        </div>

        {/* Emergency indicator */}
        {state.robot.isEmergencyStopped && (
          <div className="badge badge-danger animate-pulse">
            <span className="w-1.5 h-1.5 bg-danger rounded-full" />
            ARRÊT URGENCE
          </div>
        )}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="relative p-2 rounded-xl hover:bg-white/5 transition-colors group"
            aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} non lues)` : ''}`}
          >
            <Bell className="w-5 h-5 text-text-secondary group-hover:text-white transition-colors" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full shadow-glow" />
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 top-full mt-4 w-80 max-h-96 overflow-y-auto glass-panel shadow-2xl z-50 p-2">
              <div className="px-4 py-3 border-b border-border flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-wider">Notifications</span>
                <span className="badge bg-white/5 text-text-secondary border-transparent">{state.notifications.length}</span>
              </div>
              {state.notifications.length === 0 ? (
                <div className="p-8 text-xs text-text-tertiary text-center uppercase tracking-wider">Aucune notification</div>
              ) : (
                <div className="space-y-1">
                {state.notifications.slice(0, 15).map(n => (
                  <div
                    key={n.id}
                    className={`p-3 rounded-xl border border-transparent transition-colors ${!n.read ? 'bg-white/5 border-border' : 'hover:bg-white/5'}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className={`mt-1 w-1.5 h-1.5 rounded-full shrink-0 ${
                        n.type === 'error' ? 'bg-danger shadow-glow-danger' :
                        n.type === 'warning' ? 'bg-warning' :
                        n.type === 'success' ? 'bg-success shadow-glow-success' : 'bg-primary shadow-glow'
                      }`} />
                      <div>
                        <p className="text-xs font-medium text-white mb-0.5">{n.title}</p>
                        <p className="text-[10px] text-text-secondary leading-relaxed">{n.message}</p>
                        <p className="text-[10px] text-text-tertiary mt-1.5 font-mono">{new Date(n.timestamp).toLocaleTimeString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
