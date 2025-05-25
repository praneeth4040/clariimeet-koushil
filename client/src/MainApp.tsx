import React, { useState } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import Sidebar from './components/Sidebar.tsx';
import Dashboard from './components/Dashboard.tsx';
import ChatOverlay from './components/overlays/ChatOverlay.tsx';
import SummaryOverlay from './components/overlays/SummaryOverlay.tsx';
import NotesOverlay from './components/overlays/NotesOverlay.tsx';
import { darkTheme, lightTheme, GlobalStyle } from './styles/themeNew.ts';

// Main layout containers
const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background: ${({ theme }) => theme.background};
`;

const OverlayContainer = styled.div`
  position: fixed;
  z-index: 1000;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
`;

function MainApp() {
  // Theme state
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  // Overlay states
  const [showChat, setShowChat] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  // MiniTab state
  const [miniTabOpen, setMiniTabOpen] = useState(false);

  return (
    <ThemeProvider theme={theme === 'dark' ? darkTheme : lightTheme}>
      <GlobalStyle />
      <AppContainer>
        {/* Sidebar for navigation and theme switch */}
        <Sidebar theme={theme} setTheme={setTheme} />
        {/* Dashboard with Start Meeting button */}
        <Dashboard
          onStartMeeting={() => {
            if (window.electron?.ipcRenderer) {
              window.electron.ipcRenderer.send('show-overlay');
            }
          }}
        />
        {/* MiniTab is now only in overlay window, not in main window */}
        {/* Overlays for Chat, Summary, Notes */}
        <OverlayContainer>
          {showChat && <ChatOverlay onClose={() => setShowChat(false)} />}
          {showSummary && <SummaryOverlay onClose={() => setShowSummary(false)} />}
          {showNotes && <NotesOverlay onClose={() => setShowNotes(false)} />}
        </OverlayContainer>
      </AppContainer>
    </ThemeProvider>
  );
}

export default MainApp;
