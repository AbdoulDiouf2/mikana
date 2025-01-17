export interface MetricCard {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
}

export interface MaintenanceItem {
  id: string;
  machine: string;
  status: 'healthy' | 'warning' | 'critical';
  nextService: string;
  lastService: string;
}

export interface DeliveryRoute {
  id: string;
  driver: string;
  status: 'in-progress' | 'completed' | 'scheduled';
  stops: number;
  eta: string;
}