import { useNavigate, Navigate } from "react-router-dom";

export default function QAndAPage() {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  // Nếu chưa đăng nhập → chuyển hướng về /login
  if (!token) {
    return <Navigate to="/login" />;
  }

  // Hàm xử lý logout
  const handleLogout = () => {
    localStorage.removeItem("token"); // Xóa token
    navigate("/login"); // Điều hướng về trang login
  };

  return (
    <div>
      <h2>Q And A Page</h2>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

