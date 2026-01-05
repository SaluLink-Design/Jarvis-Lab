import { create } from 'zustand';

// Default welcome scene for initial load
const DEFAULT_SCENE = {
  scene_id: 'welcome',
  objects: [
    {
      id: 'welcome-cube',
      type: 'cube',
      geometry: {
        type: 'BoxGeometry',
        parameters: {
          width: 2,
          height: 2,
          depth: 2
        }
      },
      material: {
        type: 'MeshStandardMaterial',
        color: '#0ea5e9',
        metalness: 0.3,
        roughness: 0.7
      },
      position: [0, 1, 0],
      rotation: [0.5, 0.5, 0]
    },
    {
      id: 'welcome-sphere',
      type: 'sphere',
      geometry: {
        type: 'SphereGeometry',
        parameters: {
          radius: 1.5,
          widthSegments: 32,
          heightSegments: 32
        }
      },
      material: {
        type: 'MeshStandardMaterial',
        color: '#f59e0b',
        metalness: 0.2,
        roughness: 0.8
      },
      position: [-4, 2, -2],
      rotation: [0, 0, 0]
    },
    {
      id: 'welcome-cylinder',
      type: 'cylinder',
      geometry: {
        type: 'CylinderGeometry',
        parameters: {
          radiusTop: 1,
          radiusBottom: 1,
          height: 3,
          radialSegments: 32
        }
      },
      material: {
        type: 'MeshStandardMaterial',
        color: '#10b981',
        metalness: 0.3,
        roughness: 0.7
      },
      position: [4, 1.5, -2],
      rotation: [0, 0, 0]
    }
  ],
  environment: {},
  lighting: {},
  camera: {},
  created_at: new Date().toISOString()
};

export const useJarvisStore = create((set) => ({
  // Scene state
  contextId: 'welcome',
  sceneData: DEFAULT_SCENE,
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
    contextId: 'welcome',
    sceneData: DEFAULT_SCENE,
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
