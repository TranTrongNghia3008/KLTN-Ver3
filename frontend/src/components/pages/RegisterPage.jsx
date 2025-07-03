import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import { BsCheckCircleFill } from "react-icons/bs";

export default function RegisterPage() {
  const [form, setForm] = useState({ Name: "", Email: "", Password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(form);
      setSuccess("Registration successful!");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-tr from-blue-100 via-white to-blue-200 px-4">
      <div className="w-full max-w-md bg-white shadow-xl rounded-xl p-8">
        <div className="mb-6 text-center">
          <h3 className="text-3xl font-bold mb-2 text-gray-800">Start Your Conversation</h3>
          <div className="flex flex-wrap justify-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center gap-1 mb-1">
              <BsCheckCircleFill className="text-green-500" />
              <span>100% Free Forever</span>
            </div>
            <div className="flex items-center gap-1 mb-1">
              <BsCheckCircleFill className="text-green-500" />
              <span>No Credit Card Required</span>
            </div>
          </div>
        </div>

        {/* Message (fixed height) */}
        <div className="h-10 mb-4 text-sm">
          {error && (
            <div className="bg-red-100 text-red-600 p-2 rounded">{error}</div>
          )}
          {!error && success && (
            <div className="bg-green-100 text-green-600 p-2 rounded">{success}</div>
          )}
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          <div>
            <label htmlFor="name" className="block mb-1 font-medium text-gray-700">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="Name"
              type="text"
              placeholder="Your full name"
              value={form.Name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="email" className="block mb-1 font-medium text-gray-700">
              Email Address <span className="text-red-500">*</span>
            </label>
            <input
              id="email"
              name="Email"
              type="email"
              placeholder="you@example.com"
              value={form.Email}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block mb-1 font-medium text-gray-700">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              id="password"
              name="Password"
              type="password"
              placeholder="••••••••"
              value={form.Password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full flex justify-center items-center gap-2 bg-blue-600 text-white py-2 px-4 rounded-md transition hover:bg-blue-700 ${
              loading ? "opacity-70 cursor-not-allowed" : ""
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
            {loading ? "Creating account..." : "Create free account"}
          </button>

          <p className="text-center text-sm text-gray-600">
            Already have an account?{" "}
            <a href="/login" className="text-blue-600 underline font-medium">
              Login
            </a>
          </p>

          <p className="text-center text-xs text-gray-400 mt-2">
            By creating an account, you agree to <strong>GeoSI</strong>
          </p>
          <p className="text-center text-xs text-gray-400">
            <a href="#" className="text-blue-500 hover:underline">
              Terms of Use
            </a>{" "}
            and{" "}
            <a href="#" className="text-blue-500 hover:underline">
              Privacy Policy
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
