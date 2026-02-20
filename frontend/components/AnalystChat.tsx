'use client';

import { useState } from 'react';
import { getSummary, triggerSelfHeal } from '@/lib/api';
import { AnalystReport, SelfHealResult } from '@/lib/types';

export default function AnalystChat() {
    const [report, setReport] = useState<AnalystReport | null>(null);
    const [healResult, setHealResult] = useState<SelfHealResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [healLoading, setHealLoading] = useState(false);

    const runAnalysis = async () => {
        setLoading(true);
        try {
            const data = await getSummary();
            setReport(data);
        } catch (e) {
            console.error('Analysis failed:', e);
        }
        setLoading(false);
    };

    const runSelfHeal = async () => {
        setHealLoading(true);
        try {
            const data = await triggerSelfHeal();
            setHealResult(data);
        } catch (e) {
            console.error('Self-heal failed:', e);
        }
        setHealLoading(false);
    };

    return (
        <div className="cyber-card">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🧠</span>
                    <h2 className="text-sm font-semibold text-white uppercase tracking-wide">AI Analyst Console</h2>
                </div>
                <div className="flex gap-2">
                    <button onClick={runAnalysis} disabled={loading} className="cyber-btn text-xs">
                        {loading ? '⏳ Analyzing...' : '📊 Run Analysis'}
                    </button>
                    <button onClick={runSelfHeal} disabled={healLoading} className="cyber-btn text-xs">
                        {healLoading ? '⏳ Healing...' : '🔧 Self-Heal'}
                    </button>
                </div>
            </div>

            <div className="space-y-4 max-h-[400px] overflow-y-auto">
                {/* Analysis Report */}
                {report && (
                    <div className="p-4 rounded-lg bg-black/40 border border-cyan-500/20 space-y-3">
                        <h3 className="text-xs font-semibold text-cyan-400 uppercase">Analysis Report</h3>
                        <p className="text-xs text-gray-300">{report.summary}</p>

                        {report.mitre_mappings && report.mitre_mappings.length > 0 && (
                            <div>
                                <h4 className="text-[10px] text-gray-500 uppercase mb-1">MITRE ATT&CK Mappings</h4>
                                {report.mitre_mappings.map((m: any, i: number) => (
                                    <div key={i} className="text-xs text-purple-400 font-mono">
                                        {m.techniques?.join(', ')} — {m.description}
                                    </div>
                                ))}
                            </div>
                        )}

                        {report.predicted_next && (
                            <div>
                                <h4 className="text-[10px] text-gray-500 uppercase mb-1">Predicted Next Attack</h4>
                                <p className="text-xs text-yellow-400">{report.predicted_next}</p>
                            </div>
                        )}

                        {report.correlations && report.correlations.length > 0 && (
                            <div>
                                <h4 className="text-[10px] text-gray-500 uppercase mb-1">Correlations</h4>
                                {report.correlations.map((c: any, i: number) => (
                                    <p key={i} className="text-xs text-gray-400">
                                        {c.pattern}: {c.source_ip || c.target_ip} ({c.event_count || c.source_count} events)
                                    </p>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Self-Heal Results */}
                {healResult && (
                    <div className="p-4 rounded-lg bg-black/40 border border-emerald-500/20 space-y-3">
                        <h3 className="text-xs font-semibold text-emerald-400 uppercase">Self-Heal Report</h3>
                        <div className="grid grid-cols-3 gap-2 text-center">
                            <div>
                                <p className="text-lg font-bold text-white">{healResult.incidents_healed}</p>
                                <p className="text-[10px] text-gray-500">Healed</p>
                            </div>
                            <div>
                                <p className="text-lg font-bold text-emerald-400">+{(healResult.health_score_delta ?? 0).toFixed(0)}</p>
                                <p className="text-[10px] text-gray-500">Health ↑</p>
                            </div>
                            <div>
                                <p className="text-lg font-bold text-cyan-400">{(healResult.health_score_after ?? 0).toFixed(0)}%</p>
                                <p className="text-[10px] text-gray-500">Current</p>
                            </div>
                        </div>

                        {healResult.hardening_recommendations && healResult.hardening_recommendations.length > 0 && (
                            <div>
                                <h4 className="text-[10px] text-gray-500 uppercase mb-1">Hardening Recommendations</h4>
                                <ul className="space-y-1">
                                    {healResult.hardening_recommendations.map((r, i) => (
                                        <li key={i} className="text-xs text-gray-300 flex items-start gap-1">
                                            <span className="text-emerald-400 mt-0.5">›</span> {r}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {healResult.lessons_learned && (
                            <div>
                                <h4 className="text-[10px] text-gray-500 uppercase mb-1">Lessons Learned</h4>
                                <p className="text-xs text-gray-400 italic">{healResult.lessons_learned}</p>
                            </div>
                        )}
                    </div>
                )}

                {!report && !healResult && (
                    <p className="text-gray-500 text-center py-8 text-xs">
                        Click &quot;Run Analysis&quot; for threat intelligence or &quot;Self-Heal&quot; for post-incident hardening.
                    </p>
                )}
            </div>
        </div>
    );
}
