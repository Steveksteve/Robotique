'use client'

import { useRobot } from '@/context/RobotContext'
import { MAP_POINTS, type MapPoint } from '@/types'
import { useState } from 'react'
import { MapPin, Navigation, Map as MapIcon, Target } from 'lucide-react'

interface RobotMapProps {
  onSelectPoint?: (point: MapPoint) => void
  selectedOrigin?: MapPoint | null
  selectedDestination?: MapPoint | null
  mode?: 'view' | 'select-origin' | 'select-destination'
}

export default function RobotMap({ onSelectPoint, selectedOrigin, selectedDestination, mode = 'view' }: RobotMapProps) {
  const { state } = useRobot()
  const [hoveredPoint, setHoveredPoint] = useState<string | null>(null)

  const { position } = state.robot
  const activeMission = state.missions.find(m => m.id === state.robot.currentMissionId)

  const getPointColor = (point: MapPoint) => {
    if (selectedOrigin?.id === point.id) return '#10b981' // Success
    if (selectedDestination?.id === point.id) return '#ef4444' // Danger
    switch (point.type) {
      case 'pickup': return '#3b82f6' // Primary
      case 'dropoff': return '#8b5cf6' // Violet
      case 'charging': return '#f59e0b' // Warning
      case 'waypoint': return '#525252' // Text tertiary
    }
  }

  const getPointRadius = (point: MapPoint) => {
    const isHovered = hoveredPoint === point.id
    const isSelected = selectedOrigin?.id === point.id || selectedDestination?.id === point.id
    if (isSelected) return 12
    if (isHovered) return 10
    return 6
  }

  return (
    <div className="glass-panel h-full flex flex-col">
      <div className="panel-header justify-between">
        <span className="flex items-center gap-2">
          <MapIcon className="w-4 h-4 text-primary" />
          Carte du bâtiment
        </span>
        {mode !== 'view' && (
          <span className="badge badge-primary normal-case tracking-normal animate-pulse">
            {mode === 'select-origin' ? 'Sélectionnez le point de départ' : 'Sélectionnez la destination'}
          </span>
        )}
      </div>

      <div className="flex-1 p-0 relative overflow-hidden flex items-center justify-center bg-[#050505] rounded-b-3xl">
        <svg
          viewBox="0 0 800 600"
          className="w-full h-full object-contain p-8"
        >
          {/* Technical Grid Background */}
          <defs>
            <pattern id="grid-small" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
            </pattern>
            <pattern id="grid-large" width="100" height="100" patternUnits="userSpaceOnUse">
              <rect width="100" height="100" fill="url(#grid-small)" />
              <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
            </pattern>
            <filter id="glow-path">
               <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
               <feMerge>
                 <feMergeNode in="coloredBlur"/>
                 <feMergeNode in="SourceGraphic"/>
               </feMerge>
            </filter>
          </defs>
          
          <rect width="800" height="600" fill="url(#grid-large)" />

          {/* Architectural Layout */}
          <g stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
             {/* Outer Walls */}
             <rect x="40" y="40" width="720" height="520" rx="20" stroke="rgba(255,255,255,0.4)" strokeWidth="4" />
             
             {/* Vertical Dividers */}
             <path d="M 240 40 L 240 560" strokeDasharray="4 4" opacity="0.5" />
             <path d="M 500 40 L 500 560" strokeDasharray="4 4" opacity="0.5" />
             
             {/* Horizontal Dividers */}
             <path d="M 40 220 L 240 220" strokeDasharray="4 4" opacity="0.5" />
             <path d="M 240 220 L 500 220" strokeDasharray="4 4" opacity="0.5" />
             <path d="M 500 220 L 760 220" strokeDasharray="4 4" opacity="0.5" />
             <path d="M 40 420 L 240 420" strokeDasharray="4 4" opacity="0.5" />
             <path d="M 240 420 L 500 420" strokeDasharray="4 4" opacity="0.5" />
          </g>

          {/* Room Labels */}
          <g fill="rgba(255,255,255,0.3)" fontSize="14" fontFamily="monospace" fontWeight="bold" letterSpacing="1" textAnchor="middle">
            {/* Left Column */}
            <text x="140" y="150">ZONE ACCUEIL</text>
            <text x="140" y="460">ENTREPÔT</text>
            
            {/* Middle Column */}
            <text x="370" y="80">BUREAUX</text>
            <text x="370" y="460">ARCHIVES</text>
            
            {/* Right Column */}
            <text x="630" y="80">SALLE RÉUNION</text>
            
            {/* Special Labels */}
            <text x="80" y="60" fontSize="10" opacity="0.7" textAnchor="start">STATION CHARGE</text>
          </g>



          {/* Robot Label */}
          <text
            x={position.x}
            y={position.y + 30}
            textAnchor="middle"
            fill="white"
            fontSize="10"
            fontWeight="bold"
            letterSpacing="1"
            className="select-none drop-shadow-md"
          >
            RAA-01
          </text>

          {/* Mission path */}
          {activeMission && (
            <path
              d={`M ${activeMission.origin.x} ${activeMission.origin.y} L ${activeMission.destination.x} ${activeMission.destination.y}`}
              stroke="#3b82f6"
              strokeWidth="2"
              strokeDasharray="8 4"
              opacity="0.6"
              fill="none"
              className="animate-pulse"
            />
          )}

          {/* Map Points */}
          {MAP_POINTS.map((point) => (
            <g 
              key={point.id}
              onClick={() => onSelectPoint?.(point)}
              onMouseEnter={() => setHoveredPoint(point.id)}
              onMouseLeave={() => setHoveredPoint(null)}
              className={`${onSelectPoint ? 'cursor-pointer' : ''} transition-all duration-300`}
            >
              {/* Pulse effect for selected/hovered */}
              {(hoveredPoint === point.id || selectedOrigin?.id === point.id || selectedDestination?.id === point.id) && (
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="20"
                  fill={getPointColor(point)}
                  opacity="0.2"
                  className="animate-ping"
                />
              )}
              
              <circle
                cx={point.x}
                cy={point.y}
                r={getPointRadius(point)}
                fill={getPointColor(point)}
                stroke="white"
                strokeWidth="2"
                filter="url(#glow)"
                className="transition-all duration-300"
              />
              
              {/* Tooltip */}
              {hoveredPoint === point.id && (
                <g transform={`translate(${point.x}, ${point.y - 25})`}>
                  <rect
                    x="-40"
                    y="-20"
                    width="80"
                    height="20"
                    rx="4"
                    fill="rgba(0,0,0,0.8)"
                  />
                  <text
                    x="0"
                    y="-6"
                    fill="white"
                    fontSize="10"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {point.name}
                  </text>
                </g>
              )}
            </g>
          ))}

          {/* Robot */}
          <g transform={`translate(${position.x}, ${position.y}) rotate(${position.heading})`}>
            {/* Robot Glow */}
            <circle r="15" fill="rgba(59, 130, 246, 0.2)" filter="url(#glow)" />
            
            {/* Robot Body */}
            <circle r="8" fill="#3b82f6" stroke="white" strokeWidth="2" />
            
            {/* Direction Indicator */}
            <path d="M 0 -8 L 6 8 L 0 5 L -6 8 Z" fill="white" />
          </g>
        </svg>

        {/* Legend Overlay */}
        <div className="absolute bottom-6 left-6 flex gap-4 pointer-events-none">
          <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/5">
            <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
            <span className="text-[10px] text-gray-300 font-medium tracking-wide">Pickup</span>
          </div>
          <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/5">
            <div className="w-2 h-2 rounded-full bg-violet-500 shadow-[0_0_10px_rgba(139,92,246,0.5)]" />
            <span className="text-[10px] text-gray-300 font-medium tracking-wide">Dropoff</span>
          </div>
          <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/5">
            <div className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
            <span className="text-[10px] text-gray-300 font-medium tracking-wide">Charge</span>
          </div>
        </div>
      </div>
    </div>
  )
}
