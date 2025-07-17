import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface Analytics {
  analytics: {
    total_ideas_generated: number;
    this_month: number;
    today: number;
    template_distribution: Record<string, number>;
    language_distribution: Record<string, number>;
    most_used_template: string | null;
    most_used_language: string | null;
  };
  tier: string;
}

export default function AnalyticsDashboard() {
  const { getToken } = useAuth();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const token = await getToken();
        const response = await fetch('/api/analytics', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.status === 403) {
          setError('Analytics not available in your tier. Upgrade to access!');
          setLoading(false);
          return;
        }

        const data = await response.json();
        setAnalytics(data);
      } catch (err) {
        setError('Failed to load analytics');
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, [getToken]);

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-64 rounded-lg"></div>
    );
  }

  if (error) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
        <p className="text-yellow-800 dark:text-yellow-200">{error}</p>
      </div>
    );
  }

  if (!analytics) return null;

  const data = analytics.analytics;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">
        📊 Analytics Dashboard
      </h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4">
          <div className="text-sm text-blue-600 dark:text-blue-400 mb-1">Total Ideas</div>
          <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">
            {data.total_ideas_generated}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4">
          <div className="text-sm text-green-600 dark:text-green-400 mb-1">This Month</div>
          <div className="text-3xl font-bold text-green-900 dark:text-green-100">
            {data.this_month}
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4">
          <div className="text-sm text-purple-600 dark:text-purple-400 mb-1">Today</div>
          <div className="text-3xl font-bold text-purple-900 dark:text-purple-100">
            {data.today}
          </div>
        </div>
      </div>

      {/* Template Distribution */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">
          Template Usage
        </h3>
        <div className="space-y-2">
          {Object.entries(data.template_distribution).map(([template, count]) => (
            <div key={template} className="flex items-center">
              <div className="w-32 text-sm text-gray-600 dark:text-gray-400 capitalize">
                {template}
              </div>
              <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-6 relative">
                <div
                  className="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-2"
                  style={{
                    width: `${(count / data.total_ideas_generated) * 100}%`
                  }}
                >
                  <span className="text-xs text-white font-medium">{count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        {data.most_used_template && (
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Most used: <span className="font-semibold">{data.most_used_template}</span>
          </div>
        )}
      </div>

      {/* Language Distribution */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">
          Language Usage
        </h3>
        <div className="flex flex-wrap gap-3">
          {Object.entries(data.language_distribution).map(([lang, count]) => (
            <div
              key={lang}
              className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2"
            >
              <div className="text-xs text-gray-600 dark:text-gray-400 uppercase">{lang}</div>
              <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{count}</div>
            </div>
          ))}
        </div>
        {data.most_used_language && (
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Most used: <span className="font-semibold uppercase">{data.most_used_language}</span>
          </div>
        )}
      </div>
    </div>
  );
}
