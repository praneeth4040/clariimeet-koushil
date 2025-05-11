# Clariimeet Client

AI-Powered Desktop Meeting Assistant (Frontend)

## Overview
Clariimeet is a Windows desktop application that provides real-time meeting transcription, AI-generated summaries, contextual chatbot assistance, advanced note management, stealth mode, and multilingual support.

This `client` folder contains the Electron + React frontend.

## Tech Stack
- Electron.js
- React.js (with Typescript)
- styled-components
- Redux Toolkit

## Features
- Real-time transcription & AI summaries
- AI assistant chatbot for clarification
- Smart categorized note-taking
- Stealth mode & floating overlays
- Multilingual support

## Getting Started

### Install dependencies
```sh
npm install
```

### Run the app (development)
```sh
npm run start
```

### Build for production
```sh
npm run build
```

## Project Structure
- `public/` — Electron main process & static assets
- `src/` — React UI source code
- `src/components/` — Modular UI components
- `src/components/overlays/` — Floating overlay windows
- `src/styles/` — Theme & global styles

## Notes
- This is the frontend only. Backend/server code should be placed in the `../server` directory.
- All overlays and UI components are modular and ready for integration with AI and backend APIs.
