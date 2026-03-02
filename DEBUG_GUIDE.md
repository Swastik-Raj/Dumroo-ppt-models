# Debugging the Preview Issue

## What Was Fixed

1. **Backend (`app/main.py`)**:
   - Preview endpoint now extracts real slide data from the AI-generated PresentationSpec
   - Added detailed debug logging to trace the generation process
   - Returns actual slide titles, content, and keywords instead of placeholders

2. **Frontend (`frontend/src/App.tsx`)**:
   - Added console logging to see exactly what data is received from the API

## How to Debug

### Step 1: Restart the Python Server

The Python server needs to be restarted to load the updated code:

```bash
# Stop the current server (Ctrl+C if running)
# Then restart:
python3 api_server.py
```

Or if you have it running differently:
```bash
cd /tmp/cc-agent/63940075/project
python3 -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Check the Frontend is Updated

The frontend has been rebuilt. If you're using the Vite dev server, it should auto-reload.
If not, refresh your browser (Ctrl+Shift+R for hard refresh).

### Step 3: Test the API Directly

Run the test script to see the raw API response:

```bash
cd /tmp/cc-agent/63940075/project
./test_preview.sh
```

This will:
- Make a POST request to `/api/generate/preview`
- Pretty-print the JSON response
- Show you the first 50 lines

**What to look for:**
- `slides` array should contain real data
- Each slide should have meaningful `title` and `content`
- NOT generic "Slide 1", "Slide 2" placeholders

### Step 4: Check Python Server Logs

When you generate a preview, watch the Python server terminal for `[DEBUG]` messages:

```
[DEBUG] Generating preview for topic: Introduction to Python...
[DEBUG] Slide count: 5, Theme: Modern Minimal
[DEBUG] Generated spec with title: Introduction to Python Programming
[DEBUG] Number of slides in spec: 5
[DEBUG] Slide 1: Introduction to Python Programming (intro)
[DEBUG] Slide 2: Core Components (process)
[DEBUG] Slide 3: End-to-End Flow (flow)
[DEBUG] PPTX generated at: output/...
[DEBUG] Returning response with 5 slides
```

### Step 5: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Click "Generate Preview" in the app
4. Look for these console logs:

```
Preview data received: {presentation_id: "...", topic: "...", ...}
Number of slides: 5
First slide: {id: 1, type: "intro", title: "...", ...}
```

### Step 6: Check Network Tab

In Browser Dev Tools:
1. Go to Network tab
2. Click "Generate Preview"
3. Find the POST request to `/api/generate/preview`
4. Click on it
5. Check the **Response** tab

You should see JSON with real slide data.

## Common Issues and Solutions

### Issue 1: Still Seeing Placeholder Data

**Symptoms:**
- Slides titled "Slide 1", "Slide 2", etc.
- Content says "Generated content"

**Cause:** Python server not restarted with new code

**Solution:**
```bash
# Kill the old server
pkill -f "api_server.py"
# Or use Ctrl+C

# Start fresh
python3 api_server.py
```

### Issue 2: Using Mock Fallback Data

**Symptoms:**
- Slides have generic titles like "Core Components", "End-to-End Flow"
- Content doesn't match your input

**Cause:** No AI API key configured

**Solution:**
Add an API key to `.env`:
```bash
# For OpenAI
OPENAI_API_KEY=sk-...

# Or for Gemini
GEMINI_API_KEY=your-key-here
```

Then restart the server.

### Issue 3: Error 500 from API

**Symptoms:**
- Red error message in UI
- Status code 500 in Network tab

**Cause:** Python exception during generation

**Solution:**
Check the Python server terminal for the full stack trace. The error message will tell you what went wrong.

### Issue 4: CORS Error

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/generate/preview' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Cause:** Server not allowing requests from frontend

**Solution:**
The server already has CORS configured. This shouldn't happen unless:
- Server isn't running
- Wrong URL (check it's localhost:8000)

### Issue 5: Preview Shows Old Data

**Symptoms:**
- Frontend was updated but still showing old behavior

**Cause:** Browser cache or old build

**Solution:**
```bash
# Hard refresh the browser
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# Or rebuild frontend
cd frontend
npm run build
```

## What the Response Should Look Like

Here's an example of a CORRECT response:

```json
{
  "presentation_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Introduction to Python Programming",
  "theme": "Modern Minimal",
  "slides": [
    {
      "id": 1,
      "type": "intro",
      "title": "Introduction to Python Programming",
      "content": "Python is a high-level, interpreted programming language known for its simplicity and readability...",
      "keywords": ["Python", "programming", "introduction"],
      "image_url": null
    },
    {
      "id": 2,
      "type": "process",
      "title": "Why Learn Python?",
      "content": "Python is widely used in web development, data science, AI, automation...",
      "keywords": ["versatile", "popular", "easy to learn"],
      "image_url": null
    }
  ]
}
```

## What an INCORRECT Response Looks Like

This is what it looked like BEFORE the fix:

```json
{
  "presentation_id": "...",
  "topic": "Introduction to Python Programming",
  "theme": "Modern Minimal",
  "slides": [
    {
      "id": 1,
      "type": "intro",
      "title": "Slide 1",
      "content": "Generated content",
      "keywords": [],
      "image_url": null
    },
    {
      "id": 2,
      "type": "content",
      "title": "Slide 2",
      "content": "Generated content",
      "keywords": [],
      "image_url": null
    }
  ]
}
```

## Quick Checklist

- [ ] Python server restarted after code changes
- [ ] Browser refreshed (hard refresh)
- [ ] Check Python server logs for `[DEBUG]` messages
- [ ] Check browser console for `Preview data received:` log
- [ ] Check Network tab for actual API response
- [ ] Verify response has real titles, not "Slide 1", "Slide 2"
- [ ] If using mock data, consider adding API key for real AI generation

## Still Not Working?

If you've tried all the above and it's still broken:

1. **Check if the server is actually running:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"ok":true}
   ```

2. **Test with curl directly:**
   ```bash
   ./test_preview.sh
   ```

3. **Check the exact error:**
   - Python server terminal output
   - Browser console errors
   - Network tab response

4. **Verify the code changes were saved:**
   ```bash
   grep -n "DEBUG" app/main.py
   # Should show the debug print statements
   ```

Let me know what you see in the logs and I can help further!
