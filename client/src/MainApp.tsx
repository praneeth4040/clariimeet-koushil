import React, { useState } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import Sidebar from './components/Sidebar.tsx';
import Dashboard from './components/Dashboard.tsx';
import MiniTab from './components/MiniTab.tsx';
import { showOverlay } from './utils/overlay.ts';
import ChatOverlay from './components/overlays/ChatOverlay.tsx';
import SummaryOverlay from './components/overlays/SummaryOverlay.tsx';
import NotesOverlay from './components/overlays/NotesOverlay.tsx';
import { darkTheme, lightTheme, GlobalStyle } from './styles/themeNew.ts';

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
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [showChat, setShowChat] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [miniTabOpen, setMiniTabOpen] = useState(false);

  return (
    <ThemeProvider theme={theme === 'dark' ? darkTheme : lightTheme}>
      <GlobalStyle />
      <AppContainer>
        <Sidebar theme={theme} setTheme={setTheme} />
        <Dashboard
          onStartMeeting={() => setMiniTabOpen(true)}
        />
        {miniTabOpen && (
          <MiniTab
            onChat={() => setShowChat((v) => !v)}
            onSummary={() => setShowSummary((v) => !v)}
            onNotes={() => setShowNotes((v) => !v)}
            onClose={() => setMiniTabOpen(false)}
            showChat={showChat}
            showSummary={showSummary}
            showNotes={showNotes}
          />
        )}
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
