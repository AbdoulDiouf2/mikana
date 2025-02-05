// components/performance/MetricCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { ArrowDownIcon, ArrowUpIcon } from "lucide-react"

interface MetricCardProps {
  title: string
  value: number | string // Accepter les strings
  unit?: string
  change?: number
  description?: string
}

export function MetricCard({ title, value, unit = "", change, description }: MetricCardProps) {
  return (
    <Card className="dark:bg-gray-800 dark:border-gray-700">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium dark:text-white">{title}</CardTitle>
        {change && (
          <div className={`flex items-center ${change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {change >= 0 ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />}
            <span className="text-sm ml-1">{Math.abs(change)}%</span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold dark:text-white">
          {typeof value === 'string' 
            ? value // Afficher directement les strings
            : (typeof value === 'number' ? value.toFixed(2) : '-')}
          {unit}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground dark:text-gray-400 mt-1">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  )
}