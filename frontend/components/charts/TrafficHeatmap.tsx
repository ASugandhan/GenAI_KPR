'use client';

import { useState, useEffect } from 'react';
import { useSSE } from '@/lib/useSSE';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

const PROTOCOLS = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS', 'SSH', 'ICMP'];
const HOURS = ['00', '04', '08', '12', '16', '20'];

export default function TrafficHeatmap() {
    const { packets } = useSSE(`${API_URL}/api/traffic/stream`, 200);
    const [heatData, setHeatData] = useState<Record<string, number>>({});

    useEffect(() => {
        const counts: Record<string, number> = {};
        const currentHour = new Date().getHours();

        // Find the closest hour bucket (00, 04, 08, 12, 16, 20)
        const bucket = HOURS.reduce((prev, curr) => {
            return (Math.abs(parseInt(curr) - currentHour) < Math.abs(parseInt(prev) - currentHour) ? curr : prev);
        });

        packets.forEach((p) => {
            const proto = (p.protocol || 'TCP').toUpperCase();
            const key = `${proto}-${bucket}`;
            counts[key] = (counts[key] || 0) + 1;
        });
        setHeatData(counts);
    }, [packets]);

    const maxVal = Math.max(1, ...Object.values(heatData));

    const getIntensity = (protocol: string, hour: string) => {
        const key = `${protocol}-${hour}`;
        const val = heatData[key] || 0;
        return val / maxVal;
    };

    const intensityColor = (intensity: number) => {
        if (intensity === 0) return 'bg-gray-800/50';
        if (intensity < 0.25) return 'bg-cyan-900/50';
        if (intensity < 0.5) return 'bg-cyan-700/60';
        if (intensity < 0.75) return 'bg-cyan-500/70';
        return 'bg-cyan-400/80';
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">🔥</span>
                <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Traffic Heatmap</h2>
            </div>

            <div className="overflow-x-auto">
                <div className="min-w-[280px]">
                    {/* Header */}
                    <div className="flex mb-1">
                        <div className="w-12" />
                        {HOURS.map((h) => (
                            <div key={h} className="flex-1 text-center text-[9px] text-gray-500 font-mono">
                                {h}:00
                            </div>
                        ))}
                    </div>

                    {/* Rows */}
                    {PROTOCOLS.map((proto) => (
                        <div key={proto} className="flex items-center mb-1">
                            <div className="w-12 text-[10px] text-gray-400 font-mono">{proto}</div>
                            {HOURS.map((h) => {
                                const intensity = getIntensity(proto, h);
                                return (
                                    <div key={`${proto}-${h}`} className="flex-1 px-0.5">
                                        <div
                                            className={`h-5 rounded-sm ${intensityColor(intensity)} transition-colors duration-500`}
                                            title={`${proto} @ ${h}:00 — ${(heatData[`${proto}-${h}`] || 0)} packets`}
                                        />
                                    </div>
                                );
                            })}
                        </div>
                    ))}

                    {/* Legend */}
                    <div className="flex items-center justify-end gap-1 mt-2">
                        <span className="text-[9px] text-gray-500">Low</span>
                        <div className="w-3 h-2 rounded-sm bg-gray-800/50" />
                        <div className="w-3 h-2 rounded-sm bg-cyan-900/50" />
                        <div className="w-3 h-2 rounded-sm bg-cyan-700/60" />
                        <div className="w-3 h-2 rounded-sm bg-cyan-500/70" />
                        <div className="w-3 h-2 rounded-sm bg-cyan-400/80" />
                        <span className="text-[9px] text-gray-500">High</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
