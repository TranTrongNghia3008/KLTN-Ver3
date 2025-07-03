import { useEffect, useState } from "react";
import {
  fetchConversations,
  createConversation,
  deleteConversation,
  renameConversation,
} from "./services/qnaService";
import { FiEdit2, FiTrash2, FiCheck, FiX } from "react-icons/fi";
import { RiChatNewFill } from "react-icons/ri";
import Modal from "./ui/Modal";

export default function Sidebar({
  userId,
  selectedConversationId,
  setSelectedConversationId,
  setShowSidebar,
}) {
  const [conversations, setConversations] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState(null);

  const loadConversations = async () => {
    try {
      const data = await fetchConversations(userId);
      setConversations(data);
      if (!selectedConversationId) {
        setSelectedConversationId(data.length > 0 ? data[0]._id : null);
      }
      console.log("Loaded conversations:", data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [userId]);

  const handleCreate = async () => {
    const newConv = await createConversation(userId);
    setSelectedConversationId(newConv._id);
    loadConversations();
  };

  const handleDelete = async () => {
    await deleteConversation(conversationToDelete);
    try {
      const data = await fetchConversations(userId);
      setConversations(data);
      if (selectedConversationId === conversationToDelete) {
        setSelectedConversationId(data.length > 0 ? data[0]._id : null);
      }
      console.log("Loaded conversations:", data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const handleRename = (id, currentTitle) => {
    setEditingId(id);
    setEditingTitle(currentTitle);
  };

  const handleRenameSubmit = async (id) => {
    if (editingTitle.trim()) {
      await renameConversation(id, editingTitle.trim());
      setEditingId(null);
      setEditingTitle("");
      loadConversations();
    }
  };

  return (
    <div className="absolute z-20 top-0 left-0 w-72 p-4 bg-white border-r border-gray-200 shadow-lg h-full overflow-y-auto rounded">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
        <button
          onClick={() => setShowSidebar(false)}
          className="p-2 hover:bg-gray-100 rounded-full transition"
          title="Close Sidebar"
        >
          <FiX size={20} />
        </button>
      </div>

      {/* New Conversation */}
      <button
        onClick={handleCreate}
        className="w-full mb-4 px-3 py-2 border border-gray-300 text-gray-700 rounded-md flex items-center justify-center gap-2 hover:bg-gray-100 transition-colors font-medium shadow-sm"
      >
        <RiChatNewFill size={18} className="text-gray-500" />
        New Conversation
      </button>

      {/* Conversations List */}
      <ul className="space-y-2 overflow-y-auto max-h-[calc(100vh-200px)] pr-1">
        {conversations.map((conv) => {
          const isEditing = editingId === conv._id;
          const isSelected = selectedConversationId === conv._id;

          return (
            <li
              key={conv._id}
              className={`p-2 rounded-md cursor-pointer border transition ${
                isSelected
                  ? "bg-blue-100 border-blue-400"
                  : "hover:bg-gray-100 border-gray-200"
              }`}
              onClick={() => setSelectedConversationId(conv._id)}
            >
              <div className="flex justify-between items-center">
                {/* Title or input */}
                <div className="w-3/4 truncate text-sm font-medium text-gray-800">
                  {isEditing ? (
                    <input
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleRenameSubmit(conv._id);
                      }}
                      className="w-full px-2 py-1 border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                      autoFocus
                    />
                  ) : (
                    <span>{conv.Title || "Untitled"}</span>
                  )}
                </div>

                {/* Action buttons */}
                <div className="flex space-x-2 text-gray-500 text-base">
                  {isEditing ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRenameSubmit(conv._id);
                      }}
                      className="hover:text-green-600"
                      title="Save"
                    >
                      <FiCheck />
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRename(conv._id, conv.Title || "");
                      }}
                      className="hover:text-blue-600"
                      title="Rename"
                    >
                      <FiEdit2 />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setConversationToDelete(conv._id);
                      setShowConfirm(true);
                    }}
                    className="hover:text-red-600"
                    title="Delete"
                  >
                    <FiTrash2 />
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>

      {/* Modal Confirm Delete */}
      {showConfirm && (
        <Modal
          title="Confirm Delete"
          onClose={() => {
            setShowConfirm(false);
            setConversationToDelete(null);
          }}
        >
          <p className="text-sm text-gray-700 mb-4">
            Are you sure you want to delete this conversation?
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => {
                setShowConfirm(false);
                setConversationToDelete(null);
              }}
              className="px-4 py-1 text-sm rounded bg-gray-100 hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                handleDelete();
                setShowConfirm(false);
                setConversationToDelete(null);
              }}
              className="px-4 py-1 text-sm rounded bg-red-600 text-white hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
