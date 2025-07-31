import { useState } from 'react';
import { FaUserCircle } from 'react-icons/fa';
import userDefaultImage from "/images/default-user-image.png";
import { FiUser, FiLogOut } from 'react-icons/fi'

export default function Header({ currentTab, setCurrentTab, user, onLogout }) {
  const tabs = ['Q&A', 'Cheapfake', 'Deepfake', 'Settings'];
  const [showDropdown, setShowDropdown] = useState(false);

  return (
    <header className="flex justify-between items-center px-4 py-2 bg-blue-100 border-b border-gray-300 shadow-sm">
      <div className="text-xl font-bold">
        <img src="/images/img-logo.webp" alt="Logo" className="inline-block w-8 h-8 mr-2" />
       GeoSI
      </div>
      <nav className="flex space-x-6">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`text-sm font-medium ${tab === currentTab ? 'text-blue-600' : 'text-gray-600'}`}
            onClick={() => setCurrentTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>
      <div className="relative">
          <img
            src={user?.Avatar || userDefaultImage}
            alt="User"
            className="w-8 h-8 rounded-full object-cover my-auto cursor-pointer"
            onClick={() => setShowDropdown(!showDropdown)}
          />
        {showDropdown && (
          <div className="absolute right-0 mt-2 w-56 bg-white border rounded-lg shadow-lg z-10">
            {/* User Info */}
            <div className="flex items-center gap-3 px-4 py-3 border-b">
              <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center text-lg font-semibold">
                {user?.Name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="text-sm font-medium text-gray-800">{user.Name}</div>
            </div>

            {/* Actions */}
            <button
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
              onClick={() => console.log('Go to profile')}
            >
              <FiUser size={16} />
              Profile
            </button>

            <button
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition"
              onClick={onLogout}
            >
              <FiLogOut size={16} />
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
