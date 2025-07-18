"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth, UserButton } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import TemplateSelector from '../components/TemplateSelector';
import LanguageSelector from '../components/LanguageSelector';
import UsageStats from '../components/UsageStats';
import Link from 'next/link';

export default function Product() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState('general');
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    const [error, setError] = useState<string | null>(null);

    const generateIdea = async () => {
        setIsGenerating(true);
        setError(null);
        setIdea('');

        try {
            const jwt = await getToken();
            if (!jwt) {
                setError('Authentication required');
                setIsGenerating(false);
                return;
            }

            let buffer = '';

            await fetchEventSource('/api', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${jwt}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    template: selectedTemplate,
                    language: selectedLanguage
                }),
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    setError('Failed to generate idea. Please try again.');
                    throw err; // Stop retrying
                },
                onclose() {
                    setIsGenerating(false);
                }
            });
        } catch (err: any) {
            setIsGenerating(false);
            if (err.message) {
                setError(err.message);
            }
        }
    };

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
                            href="/analytics"
                            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                        >
                            📊 Analytics
                        </Link>
                        <UserButton showName={true} />
                    </div>
                </div>
            </nav>

            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content */}
                    <div className="lg:col-span-2">
                        {/* Header */}
                        <header className="text-center mb-8">
                            <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                                Business Idea Generator
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400">
                                AI-powered innovation with templates and multi-language support
                            </p>
                        </header>

                        {/* Template Selector */}
                        <TemplateSelector
                            selected={selectedTemplate}
                            onSelect={setSelectedTemplate}
                        />

                        {/* Language Selector */}
                        <LanguageSelector
                            selected={selectedLanguage}
                            onSelect={setSelectedLanguage}
                        />

                        {/* Generate Button */}
                        <button
                            onClick={generateIdea}
                            disabled={isGenerating}
                            className={`w-full py-4 rounded-lg font-semibold text-white transition-all mb-6 ${
                                isGenerating
                                    ? 'bg-gray-400 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105'
                            }`}
                        >
                            {isGenerating ? '🔄 Generating...' : '✨ Generate New Idea'}
                        </button>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                                <p className="text-red-800 dark:text-red-200">{error}</p>
                            </div>
                        )}

                        {/* Idea Display */}
                        {idea && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
                                <div className="markdown-content text-gray-700 dark:text-gray-300">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm, remarkBreaks]}
                                    >
                                        {idea}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        )}

                        {!idea && !isGenerating && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-12 text-center">
                                <div className="text-6xl mb-4">💡</div>
                                <p className="text-gray-500 dark:text-gray-400">
                                    Select a template and language, then click "Generate New Idea" to get started!
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="lg:col-span-1">
                        <UsageStats />

                        {/* Tips Card */}
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                            <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">
                                💡 Tips
                            </h3>
                            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                                <li>• Try different templates for specialized ideas</li>
                                <li>• Generate ideas in your native language</li>
                                <li>• Upgrade for unlimited generations</li>
                                <li>• Check analytics for insights</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
