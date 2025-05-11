import React from 'react';
import styled from 'styled-components';

const OverlayPanel = styled.div`
  position: absolute;
  top: 80px;
  right: 120px;
  width: 340px;
  height: 420px;
  background: ${({ theme }) => theme.card};
  box-shadow: ${({ theme }) => theme.shadow};
  border-radius: 22px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  backdrop-filter: ${({ theme }) => theme.blur};
  opacity: 0.98;
  z-index: 1200;
  pointer-events: all;
`;
const CloseBtn = styled.button`
  align-self: flex-end;
  background: none;
  border: none;
  color: ${({ theme }) => theme.text};
  font-size: 1.3rem;
  cursor: pointer;
`;
const Title = styled.h3`
  margin: 0 0 8px 0;
  font-size: 1.2rem;
`;
const ChatBox = styled.div`
  flex: 1;
  background: ${({ theme }) => theme.sidebar};
  border-radius: 12px;
  margin: 10px 0;
  padding: 10px;
  overflow-y: auto;
`;
const Input = styled.input`
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  margin-top: 8px;
  font-size: 1rem;
  width: 100%;
  background: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
`;

interface ChatOverlayProps {
  onClose: () => void;
}

const ChatOverlay: React.FC<ChatOverlayProps> = ({ onClose }) => (
  <OverlayPanel>
    <CloseBtn onClick={onClose}>✖️</CloseBtn>
    <Title>AI Assistant Chat</Title>
    <ChatBox>
      <div style={{opacity:0.5}}>Chatbot coming soon...</div>
    </ChatBox>
    <Input placeholder="Ask for clarification..." disabled />
  </OverlayPanel>
);

export default ChatOverlay;
