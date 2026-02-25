'use client'

import React, { createContext, useContext, useReducer, useCallback, useRef, useEffect } from 'react'
import type { Mission, MissionStatus, RobotState, RobotPosition, Notification, MapPoint } from '@/types'

interface AppState {
  robot: RobotState
  missions: Mission[]
  notifications: Notification[]
  selectedMissionId: string | null
  isSimulating: boolean
}

type Action =
  | { type: 'SET_ROBOT_STATE'; payload: Partial<RobotState> }
  | { type: 'SET_ROBOT_POSITION'; payload: RobotPosition }
  | { type: 'ADD_MISSION'; payload: Mission }
  | { type: 'UPDATE_MISSION'; payload: { id: string; status: MissionStatus; progress?: number; estimatedDuration?: number } }
  | { type: 'SELECT_MISSION'; payload: string | null }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'CLEAR_NOTIFICATIONS' }
  | { type: 'EMERGENCY_STOP' }
  | { type: 'RELEASE_EMERGENCY' }
  | { type: 'TOGGLE_GRIPPER' }
  | { type: 'SET_SIMULATING'; payload: boolean }

const initialState: AppState = {
  robot: {
    batteryLevel: 87,
    position: { x: 120, y: 280, heading: 0 },
    speed: 0,
    connectionStatus: 'connected',
    lastHeartbeat: new Date().toISOString(),
    isEmergencyStopped: false,
    gripperOpen: true,
    currentMissionId: null,
  },
  missions: [],
  notifications: [],
  selectedMissionId: null,
  isSimulating: false,
}

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_ROBOT_STATE':
      return { ...state, robot: { ...state.robot, ...action.payload } }
    case 'SET_ROBOT_POSITION':
      return { ...state, robot: { ...state.robot, position: action.payload } }
    case 'ADD_MISSION':
      return { ...state, missions: [action.payload, ...state.missions] }
    case 'UPDATE_MISSION':
      return {
        ...state,
        missions: state.missions.map(m =>
          m.id === action.payload.id
            ? { ...m, ...action.payload, updatedAt: new Date().toISOString() }
            : m
        ),
      }
    case 'SELECT_MISSION':
      return { ...state, selectedMissionId: action.payload }
    case 'ADD_NOTIFICATION':
      return { ...state, notifications: [action.payload, ...state.notifications].slice(0, 50) }
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(n =>
          n.id === action.payload ? { ...n, read: true } : n
        ),
      }
    case 'CLEAR_NOTIFICATIONS':
      return { ...state, notifications: [] }
    case 'EMERGENCY_STOP':
      return {
        ...state,
        robot: { ...state.robot, isEmergencyStopped: true, speed: 0 },
        missions: state.missions.map(m =>
          ['CREATED', 'ASSIGNED', 'NAVIGATING_TO_PICKUP', 'PICKING_UP', 'NAVIGATING_TO_DROP', 'DROPPING_OFF'].includes(m.status)
            ? { ...m, status: 'EMERGENCY_STOPPED', updatedAt: new Date().toISOString() }
            : m
        ),
        isSimulating: false,
      }
    case 'RELEASE_EMERGENCY':
      return { ...state, robot: { ...state.robot, isEmergencyStopped: false } }
    case 'TOGGLE_GRIPPER':
      return { ...state, robot: { ...state.robot, gripperOpen: !state.robot.gripperOpen } }
    case 'SET_SIMULATING':
      return { ...state, isSimulating: action.payload }
    default:
      return state
  }
}

interface RobotContextType {
  state: AppState
  dispatch: React.Dispatch<Action>
  createMission: (origin: MapPoint, destination: MapPoint, objectDescription: string) => void
  cancelMission: (id: string) => void
  emergencyStop: () => void
  releaseEmergency: () => void
  toggleGripper: () => void
  simulateMission: (missionId: string) => void
  addNotification: (type: Notification['type'], title: string, message: string) => void
}

const RobotContext = createContext<RobotContextType | null>(null)

export function RobotProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  const simulationInterval = useRef<NodeJS.Timeout | null>(null)

  // Simulation effect
  useEffect(() => {
    return () => {
      if (simulationInterval.current) clearInterval(simulationInterval.current)
    }
  }, [])

  const addNotification = useCallback((type: Notification['type'], title: string, message: string) => {
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        id: crypto.randomUUID(),
        type,
        title,
        message,
        timestamp: new Date().toISOString(),
        read: false,
      },
    })
  }, [])

  const createMission = useCallback((origin: MapPoint, destination: MapPoint, objectDescription: string) => {
    const mission: Mission = {
      id: crypto.randomUUID(),
      origin,
      destination,
      objectDescription,
      status: 'CREATED',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      progress: 0,
    }
    dispatch({ type: 'ADD_MISSION', payload: mission })
    addNotification('info', 'Mission créée', `Transport de "${objectDescription}" : ${origin.name} → ${destination.name}`)
  }, [addNotification])

  const cancelMission = useCallback((id: string) => {
    dispatch({ type: 'UPDATE_MISSION', payload: { id, status: 'CANCELLED' } })
    addNotification('warning', 'Mission annulée', `Mission ${id.slice(0, 8)} annulée par l'opérateur`)
  }, [addNotification])

  const emergencyStop = useCallback(() => {
    if (simulationInterval.current) {
      clearInterval(simulationInterval.current)
      simulationInterval.current = null
    }
    dispatch({ type: 'EMERGENCY_STOP' })
    addNotification('error', 'ARRÊT D\'URGENCE', 'Arrêt d\'urgence déclenché — Robot immobilisé')
  }, [addNotification])

  const releaseEmergency = useCallback(() => {
    dispatch({ type: 'RELEASE_EMERGENCY' })
    addNotification('success', 'Urgence levée', 'Arrêt d\'urgence désactivé — Robot opérationnel')
  }, [addNotification])

  const toggleGripper = useCallback(() => {
    dispatch({ type: 'TOGGLE_GRIPPER' })
  }, [])

  const simulateMission = useCallback((missionId: string) => {
    const mission = state.missions.find(m => m.id === missionId)
    if (!mission || state.robot.isEmergencyStopped) return

    if (simulationInterval.current) {
      clearInterval(simulationInterval.current)
    }

    const steps = [
      { status: 'ASSIGNED', duration: 1000, message: 'Mission assignée au robot' },
      { status: 'NAVIGATING_TO_PICKUP', duration: 3000, message: `Navigation vers ${mission.origin.name}` },
      { status: 'PICKING_UP', duration: 2000, message: 'Saisie de l\'objet en cours' },
      { status: 'NAVIGATING_TO_DROP', duration: 3000, message: `Navigation vers ${mission.destination.name}` },
      { status: 'DROPPING_OFF', duration: 2000, message: 'Dépose de l\'objet en cours' },
      { status: 'COMPLETED', duration: 0, message: 'Mission terminée avec succès !' },
    ] as const

    let currentStepIndex = 0
    let progress = 0
    
    dispatch({ type: 'SET_ROBOT_STATE', payload: { currentMissionId: missionId, speed: 0.8 } })
    dispatch({ type: 'SET_SIMULATING', payload: true })

    simulationInterval.current = setInterval(() => {
      const step = steps[currentStepIndex]
      
      if (!step) {
        if (simulationInterval.current) clearInterval(simulationInterval.current)
        dispatch({ type: 'SET_ROBOT_STATE', payload: { currentMissionId: null, speed: 0 } })
        dispatch({ type: 'SET_SIMULATING', payload: false })
        return
      }

      progress += 10
      
      // Update robot position based on current step (simplified linear interpolation)
      let targetX = 0
      let targetY = 0
      
      if (step.status === 'NAVIGATING_TO_PICKUP') {
        targetX = mission.origin.x
        targetY = mission.origin.y
      } else if (step.status === 'NAVIGATING_TO_DROP') {
        targetX = mission.destination.x
        targetY = mission.destination.y
      } else if (step.status === 'COMPLETED') {
        // Stay at destination
        targetX = mission.destination.x
        targetY = mission.destination.y
      } else {
        // Stay at current position
        targetX = state.robot.position.x
        targetY = state.robot.position.y
      }

      // Move robot towards target
      if (targetX !== 0 && targetY !== 0) {
        const dx = targetX - state.robot.position.x
        const dy = targetY - state.robot.position.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        
        if (dist > 5) {
           const moveX = state.robot.position.x + (dx / dist) * 5
           const moveY = state.robot.position.y + (dy / dist) * 5
           dispatch({ type: 'SET_ROBOT_POSITION', payload: { x: moveX, y: moveY, heading: Math.atan2(dy, dx) * (180 / Math.PI) } })
        }
      }

      if (progress >= 100) {
        dispatch({ 
          type: 'UPDATE_MISSION', 
          payload: { id: missionId, status: step.status, progress: 100 } 
        })
        
        if (step.message) {
           // Only show notifications for key steps to avoid spam
           if (['ASSIGNED', 'PICKING_UP', 'DROPPING_OFF', 'COMPLETED'].includes(step.status)) {
             addNotification(step.status === 'COMPLETED' ? 'success' : 'info', 'Mission Update', step.message)
           }
        }

        currentStepIndex++
        progress = 0
      } else {
        dispatch({ 
          type: 'UPDATE_MISSION', 
          payload: { id: missionId, status: step.status, progress } 
        })
      }
    }, 100)

  }, [state.missions, state.robot.isEmergencyStopped, state.robot.position, addNotification])

  return (
    <RobotContext.Provider
      value={{
        state,
        dispatch,
        createMission,
        cancelMission,
        emergencyStop,
        releaseEmergency,
        toggleGripper,
        simulateMission,
        addNotification,
      }}
    >
      {children}
    </RobotContext.Provider>
  )
}

export function useRobot() {
  const context = useContext(RobotContext)
  if (!context) {
    throw new Error('useRobot must be used within a RobotProvider')
  }
  return context
}
