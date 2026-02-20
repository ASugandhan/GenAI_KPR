'use client';

import { useSSE } from '@/lib/useSSE';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default function LiveFeed() {
    const { packets, connected } = useSSE(`${API_URL}/api/traffic/stream`, 30);

    const severityColor = (type: string) => {
        if (type === 'normal') return 'text-emerald-400';
        if (['ddos', 'exploit'].includes(type)) return 'text-red-400';
        if (['brute_force', 'c2_beacon'].includes(type)) return 'text-orange-400';
        return 'text-yellow-400';
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">📡</span>
                    <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Live Packet Feed</h2>
                </div>
                <div className="flex items-center gap-2">
                    {connected ? (
                        <>
                            <div className="live-pulse" />
                            <span className="text-xs text-emerald-400">Connected</span>
                        </>
                    ) : (
                        <span className="text-xs text-red-400">● Disconnected</span>
                    )}
                </div>
            </div>

            <div className="space-y-1 max-h-[300px] overflow-y-auto font-mono text-xs">
                {packets.length === 0 ? (
                    <p className="text-gray-500 text-center py-6">Waiting for packets...</p>
                ) : (
                    packets.map((pkt, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-3 px-3 py-1.5 rounded-md hover:bg-white/5 transition-colors animate-slide-in"
                        >
                            <span className="text-gray-600 w-16">{pkt.timestamp?.split('T')[1]?.slice(0, 8) || '--:--:--'}</span>
                            <span className="text-cyan-400 w-28 truncate">{pkt.src_ip}</span>
                            <span className="text-gray-600">→</span>
                            <span className="text-blue-400 w-28 truncate">{pkt.dst_ip}</span>
                            <span className="text-gray-500 w-14 text-right">:{pkt.port}</span>
                            <span className="text-purple-400 w-12">{pkt.protocol}</span>
                            <span className="text-gray-500 w-16 text-right">{pkt.bytes}B</span>
                            <span className={`ml-auto ${severityColor(pkt.attack_type || 'normal')}`}>
                                {pkt.attack_type === 'normal' ? '✓' : '⚠'} {pkt.attack_type || 'normal'}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
