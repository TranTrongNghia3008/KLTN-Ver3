import { useEffect, useState } from 'react';
import Header from '../Header';
import Sidebar from '../Sidebar';
import ChatBox from '../ChatBox';
import MapView from '../MapView';
import { Navigate, useNavigate } from 'react-router-dom';
import { FiMenu, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import EditedHistory from '../EditedHistory';
import { fetchConversations } from '../services/qnaService';

export default function QAndAPage() {
  const user = JSON.parse(localStorage.getItem("user")) || {};
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  const [currentTab, setCurrentTab] = useState('Q&A');
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [input, setInput] = useState("");
  const [isCrawl, setIsCrawl] = useState(true);
  const [linkSpecific, setLinkSpecific] = useState("");
  const [locations, setLocations] = useState([]);

  const [showSidebar, setShowSidebar] = useState(false);
  const [showChatBox, setShowChatBox] = useState(true);
  const [showEditedHistory, setShowEditedHistory] = useState(false);
  const [editedHistory, setEditedHistory] = useState([]);

  useEffect(() => {
    loadConversations()
  }, []);

  const loadConversations = async () => {
      try {
        const data = await fetchConversations(user._id);
        if (!selectedConversationId) {
          setSelectedConversationId(data.length > 0 ? data[0]._id : null);
        }
        
      } catch (err) {
        console.error("Failed to load conversations:", err);
      }
    };

  if (!token) {
    return <Navigate to="/login" />;
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const sendMessageFromLocation = (query, link) => {
    console.log("Sending message from location:", query, link);
    setIsCrawl(true);
    setLinkSpecific(link);
    setInput(query);
  };

  return (
    <div className="flex flex-col h-svh">
      <Header currentTab={currentTab} setCurrentTab={setCurrentTab} user={user} onLogout={handleLogout} />
      <div className="flex flex-1 relative">
        {currentTab === 'Q&A' && (
          <div className="flex flex-1 relative">

            {/* Sidebar (overlay) */}
            {showSidebar && (

                <Sidebar
                  userId={user._id}
                  selectedConversationId={selectedConversationId}
                  setSelectedConversationId={setSelectedConversationId}
                  setShowSidebar={setShowSidebar}
                />          

            )}

            {/* ChatBox Section */}
            {showChatBox && (
              <div className="w-1/3 flex flex-col border-r relative">
                {/* Chat Header + Toggle Sidebar */}
                <div className="flex items-center justify-between p-2 bg-gray-100 text-sm font-semibold border-b border-gray-300">
                  {!showSidebar && (
                    <button
                      onClick={() => setShowSidebar(true)}
                      className="p-1 hover:bg-gray-200 rounded"
                      title="Hiện Sidebar"
                    >
                      <FiMenu size={18} />
                    </button>
                  )}
                  <h3 className="text-xl">Q and A</h3>
                  {/* Nút ẩn ChatBox */}
                  <button
                    onClick={() => {
                      setShowChatBox(false)
                      setShowSidebar(false)
                    }}
                    className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full z-10"
                    title="Ẩn Chat"
                  >
                    <FiChevronLeft size={20} />
                  </button>
                </div>

                {/* Chat Content */}
                <ChatBox
                  conversationId={selectedConversationId}
                  setConversationId={setSelectedConversationId}
                  input={input}
                  setInput={setInput}
                  isCrawl={isCrawl}
                  setIsCrawl={setIsCrawl}
                  linkSpecific={linkSpecific}
                  setLinkSpecific={setLinkSpecific}
                  locations={locations}
                  user={user}
                  setLocations={setLocations}
                  setShowEditedHistory={setShowEditedHistory}
                  setEditedHistory={setEditedHistory}
                />

                
              </div>
            )}

            {/* Nút hiện ChatBox nếu đang ẩn */}
            {!showChatBox && (
              <button
                onClick={() => setShowChatBox(true)}
                className="absolute left-0 top-1/2 transform -translate-y-1/2 z-10 p-2 bg-gray-100 hover:bg-gray-200 rounded-r-full shadow"
                title="Hiện Chat"
              >
                <FiChevronRight size={20} />
              </button>
            )}

            {/* Map View luôn chiếm phần còn lại */}
            <div className="flex-1">
              {showEditedHistory ? (
                <EditedHistory
                  message={editedHistory}
                  setShowEditedHistory={setShowEditedHistory}
                />
              ) : (
                <div className="relative h-full">
                  {/* Label “Interactive Map” */}
                  <div className="absolute top-3 left-3 bg-white/80 text-gray-700 text-sm font-medium px-3 py-1 rounded shadow z-10">
                    Interactive Map
                  </div>

                  {/* Bản đồ */}
                  <MapView
                    conversationId={selectedConversationId}
                    onSendMessageFromLocation={sendMessageFromLocation}
                    setLocations={setLocations}
                  />
                </div>
              )}
            </div>

          </div>
        )}

        {currentTab !== 'Q&A' && (
          <div className="flex items-center justify-center h-full text-gray-400 text-xl">
            Chức năng "{currentTab}" đang được phát triển...
          </div>
        )}
      </div>
    </div>
  );
}
