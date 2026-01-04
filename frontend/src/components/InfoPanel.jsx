import React, { useState } from 'react';
import { useJarvisStore } from '../store/jarvisStore';
import jarvisApi from '../api/jarvisApi';

const InfoPanel = () => {
  const { sceneData, commandHistory, loading, error, contextId, removeObject } = useJarvisStore();
  const [deletingIndex, setDeletingIndex] = useState(null);

  const handleDeleteObject = async (index) => {
    if (!contextId) return;

    setDeletingIndex(index);
    try {
      await jarvisApi.deleteObject(contextId, index);
      removeObject(index);
    } catch (err) {
      console.error('Failed to delete object:', err);
    } finally {
      setDeletingIndex(null);
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Scene Info */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold mb-3">Scene Information</h2>
        
        {sceneData ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Objects:</span>
              <span className="text-white font-medium">{sceneData.objects?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Environment:</span>
              <span className="text-white font-medium">
                {sceneData.environment?.type || 'None'}
              </span>
            </div>
            {sceneData.created_at && (
              <div className="flex justify-between">
                <span className="text-gray-400">Created:</span>
                <span className="text-white font-medium text-xs">
                  {new Date(sceneData.created_at).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No active scene</p>
        )}
      </div>

      {/* Objects List */}
      <div className="flex-1 overflow-y-auto p-4 border-b border-gray-700">
        <h3 className="text-md font-semibold mb-3">Objects</h3>

        {sceneData?.objects && sceneData.objects.length > 0 ? (
          <div className="space-y-2">
            {sceneData.objects.map((obj, index) => (
              <div
                key={obj.id || index}
                className="bg-gray-800 rounded-lg p-3 text-sm"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{obj.type || 'Object'}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">#{index + 1}</span>
                    <button
                      onClick={() => handleDeleteObject(index)}
                      disabled={deletingIndex === index}
                      className="text-xs px-2 py-1 bg-red-900/50 hover:bg-red-800 text-red-300 rounded transition-colors disabled:opacity-50"
                      title="Delete this object"
                    >
                      {deletingIndex === index ? '...' : '✕'}
                    </button>
                  </div>
                </div>

                {obj.material?.color && (
                  <div className="flex items-center space-x-2 mt-1">
                    <div
                      className="w-4 h-4 rounded border border-gray-600"
                      style={{ backgroundColor: obj.material.color }}
                    />
                    <span className="text-xs text-gray-400">
                      {obj.material.color}
                    </span>
                  </div>
                )}

                {obj.position && (
                  <div className="text-xs text-gray-400 mt-1">
                    Position: ({obj.position.map(p => p.toFixed(1)).join(', ')})
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No objects in scene</p>
        )}
      </div>

      {/* Command History */}
      <div className="p-4 max-h-64 overflow-y-auto">
        <h3 className="text-md font-semibold mb-3">Command History</h3>
        
        {commandHistory.length > 0 ? (
          <div className="space-y-2">
            {commandHistory.slice().reverse().map((cmd, index) => (
              <div
                key={index}
                className="bg-gray-800 rounded-lg p-2 text-sm"
              >
                <p className="text-white">{cmd.text}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(cmd.timestamp).toLocaleTimeString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">No commands yet</p>
        )}
      </div>

      {/* Status/Error */}
      {loading && (
        <div className="p-4 bg-blue-900/30 border-t border-blue-700">
          <p className="text-sm text-blue-300">Processing...</p>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-red-900/30 border-t border-red-700">
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}
    </div>
  );
};

export default InfoPanel;
