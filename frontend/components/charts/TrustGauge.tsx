'use client';

import { useState, useEffect } from 'react';
import { getHealthScore } from '@/lib/api';

export default function TrustGauge() {
    const [score, setScore] = useState(100);
    const [healed, setHealed] = useState(0);

    useEffect(() => {
        const fetch = async () => {
            try {
                const data = await getHealthScore();
                setScore(data.health_score);
                setHealed(data.total_healed);
            } catch (e) { /* backend may not be running */ }
        };
        fetch();
        const interval = setInterval(fetch, 10000);
        return () => clearInterval(interval);
    }, []);

    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const progress = (score / 100) * circumference;
    const dashOffset = circumference - progress;

    const color = score >= 70 ? '#00ff88' : score >= 40 ? '#ffcc00' : '#ff3366';

    return (
        <div className="cyber-card">
            <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">📊</span>
                <h2 className="text-sm font-semibold text-white uppercase tracking-wide">System Health</h2>
            </div>

            <div className="flex flex-col items-center">
                <div className="relative">
                    <svg width="170" height="170" viewBox="0 0 170 170">
                        {/* Background circle */}
                        <circle
                            cx="85"
                            cy="85"
                            r={radius}
                            fill="none"
                            stroke="#1e293b"
                            strokeWidth="10"
                        />
                        {/* Progress circle */}
                        <circle
                            cx="85"
                            cy="85"
                            r={radius}
                            fill="none"
                            stroke={color}
                            strokeWidth="10"
                            strokeLinecap="round"
                            strokeDasharray={circumference}
                            strokeDashoffset={dashOffset}
                            transform="rotate(-90 85 85)"
                            style={{
                                transition: 'stroke-dashoffset 1s ease, stroke 0.5s ease',
                                filter: `drop-shadow(0 0 8px ${color}40)`,
                            }}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-white" style={{ textShadow: `0 0 15px ${color}50` }}>
                            {score.toFixed(0)}
                        </span>
                        <span className="text-[10px] text-gray-500 uppercase tracking-wider">Health Score</span>
                    </div>
                </div>

                <div className="flex gap-6 mt-3 text-center">
                    <div>
                        <p className="text-xs font-semibold text-emerald-400">{healed}</p>
                        <p className="text-[10px] text-gray-500">Healed</p>
                    </div>
                    <div>
                        <p className="text-xs font-semibold" style={{ color }}>
                            {score >= 70 ? 'Healthy' : score >= 40 ? 'Degraded' : 'Critical'}
                        </p>
                        <p className="text-[10px] text-gray-500">Status</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
