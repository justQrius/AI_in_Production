import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface Template {
  name: string;
  description: string;
  icon: string;
  prompt: string;
}

interface TemplateSelectorProps {
  onSelect: (templateKey: string) => void;
  selected: string;
}

export default function TemplateSelector({ onSelect, selected }: TemplateSelectorProps) {
  const { getToken } = useAuth();
  const [templates, setTemplates] = useState<Record<string, Template>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTemplates() {
      try {
        const token = await getToken();
        const response = await fetch('/api/templates', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        setTemplates(data.templates);
      } catch (error) {
        console.error('Failed to load templates:', error);
      } finally {
        setLoading(false);
      }
    }
    loadTemplates();
  }, [getToken]);

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-12 rounded-lg"></div>
    );
  }

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Business Template
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Object.entries(templates).map(([key, template]) => (
          <button
            key={key}
            onClick={() => onSelect(key)}
            className={`p-4 rounded-lg border-2 transition-all ${
              selected === key
                ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-400'
            }`}
          >
            <div className="text-3xl mb-2">{template.icon}</div>
            <div className="text-sm font-medium">{template.name}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
