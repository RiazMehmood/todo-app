'use client';

/**
 * Privacy Notice Modal for AI Features Opt-in (Phase III - US0)
 *
 * Displays privacy information and consent form when users enable AI features.
 * Required for GDPR/CCPA compliance.
 */

import { useState } from 'react';

interface PrivacyNoticeProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: (consentVersion: string) => void;
  isLoading?: boolean;
}

export function PrivacyNotice({
  isOpen,
  onClose,
  onAccept,
  isLoading = false,
}: PrivacyNoticeProps) {
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);
  const consentVersion = '1.0.0';

  // Handle scroll to detect if user has read the notice
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    const scrolledToBottom =
      element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

    if (scrolledToBottom && !hasScrolledToBottom) {
      setHasScrolledToBottom(true);
    }
  };

  const handleAccept = () => {
    onAccept(consentVersion);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            AI Features Privacy Notice
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Please review and accept to enable AI-powered task management
          </p>
        </div>

        {/* Content - Scrollable */}
        <div
          className="px-6 py-4 overflow-y-auto flex-1"
          onScroll={handleScroll}
        >
          <div className="space-y-4 text-gray-700">
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                What AI Features Do
              </h3>
              <p className="text-sm">
                Our AI assistant helps you manage tasks through natural language
                commands in English and Urdu. You can create, view, update, and
                delete tasks by chatting with the AI assistant.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Data Collection and Usage
              </h3>
              <ul className="list-disc list-inside text-sm space-y-1">
                <li>Your chat messages are sent to OpenAI for processing</li>
                <li>Conversation history is stored to provide context</li>
                <li>Task data is accessed to fulfill your requests</li>
                <li>Language preferences are saved for better responses</li>
              </ul>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Data Sharing
              </h3>
              <p className="text-sm">
                Your chat messages are processed by OpenAI's GPT-4 model. Please
                review{' '}
                <a
                  href="https://openai.com/policies/privacy-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  OpenAI's Privacy Policy
                </a>{' '}
                for details on how they handle data.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Your Rights
              </h3>
              <ul className="list-disc list-inside text-sm space-y-1">
                <li>
                  <strong>Opt-out anytime:</strong> Disable AI features in settings
                </li>
                <li>
                  <strong>Delete history:</strong> Request deletion of all chat history
                </li>
                <li>
                  <strong>Data access:</strong> Contact us to access your stored data
                </li>
                <li>
                  <strong>No obligation:</strong> AI features are completely optional
                </li>
              </ul>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Data Retention
              </h3>
              <p className="text-sm">
                Chat history is retained indefinitely for your convenience. You can
                delete it anytime by opting out and selecting "Delete chat history."
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Security
              </h3>
              <p className="text-sm">
                All communications are encrypted (HTTPS). Your data is stored
                securely and isolated from other users. Only you can access your
                chat history and tasks.
              </p>
            </section>

            <section className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <h3 className="text-md font-semibold text-yellow-900 mb-1">
                Important Note
              </h3>
              <p className="text-sm text-yellow-800">
                Do not share sensitive personal information (passwords, credit
                cards, etc.) with the AI assistant. While conversations are secure,
                avoid including highly confidential data.
              </p>
            </section>

            <section className="pt-4">
              <p className="text-xs text-gray-500">
                Privacy Notice Version: {consentVersion} | Last Updated: December
                16, 2025
              </p>
            </section>
          </div>
        </div>

        {/* Footer with Actions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          {!hasScrolledToBottom && (
            <p className="text-sm text-amber-600 mb-3 text-center">
              Please scroll to the bottom to read the full notice
            </p>
          )}

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleAccept}
              disabled={!hasScrolledToBottom || isLoading}
              className="px-6 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Enabling...' : 'Accept & Enable AI'}
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-3 text-center">
            By clicking "Accept & Enable AI", you consent to the collection and
            processing of your data as described above.
          </p>
        </div>
      </div>
    </div>
  );
}
