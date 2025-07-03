import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from './components/pages/LoginPage';
import RegisterPage from './components/pages/RegisterPage';
import QAndAPage from './components/pages/QAndAPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/q-and-a" element={<QAndAPage />} />
        {/* thêm các route khác */}
      </Routes>
    </BrowserRouter>
  )
}

export default App
