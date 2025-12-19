'use client';

/**
 * Test page to verify environment variables are loaded correctly.
 * Visit /test-env to see what values your deployment is using.
 */

export default function TestEnvPage() {
  // These will be undefined in browser, but we can test the API call
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'NOT SET';
  const aiEnabled = process.env.NEXT_PUBLIC_AI_ENABLED || 'NOT SET';

  const testBackendConnection = async () => {
    try {
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();

      return {
        success: true,
        status: response.status,
        data: data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  };

  const handleTest = async () => {
    const result = await testBackendConnection();
    alert(JSON.stringify(result, null, 2));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Environment Variables Test</h1>

        <div className="space-y-4">
          <div className="border-b pb-4">
            <h2 className="text-lg font-semibold mb-2">Current Values:</h2>
            <div className="bg-gray-50 p-4 rounded font-mono text-sm">
              <p><strong>NEXT_PUBLIC_API_URL:</strong> {apiUrl}</p>
              <p><strong>NEXT_PUBLIC_AI_ENABLED:</strong> {aiEnabled}</p>
            </div>
          </div>

          <div className="border-b pb-4">
            <h2 className="text-lg font-semibold mb-2">Expected Values:</h2>
            <div className="bg-green-50 p-4 rounded font-mono text-sm">
              <p><strong>NEXT_PUBLIC_API_URL:</strong> https://todo-app-production-be56.up.railway.app</p>
              <p><strong>NEXT_PUBLIC_AI_ENABLED:</strong> true</p>
            </div>
          </div>

          <div>
            <button
              onClick={handleTest}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
            >
              Test Backend Connection
            </button>
            <p className="text-sm text-gray-600 mt-2">
              Click to test if the backend is accessible from this deployment
            </p>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-sm">
              <strong>⚠️ Note:</strong> If you see "NOT SET" above, your environment variables
              are not configured. Go to Vercel Settings → Environment Variables and add them,
              then redeploy.
            </p>
          </div>

          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <p className="text-sm">
              <strong>ℹ️ How to verify:</strong>
              <ol className="list-decimal ml-4 mt-2 space-y-1">
                <li>Open DevTools (F12) → Network tab</li>
                <li>Click "Test Backend Connection" button</li>
                <li>Look at the request URL</li>
                <li>Should be: https://todo-app-production-be56.up.railway.app/health</li>
                <li>Should NOT be: http://localhost:8000/health</li>
              </ol>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
