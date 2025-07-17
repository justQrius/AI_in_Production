import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';

interface Language {
  name: string;
  native_name: string;
  flag: string;
}

interface LanguageSelectorProps {
  onSelect: (langCode: string) => void;
  selected: string;
}

export default function LanguageSelector({ onSelect, selected }: LanguageSelectorProps) {
  const { getToken } = useAuth();
  const [languages, setLanguages] = useState<Record<string, Language>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLanguages() {
      try {
        const token = await getToken();
        const response = await fetch('/api/languages', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        setLanguages(data.languages);
      } catch (error) {
        console.error('Failed to load languages:', error);
      } finally {
        setLoading(false);
      }
    }
    loadLanguages();
  }, [getToken]);

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-10 rounded-lg"></div>
    );
  }

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Language
      </label>
      <select
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {Object.entries(languages).map(([code, lang]) => (
          <option key={code} value={code}>
            {lang.flag} {lang.native_name} ({lang.name})
          </option>
        ))}
      </select>
    </div>
  );
}
