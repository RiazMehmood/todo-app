'use client';

/**
 * Settings Page (Phase III - US0)
 *
 * Provides access to user settings including AI features configuration.
 * Protected route requiring authentication.
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { requireAuth, logout } from '@/lib/auth';
import { Button } from '@/components/ui/Button';
import { AISettingsPanel } from '@/components/settings/AISettingsPanel';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const currentUser = requireAuth();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
  }, [router]);

  function handleLogout() {
    logout();
  }

  function handleBackToDashboard() {
    router.push('/dashboard');
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-sm text-gray-600 mt-1">{user.name} ({user.email})</p>
          </div>
          <div className="flex gap-3">
            <Button onClick={handleBackToDashboard} variant="secondary">
              Back to Dashboard
            </Button>
            <Button onClick={handleLogout} variant="secondary">
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* AI Settings Section */}
          <AISettingsPanel userId={user.id} />

          {/* Future sections can be added here */}
          {/* Example: Profile Settings, Notification Settings, etc. */}
        </div>
      </main>
    </div>
  );
}
