import React, { useState, useRef } from 'react';
import { useJarvisStore } from '../store/jarvisStore';
import jarvisApi from '../api/jarvisApi';

const CommandPanel = () => {
  const [command, setCommand] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const fileInputRef = useRef(null);
  
  const { contextId, loading, setLoading, setError, addCommand, updateSceneFromResponse } = useJarvisStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!command.trim() && !selectedImage) {
      return;
    }

    setLoading(true);
    addCommand(command);

    try {
      let response;

      if (selectedImage) {
        // Multimodal request with image
        const formData = new FormData();
        formData.append('text', command);
        if (contextId) formData.append('context_id', contextId);
        formData.append('image', selectedImage);

        response = await jarvisApi.processMultimodal(formData);
      } else {
        // Text-only request
        response = await jarvisApi.processText(command, contextId);
      }

      updateSceneFromResponse(response);
      setCommand('');
      setSelectedImage(null);
    } catch (error) {
      console.error('Error processing command:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to process command';
      setError(`Error: ${errorMsg}`);
      setLoading(false);
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const exampleCommands = [
    'Create a red cube',
    'Add a blue sphere',
    'Create a forest scene',
    'Make a yellow cylinder',
    'Add a green plane as ground'
  ];

  return (
    <div className="bg-gray-900 border-t border-gray-700 p-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Command Input */}
        <div className="flex space-x-2">
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Tell Jarvis what to create... (e.g., 'Create a red cube')"
            className="flex-1 bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 
                     focus:outline-none focus:border-jarvis-blue transition-colors"
            disabled={loading}
          />
          
          {/* Image Upload Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 
                     rounded-lg transition-colors"
            disabled={loading}
            title="Upload Image"
          >
            📷
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || (!command.trim() && !selectedImage)}
            className="px-6 py-3 bg-jarvis-blue hover:bg-blue-600 text-white rounded-lg 
                     font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Send'}
          </button>
        </div>

        {/* Selected Image Preview */}
        {selectedImage && (
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>📎 {selectedImage.name}</span>
            <button
              type="button"
              onClick={() => setSelectedImage(null)}
              className="text-red-400 hover:text-red-300"
            >
              Remove
            </button>
          </div>
        )}

        {/* Example Commands */}
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-400">Examples:</span>
          {exampleCommands.map((example, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setCommand(example)}
              className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 
                       rounded-full transition-colors"
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </form>
    </div>
  );
};

export default CommandPanel;
