'use client'

import { useRobot } from '@/context/RobotContext'
import { useState, useEffect } from 'react'
import {
  Battery,
  Gauge,
  Compass,
  Clock,
  Wifi,
  WifiOff,
  MapPin,
  Activity,
  Zap
} from 'lucide-react'

export default function RobotStatus() {
  const { state } = useRobot()
  const { robot } = state
  const [timeString, setTimeString] = useState<string>('')

  useEffect(() => {
    const updateTime = () => {
      if (!robot.lastHeartbeat) return
      const diff = Date.now() - new Date(robot.lastHeartbeat).getTime()
      if (diff < 1000) setTimeString('maintenant')
      else if (diff < 60000) setTimeString(`il y a ${Math.floor(diff / 1000)}s`)
      else setTimeString(`il y a ${Math.floor(diff / 60000)}min`)
    }

    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [robot.lastHeartbeat])

  return (
    <div className="glass-panel h-full flex flex-col">
      <div className="panel-header">
        <Activity className="w-4 h-4 text-primary" />
        État du Système
      </div>

      <div className="p-6 space-y-6 flex-1 overflow-y-auto">
        {/* Connection */}
        <div className="flex items-center justify-between group">
          <div className="flex items-center gap-3 text-sm text-text-secondary group-hover:text-white transition-colors">
            <div className={`p-2 rounded-lg ${robot.connectionStatus === 'connected' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
              {robot.connectionStatus === 'connected' ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
            </div>
            Connexion
          </div>
          <span className={`badge ${
            robot.connectionStatus === 'connected' ? 'badge-success' : 'badge-danger'
          }`}>
            {robot.connectionStatus === 'connected' ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        {/* Battery */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3 text-text-secondary">
              <div className={`p-2 rounded-lg ${robot.batteryLevel < 20 ? 'bg-danger/10 text-danger' : 'bg-white/5 text-white'}`}>
                <Battery className="w-4 h-4" />
              </div>
              Batterie
            </div>
            <span className={`font-mono font-bold ${robot.batteryLevel < 20 ? 'text-danger' : 'text-white'}`}>
              {Math.round(robot.batteryLevel)}%
            </span>
          </div>
          <div className="h-2 bg-surface-highlight rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                robot.batteryLevel < 20 ? 'bg-danger shadow-glow-danger' :
                robot.batteryLevel < 50 ? 'bg-warning' : 'bg-success shadow-glow-success'
              }`}
              style={{ width: `${robot.batteryLevel}%` }}
            />
          </div>
        </div>

        {/* Grid Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white/5 rounded-2xl p-3 border border-transparent hover:border-border transition-all">
            <div className="flex items-center gap-2 text-xs text-text-secondary mb-1">
              <Gauge className="w-3.5 h-3.5" /> Vitesse
            </div>
            <div className="text-xl font-mono font-bold text-white tracking-tight">
              {robot.speed.toFixed(2)} <span className="text-xs text-text-tertiary font-sans font-normal">m/s</span>
            </div>
          </div>
          
          <div className="bg-white/5 rounded-2xl p-3 border border-transparent hover:border-border transition-all">
            <div className="flex items-center gap-2 text-xs text-text-secondary mb-1">
              <Compass className="w-3.5 h-3.5" /> Cap
            </div>
            <div className="text-xl font-mono font-bold text-white tracking-tight">
              {Math.round(robot.position.heading)}°
            </div>
          </div>
        </div>

        {/* Position */}
        <div className="bg-white/5 rounded-2xl p-4 border border-transparent hover:border-border transition-all group">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs text-text-secondary group-hover:text-white transition-colors">
              <MapPin className="w-3.5 h-3.5" /> Position GPS
            </div>
            <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-glow animate-pulse" />
          </div>
          <div className="flex justify-between items-end font-mono">
            <div>
              <div className="text-[10px] text-text-tertiary uppercase tracking-wider">Latitude</div>
              <div className="text-sm font-medium text-white">{robot.position.x.toFixed(4)}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-text-tertiary uppercase tracking-wider">Longitude</div>
              <div className="text-sm font-medium text-white">{robot.position.y.toFixed(4)}</div>
            </div>
          </div>
        </div>

        {/* Heartbeat */}
        <div className="flex items-center justify-between py-2 border-t border-border mt-2">
          <div className="flex items-center gap-2 text-xs text-text-tertiary">
            <Clock className="w-3.5 h-3.5" />
            Dernier signal
          </div>
          <span className="text-xs font-mono text-text-secondary">{timeString}</span>
        </div>
      </div>
    </div>
  )
}
