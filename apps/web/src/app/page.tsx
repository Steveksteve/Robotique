'use client'

import { useState } from 'react'
import type { MapPoint } from '@/types'
import Header from '@/components/Header'
import RobotMap from '@/components/RobotMap'
import MissionForm from '@/components/MissionForm'
import ControlPanel from '@/components/ControlPanel'
import RobotStatus from '@/components/RobotStatus'
import MissionList from '@/components/MissionList'
import StatsCards from '@/components/StatsCards'

export default function DashboardPage() {
  const [selectedOrigin, setSelectedOrigin] = useState<MapPoint | null>(null)
  const [selectedDestination, setSelectedDestination] = useState<MapPoint | null>(null)

  const selectMode = !selectedOrigin
    ? 'select-origin'
    : !selectedDestination
    ? 'select-destination'
    : 'view'

  const handleSelectPoint = (point: MapPoint) => {
    if (!selectedOrigin) {
      if (point.type === 'pickup' || point.type === 'waypoint') {
        setSelectedOrigin(point)
      }
    } else if (!selectedDestination) {
      if (point.id !== selectedOrigin.id && (point.type === 'dropoff' || point.type === 'waypoint')) {
        setSelectedDestination(point)
      }
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 p-4 lg:p-6 pt-24 lg:pt-28 max-w-[1800px] mx-auto w-full flex flex-col gap-4">
        {/* Top Row: Stats (Compact) */}
        <div className="shrink-0">
          <StatsCards />
        </div>

        {/* Main Bento Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          
          {/* Left Column: Map (Main Focus) - Spans 8 cols */}
          <div className="lg:col-span-8 flex flex-col gap-4">
            <div className="relative h-[600px]">
              <RobotMap
                onSelectPoint={handleSelectPoint}
                selectedOrigin={selectedOrigin}
                selectedDestination={selectedDestination}
                mode={selectMode as 'view' | 'select-origin' | 'select-destination'}
              />
              
              {/* Floating Mission Form overlaying the map bottom-left or separate? 
                  Let's keep it separate for now but compact below map or inside map container.
                  Actually, putting MissionForm in a sidebar might be better for "Dashboard" feel.
                  Let's try putting it below the map for now.
              */}
            </div>
          </div>

          {/* Right Column: Sidebar (Controls & Status) - Spans 4 cols */}
          <div className="lg:col-span-4 flex flex-col gap-4 min-h-0 overflow-hidden">
            
            {/* Top Right: Status & Controls Grid */}
            <div className="grid grid-cols-2 gap-4 shrink-0 min-h-[220px]">
              <RobotStatus />
              <ControlPanel />
            </div>

            {/* Middle Right: Mission Form - Fixed height to prevent collapse */}
            <div className="shrink-0 min-h-[300px]">
               <MissionForm
                selectedOrigin={selectedOrigin}
                selectedDestination={selectedDestination}
                onSetOrigin={setSelectedOrigin}
                onSetDestination={setSelectedDestination}
              />
            </div>

            {/* Bottom Right: Mission List (Fills remaining space) */}
            <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
              <MissionList />
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-slate-900 border-t border-slate-800 px-6 py-3 text-center">
        <p className="text-xs text-slate-600">
          RAA — Robot d&apos;Assistance Autonome | HETIC Web3 — Février 2026 | Mode simulation (pas de backend)
        </p>
      </footer>
    </div>
  )
}
