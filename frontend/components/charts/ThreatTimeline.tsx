'use client';

import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useSSE } from '@/lib/useSSE';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ThreatTimeline() {
    const { packets } = useSSE(`${API_URL}/api/traffic/stream`, 100);
    const [data, setData] = useState<any[]>([]);

    useEffect(() => {
        // Aggregate packets into time buckets
        const now = Date.now();
        const buckets: Record<string, { time: string; threats: number; normal: number }> = {};

        for (let i = 0; i < 10; i++) {
            const t = new Date(now - (9 - i) * 5000);
            const key = t.toLocaleTimeString().slice(0, 5);
            buckets[key] = { time: key, threats: 0, normal: 0 };
        }

        packets.forEach((p) => {
            const time = new Date().toLocaleTimeString().slice(0, 5);
            if (buckets[time]) {
                if (p.attack_type && p.attack_type !== 'normal') {
                    buckets[time].threats++;
                } else {
                    buckets[time].normal++;
                }
            }
        });

        setData(Object.values(buckets));
    }, [packets]);

    return (
        <div className="cyber-card">
            <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">📈</span>
                <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Threat Timeline</h2>
            </div>

            <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="threatGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ff3366" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ff3366" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="normalGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
                    <Tooltip
                        contentStyle={{
                            background: '#111827',
                            border: '1px solid #1e293b',
                            borderRadius: '8px',
                            fontSize: '11px',
                        }}
                    />
                    <Area type="monotone" dataKey="normal" stroke="#00ff88" fill="url(#normalGrad)" strokeWidth={2} />
                    <Area type="monotone" dataKey="threats" stroke="#ff3366" fill="url(#threatGrad)" strokeWidth={2} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
