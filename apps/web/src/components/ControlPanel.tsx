'use client'

import { useRobot } from '@/context/RobotContext'
import {
  OctagonX,
  ShieldCheck,
  Hand,
  HandMetal,
  Pause,
  RotateCcw,
  Zap,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Gamepad2
} from 'lucide-react'

export default function ControlPanel() {
  const { state, emergencyStop, releaseEmergency, toggleGripper, addNotification } = useRobot()

  const handleManualMove = (direction: string) => {
    addNotification('info', 'Commande manuelle', `Déplacement : ${direction}`)
  }

  return (
    <div className="glass-panel h-full flex flex-col">
      <div className="panel-header">
        <Gamepad2 className="w-4 h-4 text-primary" />
        Centre de Contrôle
      </div>

      <div className="p-4 space-y-4 flex-1 overflow-y-auto">
        {/* Emergency Stop - Minimalist Toggle */}
        <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-border">
          <div className="flex items-center gap-3">
             <div className={`w-8 h-8 rounded-full flex items-center justify-center ${state.robot.isEmergencyStopped ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'}`}>
                {state.robot.isEmergencyStopped ? <ShieldCheck className="w-4 h-4" /> : <OctagonX className="w-4 h-4" />}
             </div>
             <div className="flex flex-col">
               <span className="text-xs font-bold text-white tracking-wide">ARRÊT URGENCE</span>
               <span className="text-[10px] text-text-secondary">{state.robot.isEmergencyStopped ? 'Système sécurisé' : 'Système actif'}</span>
             </div>
          </div>
          
          <button
            onClick={state.robot.isEmergencyStopped ? releaseEmergency : emergencyStop}
            className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${state.robot.isEmergencyStopped ? 'bg-success/20' : 'bg-danger/20'}`}
          >
            <div className={`absolute top-1 left-1 w-4 h-4 rounded-full transition-transform duration-300 ${state.robot.isEmergencyStopped ? 'translate-x-6 bg-success shadow-glow-success' : 'translate-x-0 bg-danger shadow-glow-danger'}`} />
          </button>
        </div>

        {/* Manual Movement - Compact D-Pad */}
        <div className="bg-transparent pt-2">
          <div className="grid grid-cols-3 gap-1 max-w-[120px] mx-auto">
            <div />
            <button
              onClick={() => handleManualMove('Avant')}
              className="aspect-square rounded-lg bg-surface-highlight border border-border hover:bg-primary/20 hover:text-white transition-all active:scale-95 flex items-center justify-center group"
              disabled={state.robot.isEmergencyStopped}
            >
              <ChevronUp className="w-5 h-5 text-text-secondary group-hover:text-primary" />
            </button>
            <div />

            <button
              onClick={() => handleManualMove('Gauche')}
              className="aspect-square rounded-lg bg-surface-highlight border border-border hover:bg-primary/20 hover:text-white transition-all active:scale-95 flex items-center justify-center group"
              disabled={state.robot.isEmergencyStopped}
            >
              <ChevronLeft className="w-5 h-5 text-text-secondary group-hover:text-primary" />
            </button>
            <button
              onClick={() => handleManualMove('Stop')}
              className="aspect-square rounded-lg bg-surface-highlight border border-border hover:bg-danger/20 transition-all active:scale-95 flex items-center justify-center group"
              disabled={state.robot.isEmergencyStopped}
            >
              <div className="w-2 h-2 bg-danger rounded-sm shadow-glow-danger" />
            </button>
            <button
              onClick={() => handleManualMove('Droite')}
              className="aspect-square rounded-lg bg-surface-highlight border border-border hover:bg-primary/20 hover:text-white transition-all active:scale-95 flex items-center justify-center group"
              disabled={state.robot.isEmergencyStopped}
            >
              <ChevronRight className="w-5 h-5 text-text-secondary group-hover:text-primary" />
            </button>

            <div />
            <button
              onClick={() => handleManualMove('Arrière')}
              className="aspect-square rounded-lg bg-surface-highlight border border-border hover:bg-primary/20 hover:text-white transition-all active:scale-95 flex items-center justify-center group"

              disabled={state.robot.isEmergencyStopped}
              aria-label="Reculer"
            >
              <ChevronDown className="w-8 h-8 text-text-secondary group-hover:text-primary transition-colors" />
            </button>
            <div />
          </div>
        </div>

        {/* Tools & Actions */}
        <div className="space-y-3">
           {/* Gripper Control */}
          <button
            onClick={toggleGripper}
            className={`w-full py-4 rounded-xl font-medium flex items-center justify-center gap-3 transition-all border ${
              state.robot.gripperOpen
                ? 'bg-warning/10 border-warning/30 text-warning hover:bg-warning/20'
                : 'bg-primary/10 border-primary/30 text-primary hover:bg-primary/20'
            }`}
          >
            {state.robot.gripperOpen ? (
              <>
                <Hand className="w-5 h-5" />
                <span className="uppercase tracking-wide text-xs font-bold">Pince Ouverte</span>
              </>
            ) : (
              <>
                <HandMetal className="w-5 h-5" />
                <span className="uppercase tracking-wide text-xs font-bold">Pince Fermée</span>
              </>
            )}
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => addNotification('info', 'Retour base', 'Commande de retour à la base envoyée')}
              className="btn btn-ghost text-xs"
              disabled={state.robot.isEmergencyStopped}
            >
              <RotateCcw className="w-4 h-4" />
              Retour Base
            </button>
            <button
              onClick={() => addNotification('info', 'Recharge', 'Commande de recharge envoyée')}
              className="btn btn-ghost text-xs"
              disabled={state.robot.isEmergencyStopped}
            >
              <Zap className="w-4 h-4" />
              Recharger
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
