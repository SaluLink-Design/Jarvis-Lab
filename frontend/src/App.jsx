import React, { useState } from 'react';
import Scene3D from './components/Scene3D';
import CommandPanel from './components/CommandPanel';
import InfoPanel from './components/InfoPanel';
import { useJarvisStore } from './store/jarvisStore';

const App = () => {
  const { contextId, sceneData } = useJarvisStore();

  return (
    <div className="w-screen h-screen flex flex-col bg-jarvis-dark">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-jarvis-blue rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">J</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Jarvis</h1>
              <p className="text-sm text-gray-400">3D AI Assistant</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {contextId && contextId !== 'welcome' && (
              <div className="text-sm text-gray-400">
                Scene: <span className="text-jarvis-blue font-mono">{contextId.slice(0, 8)}</span>
              </div>
            )}
            {contextId === 'welcome' && (
              <div className="text-sm text-green-400 flex items-center space-x-1">
                <span className="inline-block w-2 h-2 bg-green-400 rounded-full"></span>
                <span>Welcome Scene</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* 3D Scene */}
        <div className="flex-1 relative">
          <Scene3D />
          
          {/* Overlay Controls */}
          <div className="absolute top-4 right-4 bg-gray-900/80 backdrop-blur-sm rounded-lg p-3 text-sm">
            <div className="text-gray-300">
              <div>Objects: {sceneData?.objects?.length || 0}</div>
              <div>Environment: {sceneData?.environment?.type || 'None'}</div>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="w-96 bg-gray-900 border-l border-gray-700 flex flex-col">
          <InfoPanel />
        </div>
      </div>

      {/* Command Panel at Bottom */}
      <CommandPanel />
    </div>
  );
};

export default App;
