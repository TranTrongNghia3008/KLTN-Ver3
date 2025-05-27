import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import { BsCheckCircleFill } from "react-icons/bs";

export default function RegisterPage() {
  const [form, setForm] = useState({ Name: "", Email: "", Password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      await registerUser(form);
      setSuccess("Registration successful!");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.message || "Registration failed");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white shadow-md rounded-lg p-6 w-full">
      <div className="mb-6 text-center">
        <h3 className="text-2xl font-bold mb-2">Start Your Conversation</h3>
        <div className="flex justify-center space-x-4 text-sm text-gray-700">
          <div className="flex items-center gap-1">
            <BsCheckCircleFill className="text-green-500" />
            <span>100% Free Forever</span>
          </div>
          <div className="flex items-center gap-1">
            <BsCheckCircleFill className="text-green-500" />
            <span>No Credit Card Required</span>
          </div>
        </div>
      </div>

      {/* Error / Success message (chiều cao cố định) */}
      <div className="h-10 mb-4">
        {error && (
          <div className="bg-red-100 text-red-600 text-sm p-2 rounded">{error}</div>
        )}
        {!error && success && (
          <div className="bg-green-100 text-green-600 text-sm p-2 rounded">{success}</div>
        )}
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-4">
          <label htmlFor="name" className="block mb-1 font-medium">
            Name <span className="text-red-500">*</span>
          </label>
          <input
            id="name"
            name="Name"
            type="text"
            placeholder="Name"
            value={form.Name}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="email" className="block mb-1 font-medium">
            Email Address <span className="text-red-500">*</span>
          </label>
          <input
            id="email"
            name="Email"
            type="email"
            placeholder="Email Address"
            value={form.Email}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="password" className="block mb-1 font-medium">
            Password <span className="text-red-500">*</span>
          </label>
          <input
            id="password"
            name="Password"
            type="password"
            placeholder="Password"
            value={form.Password}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded mb-3"
        >
          Create free account
        </button>

        <p className="text-center text-sm">
          Do you have an account?{" "}
          <a href="/login" className="text-blue-600 underline">
            Login
          </a>
        </p>

        <p className="text-center text-xs mt-2">
          By creating an account, you agree to <strong>GeoSI</strong>
        </p>
        <p className="text-center text-xs">
          <a href="#" className="text-blue-600 underline">
            Terms of Use
          </a>{" "}
          and{" "}
          <a href="#" className="text-blue-600 underline">
            Privacy Policy
          </a>
        </p>
      </form>
    </div>
  );
}
