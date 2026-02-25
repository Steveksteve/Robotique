import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { RobotProvider } from '@/context/RobotContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'RAA — Robot d\'Assistance Autonome',
  description: 'Interface opérateur pour le Robot d\'Assistance Autonome',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <RobotProvider>
          {children}
        </RobotProvider>
      </body>
    </html>
  )
}
