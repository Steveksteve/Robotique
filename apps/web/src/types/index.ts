// === Mission Types ===

export type MissionStatus =
  | 'CREATED'
  | 'ASSIGNED'
  | 'NAVIGATING_TO_PICKUP'
  | 'PICKING_UP'
  | 'NAVIGATING_TO_DROP'
  | 'DROPPING_OFF'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'FAILED'
  | 'EMERGENCY_STOPPED'

export interface MapPoint {
  id: string
  name: string
  x: number
  y: number
  type: 'pickup' | 'dropoff' | 'waypoint' | 'charging'
}

export interface Mission {
  id: string
  origin: MapPoint
  destination: MapPoint
  objectDescription: string
  status: MissionStatus
  createdAt: string
  updatedAt: string
  estimatedDuration?: number
  progress?: number
}

// === Robot Types ===

export interface RobotPosition {
  x: number
  y: number
  heading: number // degrees
}

export type RobotConnectionStatus = 'connected' | 'disconnected' | 'reconnecting'

export interface RobotState {
  batteryLevel: number
  position: RobotPosition
  speed: number
  connectionStatus: RobotConnectionStatus
  lastHeartbeat: string
  isEmergencyStopped: boolean
  gripperOpen: boolean
  currentMissionId: string | null
}

// === WebSocket Event Types ===

export interface WsEvents {
  'mission:created': Mission
  'mission:updated': { id: string; status: MissionStatus; progress?: number }
  'mission:completed': { id: string }
  'mission:assign': { missionId: string }
  'robot:heartbeat': { batteryLevel: number; timestamp: string }
  'robot:position': RobotPosition
  'robot:obstacle-detected': { x: number; y: number; distance: number }
}

// === UI Types ===

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
}

export const MISSION_STATUS_CONFIG: Record<MissionStatus, {
  label: string
  color: string
  bgColor: string
  icon: string
}> = {
  CREATED: { label: 'Créée', color: 'text-blue-600', bgColor: 'bg-blue-100', icon: '📋' },
  ASSIGNED: { label: 'Assignée', color: 'text-purple-600', bgColor: 'bg-purple-100', icon: '🤖' },
  NAVIGATING_TO_PICKUP: { label: 'En route (pickup)', color: 'text-amber-600', bgColor: 'bg-amber-100', icon: '🚗' },
  PICKING_UP: { label: 'Saisie objet', color: 'text-orange-600', bgColor: 'bg-orange-100', icon: '🦾' },
  NAVIGATING_TO_DROP: { label: 'En route (drop)', color: 'text-amber-600', bgColor: 'bg-amber-100', icon: '🚗' },
  DROPPING_OFF: { label: 'Dépose objet', color: 'text-orange-600', bgColor: 'bg-orange-100', icon: '📦' },
  COMPLETED: { label: 'Terminée', color: 'text-green-600', bgColor: 'bg-green-100', icon: '✅' },
  CANCELLED: { label: 'Annulée', color: 'text-gray-600', bgColor: 'bg-gray-100', icon: '❌' },
  FAILED: { label: 'Échouée', color: 'text-red-600', bgColor: 'bg-red-100', icon: '⚠️' },
  EMERGENCY_STOPPED: { label: 'Arrêt urgence', color: 'text-red-700', bgColor: 'bg-red-200', icon: '🛑' },
}

export const MAP_POINTS: MapPoint[] = [
  { id: 'accueil', name: 'Accueil', x: 120, y: 350, type: 'pickup' },
  { id: 'bureau-a', name: 'Bureau A', x: 360, y: 150, type: 'dropoff' },
  { id: 'bureau-b', name: 'Bureau B', x: 640, y: 150, type: 'dropoff' },
  { id: 'salle-reunion', name: 'Salle Réunion', x: 640, y: 400, type: 'dropoff' },
  { id: 'archives', name: 'Archives', x: 360, y: 500, type: 'pickup' },
  { id: 'entrepot', name: 'Entrepôt', x: 120, y: 500, type: 'pickup' },
  { id: 'couloir-1', name: 'Couloir 1', x: 360, y: 280, type: 'waypoint' },
  { id: 'couloir-2', name: 'Couloir 2', x: 360, y: 400, type: 'waypoint' },
  { id: 'charge', name: 'Station Charge', x: 80, y: 80, type: 'charging' },
]
