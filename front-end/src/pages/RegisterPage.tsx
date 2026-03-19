import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { TrainFront } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function RegisterPage() {
  const { colors, theme } = useTheme();
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await register(email, password);
      navigate("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`min-h-screen flex items-center justify-center ${colors.bg} px-4`}>
      <div className={`w-full max-w-sm ${colors.inputBg} rounded-2xl border ${colors.inputBorder} p-8 ${theme === "light" ? "shadow-lg" : ""}`}>
        <div className="text-center mb-6">
          <span className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-[#e87722]/10 mb-3">
            <TrainFront size={24} className="text-[#e87722]" />
          </span>
          <h1 className={`text-2xl font-semibold ${colors.text} tracking-tight`}>
            Create Account
          </h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={`w-full px-4 py-3 rounded-lg bg-transparent border ${colors.inputBorder} ${colors.text} focus:outline-none focus:ring-2 focus:ring-[#e87722]/40 focus:border-[#e87722]/50`}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className={`w-full px-4 py-3 rounded-lg bg-transparent border ${colors.inputBorder} ${colors.text} focus:outline-none focus:ring-2 focus:ring-[#e87722]/40 focus:border-[#e87722]/50`}
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
            className={`w-full px-4 py-3 rounded-lg bg-transparent border ${colors.inputBorder} ${colors.text} focus:outline-none focus:ring-2 focus:ring-[#e87722]/40 focus:border-[#e87722]/50`}
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-[#e87722] hover:bg-[#d06a1a] text-white font-medium transition-colors disabled:opacity-50 cursor-pointer border-none"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className={`mt-4 text-sm text-center ${colors.textMuted}`}>
          Already have an account?{" "}
          <Link to="/login" className="text-[#e87722] hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
