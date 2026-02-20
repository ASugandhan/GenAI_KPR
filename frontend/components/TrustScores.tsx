'use client';

import { useState, useEffect } from 'react';
import { getTrustScores } from '@/lib/api';
import { DeviceTrust } from '@/lib/types';

export default function TrustScores() {
    const [devices, setDevices] = useState<DeviceTrust[]>([]);

    useEffect(() => {
        const fetch = async () => {
            try {
                const data = await getTrustScores();
                setDevices(data.devices);
            } catch (e) { /* backend may not be running */ }
        };
        fetch();
        const interval = setInterval(fetch, 5000);
        return () => clearInterval(interval);
    }, []);

    const scoreColor = (score: number) => {
        if (score >= 70) return 'text-emerald-400';
        if (score >= 40) return 'text-yellow-400';
        if (score >= 20) return 'text-orange-400';
        return 'text-red-400';
    };

    const scoreBg = (score: number) => {
        if (score >= 70) return 'bg-emerald-400';
        if (score >= 40) return 'bg-yellow-400';
        if (score >= 20) return 'bg-orange-400';
        return 'bg-red-400';
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🔐</span>
                    <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Device Trust</h2>
                </div>
                <span className="text-xs text-gray-500">{devices.length} devices</span>
            </div>

            {devices.length === 0 ? (
                <p className="text-gray-500 text-center py-4 text-xs">No devices tracked yet</p>
            ) : (
                <div className="space-y-3 max-h-[200px] overflow-y-auto">
                    {devices.map((d) => (
                        <div key={d.device_id} className="space-y-1">
                            <div className="flex justify-between text-xs">
                                <span className="text-gray-300 font-mono">{d.ip_address}</span>
                                <span className={`font-semibold ${scoreColor(d.trust_score)}`}>
                                    {d.trust_score.toFixed(0)}
                                </span>
                            </div>
                            <div className="w-full h-1.5 rounded-full bg-gray-800">
                                <div
                                    className={`h-full rounded-full ${scoreBg(d.trust_score)} transition-all duration-500`}
                                    style={{ width: `${d.trust_score}%` }}
                                />
                            </div>
                            <div className="flex justify-between text-[10px] text-gray-600">
                                <span>{d.anomaly_count} anomalies</span>
                                <span>
                                    {d.trust_score >= 70 ? 'Monitor' : d.trust_score >= 40 ? 'Rate Limited' : d.trust_score >= 20 ? 'Temp Blocked' : 'Hard Blocked'}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
