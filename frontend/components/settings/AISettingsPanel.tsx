'use client';

/**
 * AI Settings Panel Component (Phase III - US0)
 *
 * Manages user preferences for AI chatbot features:
 * - Opt-in/opt-out toggle
 * - Language preferences
 * - Voice input settings
 * - Privacy controls
 */

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { UserPreferences } from '@/lib/types';
import { PrivacyNotice } from '@/components/ui/PrivacyNotice';

interface AISettingsPanelProps {
  userId: string;
}

export function AISettingsPanel({ userId }: AISettingsPanelProps) {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPrivacyNotice, setShowPrivacyNotice] = useState(false);
  const [isOptingIn, setIsOptingIn] = useState(false);
  const [isOptingOut, setIsOptingOut] = useState(false);
  const [showOptOutConfirm, setShowOptOutConfirm] = useState(false);

  // Load preferences on mount
  useEffect(() => {
    loadPreferences();
  }, [userId]);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const prefs = await api.getAIPreferences(userId);
      setPreferences(prefs);
    } catch (err: any) {
      console.error('Error loading AI preferences:', err);
      setError('Failed to load AI preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleEnableAI = () => {
    setShowPrivacyNotice(true);
  };

  const handlePrivacyAccept = async (consentVersion: string) => {
    try {
      setIsOptingIn(true);
      setError(null);

      await api.aiOptIn(userId, {
        privacy_consent_version: consentVersion,
        preferred_language: 'en',
      });

      // Reload preferences
      await loadPreferences();

      setShowPrivacyNotice(false);

      // Show success message
      alert('✅ AI Chatbot enabled successfully! You can now use the chat feature on the dashboard.');
    } catch (err: any) {
      console.error('Error enabling AI:', err);
      setError(err.message || 'Failed to enable AI features');
    } finally {
      setIsOptingIn(false);
    }
  };

  const handleDisableAI = () => {
    setShowOptOutConfirm(true);
  };

  const confirmOptOut = async (deleteHistory: boolean) => {
    try {
      setIsOptingOut(true);
      setError(null);

      await api.aiOptOut(userId, deleteHistory);

      // Reload preferences
      await loadPreferences();

      setShowOptOutConfirm(false);

      // Show confirmation message
      alert('🔒 AI Chatbot disabled. The chat feature is now locked. You can re-enable it anytime in settings.');
    } catch (err: any) {
      console.error('Error disabling AI:', err);
      setError(err.message || 'Failed to disable AI features');
    } finally {
      setIsOptingOut(false);
    }
  };

  const handleLanguageChange = async (language: 'en' | 'ur') => {
    if (!preferences?.ai_enabled) return;

    try {
      setError(null);
      await api.updateAIPreferences(userId, { preferred_language: language });
      await loadPreferences();
    } catch (err: any) {
      console.error('Error updating language:', err);
      setError('Failed to update language preference');
    }
  };

  const handleAutoDetectToggle = async () => {
    if (!preferences?.ai_enabled) return;

    try {
      setError(null);
      await api.updateAIPreferences(userId, {
        auto_detect_language: !preferences.auto_detect_language,
      });
      await loadPreferences();
    } catch (err: any) {
      console.error('Error updating auto-detect:', err);
      setError('Failed to update auto-detect setting');
    }
  };

  const handleVoiceToggle = async () => {
    if (!preferences?.ai_enabled) return;

    try {
      setError(null);
      await api.updateAIPreferences(userId, {
        voice_input_enabled: !preferences.voice_input_enabled,
      });
      await loadPreferences();
    } catch (err: any) {
      console.error('Error updating voice input:', err);
      setError('Failed to update voice input setting');
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-10 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    );
  }

  const isAIEnabled = preferences?.ai_enabled || false;

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">AI Assistant Settings</h2>
        <p className="text-sm text-gray-600 mt-1">
          Manage your AI-powered task management features
        </p>
      </div>

      <div className="p-6 space-y-6">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Enable/Disable AI */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">AI Features</h3>
            <p className="text-sm text-gray-600">
              {isAIEnabled
                ? 'AI assistant is enabled - you can chat to manage tasks'
                : 'Enable AI to use natural language task management'}
            </p>
          </div>
          <button
            onClick={isAIEnabled ? handleDisableAI : handleEnableAI}
            disabled={isOptingIn || isOptingOut}
            className={`px-4 py-2 rounded font-medium ${
              isAIEnabled
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isAIEnabled ? 'Disable AI' : 'Enable AI'}
          </button>
        </div>

        {/* AI Settings (only shown when enabled) */}
        {isAIEnabled && preferences && (
          <>
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Preferences
              </h3>

              {/* Language Preference */}
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Language
                  </label>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleLanguageChange('en')}
                      className={`px-4 py-2 rounded border ${
                        preferences.preferred_language === 'en'
                          ? 'bg-blue-50 border-blue-600 text-blue-700'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      English
                    </button>
                    <button
                      onClick={() => handleLanguageChange('ur')}
                      className={`px-4 py-2 rounded border ${
                        preferences.preferred_language === 'ur'
                          ? 'bg-blue-50 border-blue-600 text-blue-700'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      اردو (Urdu)
                    </button>
                  </div>
                </div>

                {/* Auto-detect Language */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      Auto-detect language
                    </label>
                    <p className="text-xs text-gray-500">
                      Automatically detect language from your messages
                    </p>
                  </div>
                  <button
                    onClick={handleAutoDetectToggle}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      preferences.auto_detect_language
                        ? 'bg-blue-600'
                        : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        preferences.auto_detect_language
                          ? 'translate-x-6'
                          : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                {/* Voice Input */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      Voice input (Bonus Feature)
                    </label>
                    <p className="text-xs text-gray-500">
                      Use microphone to speak commands
                    </p>
                  </div>
                  <button
                    onClick={handleVoiceToggle}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      preferences.voice_input_enabled
                        ? 'bg-blue-600'
                        : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        preferences.voice_input_enabled
                          ? 'translate-x-6'
                          : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Privacy Info */}
            <div className="bg-gray-50 rounded p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">
                Privacy Information
              </h4>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>
                  • Consent version: {preferences.privacy_consent_version}
                </li>
                <li>
                  • Opted in:{' '}
                  {preferences.ai_opt_in_date
                    ? new Date(preferences.ai_opt_in_date).toLocaleDateString()
                    : 'N/A'}
                </li>
                <li>• Chat history is stored securely</li>
                <li>• You can delete your data anytime by disabling AI</li>
              </ul>
            </div>
          </>
        )}
      </div>

      {/* Privacy Notice Modal */}
      <PrivacyNotice
        isOpen={showPrivacyNotice}
        onClose={() => setShowPrivacyNotice(false)}
        onAccept={handlePrivacyAccept}
        isLoading={isOptingIn}
      />

      {/* Opt-out Confirmation Modal */}
      {showOptOutConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Disable AI Features?
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              This will disable the AI assistant. You can re-enable it anytime.
            </p>

            <div className="space-y-3">
              <button
                onClick={() => confirmOptOut(false)}
                disabled={isOptingOut}
                className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                {isOptingOut ? 'Disabling...' : 'Disable (Keep chat history)'}
              </button>
              <button
                onClick={() => confirmOptOut(true)}
                disabled={isOptingOut}
                className="w-full px-4 py-2 bg-red-700 text-white rounded hover:bg-red-800 disabled:opacity-50"
              >
                {isOptingOut
                  ? 'Disabling...'
                  : 'Disable & Delete chat history'}
              </button>
              <button
                onClick={() => setShowOptOutConfirm(false)}
                disabled={isOptingOut}
                className="w-full px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
