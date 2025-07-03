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
  const [loading, setLoading] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await loginUser(form);
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
      navigate("/q-and-a");
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-100 via-white to-blue-200 px-4">
      <div className="grid grid-cols-1 md:grid-cols-2 bg-white rounded-xl shadow-2xl overflow-hidden max-w-5xl w-full">
        {/* Slideshow */}
        <div className="hidden md:block">
          <img
            src={images[currentIndex]}
            alt={`Slide ${currentIndex + 1}`}
            className="object-cover w-full h-full transition-opacity duration-700 ease-in-out"
          />
        </div>

        {/* Form Section */}
        <div className="flex flex-col justify-center px-8 py-10">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-gray-800">Welcome back!</h2>
            <p className="text-sm text-gray-500 mt-1">Please sign in to continue</p>
          </div>

          {/* Error Message */}
          <div className={`h-10 mb-4 transition-all duration-300 ${error ? 'opacity-100' : 'opacity-0'}`}>
            <div className="text-sm bg-red-100 text-red-600 p-2 rounded-md">
              {error || "placeholder"}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="Email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                name="Email"
                id="Email"
                required
                placeholder="you@example.com"
                value={form.Email}
                onChange={handleChange}
                autoComplete="username"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label htmlFor="Password" className="block text-sm font-medium text-gray-700 mb-1">
                Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="Password"
                id="Password"
                required
                placeholder="••••••••"
                value={form.Password}
                onChange={handleChange}
                autoComplete="current-password"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div className="text-right text-sm">
              <a href="#" className="text-blue-500 hover:underline">
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center items-center gap-2 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition duration-200 ${
                loading ? "opacity-75 cursor-not-allowed" : ""
              }`}
            >
              {loading && (
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  />
                </svg>
              )}
              {loading ? "Logging in..." : "Login"}
            </button>

            <p className="text-center text-sm text-gray-600">
              Don't have an account?{" "}
              <Link to="/register" className="text-blue-500 hover:underline font-medium">
                Sign up
              </Link>
            </p>
          </form>

          <div className="mt-6 text-center text-xs text-gray-400">
            © 2024 <strong>GeoSI</strong>. All Rights Reserved.{" "}
            <a href="#" className="text-blue-400 hover:underline">Terms</a> ·{" "}
            <a href="#" className="text-blue-400 hover:underline">Privacy</a>
          </div>
        </div>
      </div>
    </div>
  );
}
