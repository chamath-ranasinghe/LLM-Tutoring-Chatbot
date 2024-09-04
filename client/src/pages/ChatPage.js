import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import Header from '../components/Header';
import Footer from '../components/Footer';

function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatId, setChatId] = useState('abc1');  // Initial chatId state

  return (
    <div className="flex flex-col h-screen">
      <Header className="h-16" /> {/* Adjust height to match Header */}
      <div className="flex flex-grow overflow-hidden">
        <Sidebar className="fixed top-16 left-0 bottom-0 w-64" isOpen={isSidebarOpen} toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} chatId={chatId}  setChatId={setChatId} />
        <div className="flex flex-col flex-grow ml-10">
          <MainContent isSidebarOpen={isSidebarOpen} chatId={chatId} />
        </div>
      </div>
      <Footer className="h-16" /> {/* Adjust height to match Footer */}
    </div>
  );
}

export default ChatPage;