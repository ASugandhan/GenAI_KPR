'use client';

import { useState, useEffect } from 'react';
import { getLogs } from '@/lib/api';
import { EventLog } from '@/lib/types';

export default function ThreatPanel() {
    const [events, setEvents] = useState<EventLog[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchLogs = async () => {
            setLoading(true);
            try {
                const data = await getLogs(1, 15);
                setEvents(data.events);
            } catch (e) { /* backend may not be running */ }
            setLoading(false);
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const severityBadge = (severity: string) => {
        const cls: Record<string, string> = {
            CRITICAL: 'badge badge-critical',
            HIGH: 'badge badge-high',
            MEDIUM: 'badge badge-medium',
            LOW: 'badge badge-low',
        };
        return cls[severity] || 'badge badge-low';
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🎯</span>
                    <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Threat Events</h2>
                </div>
                <span className="text-xs text-gray-500">{events.length} events</span>
            </div>

            {loading && events.length === 0 ? (
                <p className="text-gray-500 text-center py-6 text-sm">Loading threats...</p>
            ) : events.length === 0 ? (
                <p className="text-gray-500 text-center py-6 text-sm">No threats detected yet</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="text-gray-500 border-b border-cyber-border">
                                <th className="text-left py-2 px-2">Time</th>
                                <th className="text-left py-2 px-2">Source</th>
                                <th className="text-left py-2 px-2">Type</th>
                                <th className="text-left py-2 px-2">Severity</th>
                                <th className="text-right py-2 px-2">Confidence</th>
                                <th className="text-center py-2 px-2">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {events.map((e) => (
                                <tr key={e.id} className="border-b border-cyber-border/50 hover:bg-white/5 transition-colors">
                                    <td className="py-2 px-2 font-mono text-gray-400">
                                        {e.timestamp?.split('T')[1]?.slice(0, 8) || '--'}
                                    </td>
                                    <td className="py-2 px-2 text-cyan-400">{e.src_ip}</td>
                                    <td className="py-2 px-2 text-white">{e.attack_type}</td>
                                    <td className="py-2 px-2">
                                        <span className={severityBadge(e.severity)}>{e.severity}</span>
                                    </td>
                                    <td className="py-2 px-2 text-right font-mono">{(e.confidence * 100).toFixed(0)}%</td>
                                    <td className="py-2 px-2 text-center">
                                        {e.resolved ? (
                                            <span className="text-emerald-400">✓</span>
                                        ) : (
                                            <span className="text-yellow-400">●</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
