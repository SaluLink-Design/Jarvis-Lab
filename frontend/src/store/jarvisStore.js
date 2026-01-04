import { create } from 'zustand';

export const useJarvisStore = create((set) => ({
  // Scene state
  contextId: null,
  sceneData: null,
  loading: false,
  error: null,

  // Command history
  commandHistory: [],

  // Actions
  setContextId: (id) => set({ contextId: id }),
  
  setSceneData: (data) => set({ sceneData: data }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  addCommand: (command) => set((state) => ({
    commandHistory: [...state.commandHistory, {
      text: command,
      timestamp: new Date().toISOString()
    }]
  })),
  
  clearScene: () => set({
    contextId: null,
    sceneData: null,
    error: null
  }),
  
  updateSceneFromResponse: (response) => {
    // Check if response has error status
    if (response.status === 'error') {
      set({
        loading: false,
        error: response.message || 'An error occurred processing your request'
      });
    } else {
      set({
        contextId: response.context_id,
        sceneData: response.scene,
        loading: false,
        error: null
      });
    }
  },

  removeObject: (index) => set((state) => ({
    sceneData: {
      ...state.sceneData,
      objects: state.sceneData?.objects?.filter((_, i) => i !== index) || []
    }
  }))
}));
