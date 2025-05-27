import { useEffect, useState } from "react";
import { loginUser } from "../services/authService";
import { useNavigate, Link } from "react-router-dom";

const images = [
  "/images/login-image-1.png",
  "/images/login-image-2.webp",
  "/images/login-image-3.png",
];

export default function LoginPage() {
  const [form, setForm] = useState({ Email: "", Password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 3000); // 3000ms = 3s

    return () => clearInterval(interval); // cleanup khi component unmount
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await loginUser(form);
      console.log("Login successful:", res);
      localStorage.setItem("token", res.access_token);
      navigate("/q-and-a");
    } catch (err) {
      setError(err.message || "Login failed");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10 bg-white rounded-lg shadow-lg p-6 w-full max-w-5xl">
        {/* Slideshow */}
        <div className="hidden md:block">
            <img
                src={images[currentIndex]}
                alt={`Slide ${currentIndex + 1}`}
                className="rounded-lg shadow transition-opacity duration-500 object-cover w-full h-full"
            />
        </div>

        {/* Form */}
        <div className="flex flex-col justify-center">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-semibold text-gray-800">Welcome back!</h3>
            <p className="text-sm text-gray-500">Sign in with your email</p>
          </div>

          <div className="h-10 mb-4">
            <div className={`text-sm p-2 rounded transition-all duration-300 ${
              error ? "bg-red-100 text-red-600" : "invisible"
              }`}
            >
              {error || "placeholder"}
            </div>
          </div>


          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="Email" className="block text-sm font-medium text-gray-700">
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                name="Email"
                id="Email"
                required
                placeholder="Email Address"
                value={form.Email}
                onChange={handleChange}
                autoComplete="username"
                className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="Password" className="block text-sm font-medium text-gray-700">
                Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="Password"
                id="Password"
                required
                placeholder="Password"
                value={form.Password}
                onChange={handleChange}
                autoComplete="current-password"
                className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="text-end text-sm">
              <a href="#" className="text-blue-500 hover:underline">Forgot my password</a>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md"
            >
              Login
            </button>

            <p className="text-center text-sm">
              Don’t have an account?{" "}
              <Link to="/register" className="text-blue-500 hover:underline">
                Sign up
              </Link>
            </p>
          </form>

          <div className="mt-6 text-center text-xs text-gray-400">
            © 2024 <strong>GeoSI</strong>. All Rights Reserved.{" "}
            <a href="#" className="text-blue-400 hover:underline">Terms of Use</a> and{" "}
            <a href="#" className="text-blue-400 hover:underline">Privacy Policy</a>
          </div>
        </div>
      </div>
    </div>
  );
}
