import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: ${({ theme }) => theme.text};
`;

const Features = styled.ul`
  margin-bottom: 36px;
  font-size: 1.1rem;
  color: ${({ theme }) => theme.text};
  list-style: disc inside;
  opacity: 0.92;
`;

const ActionButton = styled.button`
  font-size: 1.3rem;
  font-weight: 600;
  padding: 18px 44px;
  margin: 10px 0;
  border-radius: 16px;
  border: none;
  background: linear-gradient(90deg,#6366f1 0%,#60a5fa 100%);
  color: #fff;
  box-shadow: 0 4px 32px rgba(80,80,120,0.18);
  cursor: pointer;
  transition: background 0.18s, transform 0.18s;
  &:hover {
    background: linear-gradient(90deg,#60a5fa 0%,#6366f1 100%);
    transform: translateY(-2px) scale(1.03);
  }
`;

interface DashboardProps {
  onStartMeeting: () => void;
  onOpenMiniTab: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onStartMeeting, onOpenMiniTab }) => (
  <DashboardContainer>
    <Title>Clariimeet</Title>
    <Features>
      <li>🎤 Real-time transcription & AI summaries</li>
      <li>🤖 AI assistant chatbot for clarification</li>
      <li>📝 Smart categorized note-taking</li>
      <li>🕵️ Stealth mode & floating overlays</li>
      <li>🌐 Multilingual support</li>
    </Features>
    <ActionButton onClick={onStartMeeting}>Start Meeting</ActionButton>
    <ActionButton onClick={onOpenMiniTab}>Open MiniTab</ActionButton>
  </DashboardContainer>
);

export default Dashboard;
