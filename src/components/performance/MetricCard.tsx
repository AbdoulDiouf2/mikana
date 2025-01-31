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
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {change && (
          <div className={`flex items-center ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />}
            <span className="text-sm ml-1">{Math.abs(change)}%</span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {typeof value === 'string' 
            ? value // Afficher directement les strings
            : (typeof value === 'number' ? value.toFixed(2) : '-')}
          {unit}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  )
}