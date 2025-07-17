import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface UsageData {
  usage: {
    total_ideas: number;
    daily_ideas: number;
    monthly_ideas: number;
  };
  limits: {
    daily_limit: number | string;
    monthly_limit: number | string;
    remaining_today: number | string;
    remaining_month: number | string;
  };
  tier: string;
}

export default function UsageStats() {
  const { getToken } = useAuth();
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUsage() {
      try {
        const token = await getToken();
        const response = await fetch('/api/usage', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        setUsage(data);
      } catch (error) {
        console.error('Failed to load usage:', error);
      } finally {
        setLoading(false);
      }
    }
    loadUsage();
  }, [getToken]);

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-24 rounded-lg"></div>
    );
  }

  if (!usage) return null;

  const getDailyPercent = () => {
    if (usage.limits.daily_limit === 'unlimited') return 0;
    const limit = usage.limits.daily_limit as number;
    return (usage.usage.daily_ideas / limit) * 100;
  };

  const getMonthlyPercent = () => {
    if (usage.limits.monthly_limit === 'unlimited') return 0;
    const limit = usage.limits.monthly_limit as number;
    return (usage.usage.monthly_ideas / limit) * 100;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
        Usage Statistics
      </h3>

      <div className="grid grid-cols-2 gap-4">
        {/* Daily Usage */}
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Today</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {usage.usage.daily_ideas}
            {usage.limits.daily_limit !== 'unlimited' && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {' '}/ {usage.limits.daily_limit}
              </span>
            )}
          </div>
          {usage.limits.daily_limit !== 'unlimited' && (
            <div className="mt-2 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(getDailyPercent(), 100)}%` }}
              ></div>
            </div>
          )}
          {usage.limits.remaining_today !== 'unlimited' && (
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {usage.limits.remaining_today} remaining
            </div>
          )}
        </div>

        {/* Monthly Usage */}
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">This Month</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {usage.usage.monthly_ideas}
            {usage.limits.monthly_limit !== 'unlimited' && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {' '}/ {usage.limits.monthly_limit}
              </span>
            )}
          </div>
          {usage.limits.monthly_limit !== 'unlimited' && (
            <div className="mt-2 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(getMonthlyPercent(), 100)}%` }}
              ></div>
            </div>
          )}
          {usage.limits.remaining_month !== 'unlimited' && (
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {usage.limits.remaining_month} remaining
            </div>
          )}
        </div>
      </div>

      {/* Total Ideas */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-600 dark:text-gray-400">Total Ideas Generated</div>
        <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {usage.usage.total_ideas}
        </div>
      </div>

      {/* Tier Badge */}
      <div className="mt-4">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
          {usage.tier.toUpperCase()} TIER
        </span>
      </div>
    </div>
  );
}
