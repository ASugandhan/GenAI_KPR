"use client";
import { useState } from "react";

export default function LoginPage() {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {
        if (loading) return;
        setError("");
        setLoading(true);
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 8000);
            const res = await fetch(`${apiBase}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
                signal: controller.signal,
            });
            clearTimeout(timeout);

            if (res.ok) {
                let data: any = null;
                try {
                    data = await res.json();
                } catch {
                    setError("Invalid login response from server");
                    return;
                }
                if (!data?.access_token) {
                    setError("Login response missing token");
                    return;
                }
                localStorage.setItem("token", data.access_token);
                // Hard redirect so user never gets stuck on /login.
                window.location.assign("/");
            } else {
                setError(`Login failed (${res.status})`);
            }
        } catch (err: any) {
            if (err?.name === "AbortError") {
                setError("Login timed out. Check backend on :8000");
            } else {
                setError("Failed to connect to authentication server");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center">
            <div className="bg-gray-900 border border-green-500 rounded-lg p-8 w-96 shadow-[0_0_20px_rgba(34,197,94,0.2)]">
                <h1 className="text-green-400 text-2xl font-bold mb-2">🛡️ ZeroTrust AI</h1>
                <p className="text-gray-400 text-sm mb-6">Secure Authentication Required</p>
                <div className="space-y-4">
                    <input
                        className="w-full bg-gray-800 text-white border border-gray-700 focus:border-green-500 outline-none rounded p-2 transition-all"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        className="w-full bg-gray-800 text-white border border-gray-700 focus:border-green-500 outline-none rounded p-2 transition-all"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                {error && <p className="text-red-400 text-sm mt-3 mb-3">{error}</p>}
                <button
                    onClick={handleLogin}
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-500 text-white rounded p-2 font-bold mt-6 transition-colors"
                >
                    {loading ? "LOGGING IN..." : "LOGIN"}
                </button>
                <div className="mt-6 pt-6 border-t border-gray-800">
                    <p className="text-gray-500 text-xs text-center mb-1">Demo Credentials:</p>
                    <p className="text-gray-600 text-xs text-center">
                        admin / zerotrust123
                    </p>
                </div>
            </div>
        </div>
    );
}
