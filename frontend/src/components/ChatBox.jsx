import { useEffect, useState } from "react";
import DOMPurify from "dompurify";
import { fetchMessages, sendMessage, updateLocationInformations } from "./services/qnaService";
import { FiSend } from "react-icons/fi";
import userDefaultImage from "/images/default-user-image.png";
import { formatTextToHtml } from "./utils/formatTextToHtml";


DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A') {
    node.setAttribute('target', '_blank');
    node.setAttribute('rel', 'noopener noreferrer');
  }
});

export default function ChatBox({
  conversationId, setConversationId,
  input, setInput,
  isCrawl, setIsCrawl,
  linkSpecific, setLinkSpecific,
  locations, user, setLocations,
  setShowEditedHistory,
  setEditedHistory
}) {
  const [messages, setMessages] = useState([]);
  const [topK, setTopK] = useState(1);
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (conversationId) await loadMessages();
      setTopK(1);
    };
    fetchData();
  }, [conversationId]);

  const loadMessages = async () => {
    try {
      const data = await fetchMessages(conversationId);
      setMessages(data);
      if (data.length > 0) {
        setIsCrawl(false);
      } else {
        setIsCrawl(true);
        setLinkSpecific("");
        setInput("");
        setLocations([]);
      }
    } catch (err) {
      console.error("Error loading messages:", err);
    } 
  };

  function mergeLocations(existing, incoming) {
    const map = new Map();
    existing.forEach(loc => {
      const key = `${loc.administrative_area}-${loc.country}-${loc.continent}-${loc.lat}-${loc.lon}`;
      map.set(key, { ...loc });
    });
    incoming.forEach(newLoc => {
      const key = `${newLoc.administrative_area}-${newLoc.country}-${newLoc.continent}-${newLoc.lat}-${newLoc.lon}`;
      if (map.has(key)) {
        const exist = map.get(key);
        exist.links = Array.from(new Set([...exist.links, ...newLoc.links]));
        exist.summaries = Array.from(new Set([...exist.summaries, ...newLoc.summaries]));
      } else {
        map.set(key, { ...newLoc });
      }
    });
    return Array.from(map.values());
  }

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = `User: ${input}`;
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsThinking(true);

    let text = input.trim();
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    let extractedUrl = "";
    if (urlRegex.test(text)) {
      extractedUrl = text.match(urlRegex)[0];
      setLinkSpecific(extractedUrl);
      text = text.replace(urlRegex, "").trim();
    }

    try {
      const res = await sendMessage(conversationId, text, isCrawl, extractedUrl, linkSpecific, topK);
      await loadMessages();

      if (locations && res.locations && res.locations.length > 0) {
        const merged = mergeLocations(locations, res.locations || []);
        await updateLocationInformations(conversationId, merged);
      }
      setConversationId(prev => prev);
      setIsCrawl(false);
    } catch (err) {
      console.error("Error sending message:", err);
    } finally {
      setIsThinking(false);
    }
  };

  

  const showEditHistory = (message) => {
    setEditedHistory(message);
    setShowEditedHistory(true);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden max-h-[calc(100vh-110px)]">
      <div id="chatBox" className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => {
          if (msg.startsWith("User:")) {
            return (
              <div key={idx} className="flex justify-end items-start space-x-2">
                <div className="max-w-[70%] p-3 bg-blue-500 text-white rounded-lg rounded-tr-none shadow">
                  <div className="whitespace-pre-wrap break-words">
                    {msg.replace("User: ", "")}
                  </div>
                </div>
                <img
                  src={user?.Avatar || userDefaultImage}
                  alt="User"
                  className="w-8 h-8 rounded-full object-cover"
                />
              </div>
            );
          } else if (msg.startsWith("System:")) {
            const match = msg.match(/NewMessage:(.*)/s);
            const formatted = match ? formatTextToHtml(match[1].trim()) : "";
            return (
              <div key={idx} className="flex items-start space-x-2">
                <img
                  src="/images/chatbot.png"
                  alt="Bot"
                  className="w-8 h-8 rounded-full object-cover"
                />
                <div className="max-w-[75%] p-3 bg-gray-100 rounded-lg rounded-tl-none shadow">
                  <div
                    className="whitespace-pre-wrap break-words"
                    dangerouslySetInnerHTML={{ __html: formatted }}
                  />
                  <div className="text-xs text-blue-500 mt-1 cursor-pointer" onClick={() => showEditHistory(msg)}>
                    Edited
                  </div>
                </div>
              </div>
            );
          } else if (msg.startsWith("Ref:") && msg.length > 6) {
            const sanitized = DOMPurify.sanitize(msg.replace("Ref: ", "").trim());
            return (
              <div key={idx} className="flex items-start space-x-2">
                <img
                  src="/images/chatbot.png"
                  alt="Bot"
                  className="w-8 h-8 rounded-full object-cover"
                />
                <div className="max-w-[75%] p-3 bg-gray-50 rounded-lg rounded-tl-none shadow">
                  <strong className="block text-sm text-gray-500 mb-1">Reference source:</strong>
                  <div
                    className="whitespace-pre-wrap break-words text-sm"
                    dangerouslySetInnerHTML={{ __html: sanitized }}
                  />
                </div>
              </div>
            );
          } else {
            return null;
          }
        })}
        {isThinking && (
          <div className="flex items-start space-x-2 animate-pulse">
            <img src="/images/chatbot.png" alt="Bot" className="w-8 h-8 rounded-full" />
            <div className="bg-gray-200 px-4 py-2 rounded-lg text-gray-600">Chatbot is thinking...</div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-300 flex items-center gap-2 left-0 bottom-0">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Enter your message..."
          className="flex-1 border border-gray-300 rounded px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          className="flex items-center gap-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded shadow h-full"
          onClick={handleSend}
        >
          <FiSend size={16} />
        </button>
      </div>
    </div>
  );
}
