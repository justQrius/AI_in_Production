"use client"

import { UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import UsageStats from '../components/UsageStats';

export default function Analytics() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* Top Navigation */}
            <nav className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg">
                <div className="container mx-auto px-4 py-3 flex justify-between items-center">
                    <h1 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                        IdeaGen Pro
                    </h1>
                    <div className="flex items-center gap-4">
                        <Link
                            href="/product"
                            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                        >
                            ← Back to Generator
                        </Link>
                        <UserButton showName={true} />
                    </div>
                </div>
            </nav>

            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <header className="text-center mb-8">
                    <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                        Analytics Dashboard
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Track your idea generation patterns and insights
                    </p>
                </header>

                <div className="max-w-6xl mx-auto">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Main Analytics */}
                        <div className="lg:col-span-2">
                            <AnalyticsDashboard />
                        </div>

                        {/* Usage Stats Sidebar */}
                        <div>
                            <UsageStats />

                            {/* Upgrade CTA */}
                            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg shadow p-6 text-white">
                                <h3 className="text-lg font-bold mb-2">🚀 Want More?</h3>
                                <p className="text-sm mb-4 opacity-90">
                                    Upgrade to unlock unlimited ideas, all templates, and advanced analytics.
                                </p>
                                <button className="w-full bg-white text-blue-600 font-semibold py-2 px-4 rounded-lg hover:bg-gray-100 transition">
                                    Upgrade Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
