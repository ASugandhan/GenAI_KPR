"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const router = useRouter();

    const handleLogin = async () => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem("token", data.access_token);
                router.push("/");
            } else {
                setError("Invalid credentials");
            }
        } catch (err) {
            setError("Failed to connect to authentication server");
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
                    className="w-full bg-green-600 hover:bg-green-500 text-white rounded p-2 font-bold mt-6 transition-colors"
                >
                    LOGIN
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
