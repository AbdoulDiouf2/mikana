import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Brain, 
  Wrench, 
  Truck, 
  Users,
  Settings,
  HelpCircle
} from 'lucide-react';
import Logo from '../common/Logo';

const navItems = [
  { icon: LayoutDashboard, label: 'Tableau de Bord', path: '/' },
  { icon: Brain, label: 'Prévision Commandes', path: '/prediction' },
  { icon: Wrench, label: 'Maintenance', path: '/maintenance' },
  { icon: Truck, label: 'Livraison', path: '/delivery' },
  { icon: Users, label: 'Gestion RH', path: '/hr' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <div className="mb-8">
          <Logo />
        </div>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="absolute bottom-0 w-full p-4 border-t border-slate-800">
        <div className="flex items-center space-x-4 text-slate-300">
          <Settings className="w-5 h-5" />
          <HelpCircle className="w-5 h-5" />
        </div>
      </div>
    </aside>
  );
}