import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Coins, 
  BarChart3, 
  ShoppingCart,
  Target,
  Clock
} from 'lucide-react';
import BalanceChart from '../components/BalanceChart';
import RecentActivity from '../components/RecentActivity';
import QuickActions from '../components/QuickActions';
import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => api.get('/stats')
  });

  const { data: userStats } = useQuery({
    queryKey: ['userStats'],
    queryFn: () => api.get('/api/v1/users/profile')
  });

  const cards = [
    {
      title: 'Total Points',
      value: userStats?.wallet?.points_balance || '0',
      change: '+12.5%',
      icon: <Coins className="h-8 w-8 text-yellow-500" />,
      color: 'from-yellow-500/10 to-yellow-500/5'
    },
    {
      title: 'Prediction Accuracy',
      value: userStats?.stats?.success_rate ? `${userStats.stats.success_rate}%` : 'N/A',
      change: '+5.2%',
      icon: <Target className="h-8 w-8 text-green-500" />,
      color: 'from-green-500/10 to-green-500/5'
    },
    {
      title: 'Active Listings',
      value: userStats?.stats?.active_listings || '0',
      change: '+2',
      icon: <ShoppingCart className="h-8 w-8 text-blue-500" />,
      color: 'from-blue-500/10 to-blue-500/5'
    },
    {
      title: 'Daily Interest',
      value: '0.1%',
      change: 'Daily',
      icon: <TrendingUp className="h-8 w-8 text-purple-500" />,
      color: 'from-purple-500/10 to-purple-500/5'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-400">Welcome back! Here's your overview.</p>
        </div>
        <div className="flex items-center space-x-2 text-gray-400">
          <Clock className="h-4 w-4" />
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gradient-to-br ${card.color} backdrop-blur-sm rounded-2xl p-6 border border-white/10`}
          >
            <div className="flex items-center justify-between mb-4">
              {card.icon}
              <span className="text-sm font-medium text-green-400">
                {card.change}
              </span>
            </div>
            <h3 className="text-2xl font-bold mb-1">{card.value}</h3>
            <p className="text-gray-400">{card.title}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
            <h2 className="text-xl font-bold mb-6">Balance History</h2>
            <BalanceChart />
          </div>
        </div>
        <div className="lg:col-span-1">
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10 h-full">
            <h2 className="text-xl font-bold mb-6">Recent Activity</h2>
            <RecentActivity />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
        <h2 className="text-xl font-bold mb-6">Quick Actions</h2>
        <QuickActions />
      </div>

      {/* System Stats */}
      {stats && (
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 border border-white/10">
          <h2 className="text-xl font-bold mb-6">System Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400">
                {stats.total_users}
              </div>
              <div className="text-gray-400">Total Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">
                {stats.total_predictions}
              </div>
              <div className="text-gray-400">Predictions Made</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400">
                {Math.round(stats.total_points_in_circulation).toLocaleString()}
              </div>
              <div className="text-gray-400">Points in Circulation</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400">
                {stats.active_listings}
              </div>
              <div className="text-gray-400">Active Listings</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
