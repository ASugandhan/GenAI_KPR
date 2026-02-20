'use client';

import { useState, useEffect } from 'react';
import LiveFeed from '@/components/LiveFeed';
import ThreatPanel from '@/components/ThreatPanel';
import RuleEngine from '@/components/RuleEngine';
import TrustScores from '@/components/TrustScores';
import AnalystChat from '@/components/AnalystChat';
import AttackChain from '@/components/AttackChain';
import ThreatTimeline from '@/components/charts/ThreatTimeline';
import TrustGauge from '@/components/charts/TrustGauge';
import TrafficHeatmap from '@/components/charts/TrafficHeatmap';
import { getHealthScore } from '@/lib/api';

export default function Dashboard() {
    const [healthScore, setHealthScore] = useState(100);
    const [totalHealed, setTotalHealed] = useState(0);

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const data = await getHealthScore();
                setHealthScore(data.health_score);
                setTotalHealed(data.total_healed);
            } catch (e) {
                // Backend might not be running
            }
        };
        fetchHealth();
        const interval = setInterval(fetchHealth, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard
                    label="System Health"
                    value={`${healthScore.toFixed(0)}%`}
                    color={healthScore >= 70 ? 'green' : healthScore >= 40 ? 'yellow' : 'red'}
                    icon="🛡️"
                />
                <StatCard label="Incidents Healed" value={totalHealed.toString()} color="cyan" icon="🔧" />
                <StatCard label="Active Agents" value="4" color="purple" icon="🤖" />
                <StatCard label="Zero Trust" value="Enforced" color="green" icon="🔒" />
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column */}
                <div className="lg:col-span-2 space-y-6">
                    <LiveFeed />
                    <ThreatPanel />
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <ThreatTimeline />
                        <TrafficHeatmap />
                    </div>
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    <TrustGauge />
                    <TrustScores />
                    <RuleEngine />
                    <AttackChain />
                </div>
            </div>

            {/* Bottom Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AnalystChat />
            </div>
        </div>
    );
}

// ─── Stat Card ───
function StatCard({ label, value, color, icon }: { label: string; value: string; color: string; icon: string }) {
    const colorMap: Record<string, string> = {
        green: 'from-emerald-500/20 to-emerald-900/10 border-emerald-500/30 text-emerald-400',
        cyan: 'from-cyan-500/20 to-cyan-900/10 border-cyan-500/30 text-cyan-400',
        purple: 'from-purple-500/20 to-purple-900/10 border-purple-500/30 text-purple-400',
        yellow: 'from-yellow-500/20 to-yellow-900/10 border-yellow-500/30 text-yellow-400',
        red: 'from-red-500/20 to-red-900/10 border-red-500/30 text-red-400',
    };

    return (
        <div className={`cyber-card bg-gradient-to-br ${colorMap[color] || colorMap.cyan}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
                    <p className={`text-2xl font-bold mt-1 ${color === 'green' ? 'glow-green' : color === 'red' ? 'glow-red' : 'glow-text'}`}>
                        {value}
                    </p>
                </div>
                <span className="text-3xl">{icon}</span>
            </div>
        </div>
    );
}
