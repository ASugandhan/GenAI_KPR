import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'ZeroTrust AI — Multi-Agent Firewall',
    description: 'AI-Powered Multi-Agent Firewall with real-time threat detection, classification, and automated response.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className="grid-bg min-h-screen">
                {/* Header */}
                <header className="sticky top-0 z-50 border-b border-cyber-border bg-cyber-bg/80 backdrop-blur-xl">
                    <div className="max-w-[1800px] mx-auto px-6 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
                                ZT
                            </div>
                            <div>
                                <h1 className="text-lg font-semibold text-white glow-text">ZeroTrust AI</h1>
                                <p className="text-[10px] text-gray-500 tracking-widest uppercase">Multi-Agent Firewall</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                <div className="live-pulse" />
                                <span>System Active</span>
                            </div>
                            <div className="text-xs text-gray-500 font-mono">v1.0.0</div>
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="max-w-[1800px] mx-auto px-6 py-6">
                    {children}
                </main>
            </body>
        </html>
    );
}
