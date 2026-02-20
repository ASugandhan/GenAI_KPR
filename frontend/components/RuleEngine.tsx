'use client';

import { useState, useEffect } from 'react';
import { getRules, overrideRule } from '@/lib/api';
import { FirewallRule } from '@/lib/types';

export default function RuleEngine() {
    const [rules, setRules] = useState<FirewallRule[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchRules = async () => {
        setLoading(true);
        try {
            const data = await getRules();
            setRules(data.rules);
        } catch (e) { /* backend may not be running */ }
        setLoading(false);
    };

    useEffect(() => {
        fetchRules();
        const interval = setInterval(fetchRules, 8000);
        return () => clearInterval(interval);
    }, []);

    const handleOverride = async (ruleId: string, approved: boolean) => {
        try {
            await overrideRule(ruleId, approved);
            fetchRules();
        } catch (e) {
            console.error('Override failed:', e);
        }
    };

    const actionColor = (action: string) => {
        const colors: Record<string, string> = {
            monitor: 'text-emerald-400',
            rate_limit: 'text-yellow-400',
            block_temp: 'text-orange-400',
            block_perm: 'text-red-400',
        };
        return colors[action] || 'text-gray-400';
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🧱</span>
                    <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Firewall Rules</h2>
                </div>
                <span className="text-xs text-gray-500">{rules.length} active</span>
            </div>

            {rules.length === 0 ? (
                <p className="text-gray-500 text-center py-4 text-xs">No active rules</p>
            ) : (
                <div className="space-y-2 max-h-[250px] overflow-y-auto">
                    {rules.map((rule) => (
                        <div
                            key={rule.id}
                            className="p-3 rounded-lg bg-black/30 border border-cyber-border/50 hover:border-cyber-border transition-colors"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <span className={`text-xs font-semibold uppercase ${actionColor(rule.action)}`}>
                                    {rule.action?.replace('_', ' ')}
                                </span>
                                {rule.human_approved === null ? (
                                    <div className="flex gap-1">
                                        <button
                                            onClick={() => handleOverride(rule.id, true)}
                                            className="px-2 py-0.5 text-[10px] rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 transition-colors"
                                        >
                                            Approve
                                        </button>
                                        <button
                                            onClick={() => handleOverride(rule.id, false)}
                                            className="px-2 py-0.5 text-[10px] rounded bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                        >
                                            Reject
                                        </button>
                                    </div>
                                ) : (
                                    <span className={`text-[10px] ${rule.human_approved ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {rule.human_approved ? '✓ Approved' : '✕ Rejected'}
                                    </span>
                                )}
                            </div>
                            <p className="text-xs text-gray-400">{rule.rule_text}</p>
                            <p className="text-[10px] text-gray-600 font-mono mt-1">{rule.iptables_cmd}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
