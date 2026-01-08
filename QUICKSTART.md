# Jarvis - Quick Start Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API key (optional but recommended)
# Copy .env.example to .env and add your key
# OR set it as an environment variable
# See BACKEND_SETUP.md for detailed instructions

# Start the backend
python main.py
```

The backend will start on `http://localhost:8000`

**Note:** The OpenAI API key is **optional**. The system works perfectly without it using rule-based NLP. See [BACKEND_SETUP.md](./BACKEND_SETUP.md) for detailed setup instructions.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

## Usage

1. Open your browser to `http://localhost:5173`
2. You'll see the Jarvis interface with:
   - A 3D viewport in the center
   - An info panel on the right showing scene objects
   - A command panel at the bottom

### Try These Commands:

**Basic Objects:**
- "Create a red cube"
- "Add a blue sphere"
- "Make a yellow cylinder"

**Complex Scenes:**
- "Create a forest scene"
- "Build a city environment"
- "Make a studio setup"

**With Images:**
- Click the camera icon 📷
- Upload an image
- Type: "Create objects based on this image"
- Press Send

## Architecture Overview

```
Jarvis/
├── backend/               # Python FastAPI backend
│   ├── core/             # Orchestration engine (the "brain")
│   ├── nlp/              # Natural language processing
│   ├── cv/               # Computer vision
│   ├── generation/       # 3D content generation
│   └── api/              # REST API endpoints
│
└── frontend/             # React + Three.js frontend
    ├── src/
    │   ├── components/   # UI components
    │   ├── store/        # State management
    │   └── api/          # API client
    └── ...
```

## API Endpoints

- `POST /api/text` - Process text commands
- `POST /api/process` - Process multimodal input (text + image)
- `GET /api/scene/{id}` - Get scene data
- `GET /api/scenes` - List all scenes
- `DELETE /api/scene/{id}` - Delete a scene
- `GET /health` - Health check

## Features

✅ **Implemented:**
- Natural language command processing
- Basic 3D object generation (primitives)
- Scene environments (forest, city, studio, interior)
- Interactive 3D viewport with Three.js
- Image upload support
- Real-time scene updates

🚧 **Planned:**
- Advanced text-to-3D models (Shap-E, DreamFusion)
- Image-to-3D reconstruction
- Video analysis for animations
- Physics simulation
- Object manipulation via UI
- VR/AR support

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
cd backend
pip install -r requirements.txt
```

**Port 8000 already in use:**
```bash
# Change PORT in .env file
PORT=8001
```

### Frontend Issues

**"Cannot connect to API":**
- Ensure backend is running on port 8000
- Check browser console for CORS errors

**Three.js rendering issues:**
- Update your graphics drivers
- Try a different browser (Chrome recommended)

**npm install fails:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py  # Auto-reloads on changes
```

### Frontend Development

```bash
cd frontend
npm run dev  # Hot reload enabled
```

## Notes

- The current implementation uses simplified 3D generation (procedural primitives)
- For production-grade text-to-3D, integrate models like Shap-E or Magic3D
- OpenAI API key is optional but enables better natural language understanding
- Without an API key, the system uses rule-based NLP (still functional)

## Next Steps

1. **Add your OpenAI API key** for better NLP
2. **Explore the example commands** to see what Jarvis can do
3. **Experiment with image uploads** to see multimodal processing
4. **Check the research notebook** (Jarvis.ipynb) for advanced features roadmap

## Support

For issues or questions, refer to:
- Main README.md for detailed documentation
- Jarvis.ipynb for research and technical details
- API documentation at `http://localhost:8000/docs` (when backend is running)

