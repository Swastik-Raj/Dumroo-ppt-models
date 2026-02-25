# SlideGen.ai - AI PowerPoint Generator

An AI-powered application that generates professional PowerPoint presentations from a topic using OpenAI's API.

## Features

- Web-based UI for easy presentation generation
- Preview slides before downloading
- Edit slide titles and content in the preview
- Choose custom number of slides (3-20)
- Multiple professional themes available
- AI-generated content and diagrams
- Automatic image sourcing from Unsplash
- JSON file-based storage with automatic cleanup

## Setup

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```bash
OPENAI_API_KEY=your_api_key_here
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend Server

```bash
python api_server.py
```

The backend API will run on `http://localhost:8000`

### Start the Frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:5173`

## Using the Application

1. Open your browser to `http://localhost:5173`
2. Enter your presentation topic
3. Choose the number of slides (default: 5)
4. Select a theme from the dropdown
5. Click "Generate Presentation"
6. Preview the generated slides
7. Edit any slide by clicking the "Edit Slide" button
8. Navigate between slides using the sidebar or Previous/Next buttons
9. Click "Download Presentation" to get your `.pptx` file

## Available Themes

- Education Light
- Dark Tech
- Corporate Blue
- Minimal

## Command Line Usage

You can also generate presentations from the command line:

```bash
python generate.py "Your Topic" --slides 5 --theme "Education Light"
```
