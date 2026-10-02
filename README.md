# NASA Space Atlas

A Python + Flask web app that displays a celestial map with planets, moons, dwarf planets, asteroids, comets, and major stellar objects. Each object can be selected to show details such as coordinates, distance from Earth, composition, and habitability indicators.

## Features

- Fullscreen interactive 3D-style space map
- Solar-system-focused object catalog
- Click-to-inspect details panel
- NASA feed support with safe demo fallback
- Responsive layout for local or hosted use

## Run locally

```powershell
cd "C:\Users\user\Desktop\SPACEPROJECT"
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" app.py
```

Then open http://localhost:5000/

## Add your NASA key

Create a file named `.env` in the project root with:

```env
NASA_API_KEY=your_key_here
```

If no key is set, the app still runs in demo mode.

## Deploy to GitHub and public hosting

1. Install Git from https://git-scm.com/downloads
2. Open a terminal in the project folder
3. Initialize Git:

```powershell
git init
git add .
git commit -m "Initial commit"
```

4. Create a new empty GitHub repository on github.com
5. Link it:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

6. Deploy the project to a public host such as Render or Railway
7. Set environment variables in the hosting dashboard:
   - `NASA_API_KEY` = your NASA API key (optional)
   - `FLASK_DEBUG` = `0`
   - `PORT` = provided by hosting

## Production web server

This project includes `gunicorn` for hosting on Render/Railway. The app is also safe for production by reading environment variables for the host and port.

## Files to ignore

`.env`, `.venv`, `__pycache__`, and generated files are intentionally excluded from Git.
