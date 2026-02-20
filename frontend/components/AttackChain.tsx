'use client';

const ATTACK_CHAINS = [
    {
        name: 'Recon → Exploit',
        techniques: ['T1046', 'T1190'],
        steps: ['Network Scan', 'Service Discovery', 'Vulnerability ID', 'Exploitation'],
        color: 'from-cyan-500 to-blue-600',
        dotColor: 'bg-cyan-400',
    },
    {
        name: 'Brute Force → Lateral',
        techniques: ['T1110', 'T1021'],
        steps: ['Credential Attack', 'Auth Bypass', 'Internal Access', 'Lateral Move'],
        color: 'from-orange-500 to-red-600',
        dotColor: 'bg-orange-400',
    },
    {
        name: 'C2 Beacon',
        techniques: ['T1059'],
        steps: ['Initial Access', 'Beacon Install', 'C2 Connection', 'Data Exfil'],
        color: 'from-purple-500 to-pink-600',
        dotColor: 'bg-purple-400',
    },
    {
        name: 'DDoS Escalation',
        techniques: ['T1498'],
        steps: ['Traffic Spike', 'Amplification', 'Service Degradation', 'Full DDoS'],
        color: 'from-red-500 to-rose-600',
        dotColor: 'bg-red-400',
    },
];

export default function AttackChain() {
    return (
        <div className="cyber-card">
            <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">⛓️</span>
                <h2 className="text-sm font-semibold text-white uppercase tracking-wide">MITRE ATT&CK Chains</h2>
            </div>

            <div className="space-y-4">
                {ATTACK_CHAINS.map((chain) => (
                    <div key={chain.name} className="space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-gray-300">{chain.name}</span>
                            <span className="text-[10px] text-gray-500 font-mono">{chain.techniques.join(' → ')}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            {chain.steps.map((step, i) => (
                                <div key={step} className="flex items-center flex-1">
                                    <div className="flex flex-col items-center flex-1">
                                        <div className={`w-3 h-3 rounded-full ${chain.dotColor} shadow-lg shadow-current/30`} />
                                        <p className="text-[9px] text-gray-500 mt-1 text-center leading-tight">{step}</p>
                                    </div>
                                    {i < chain.steps.length - 1 && (
                                        <div className={`h-0.5 flex-1 bg-gradient-to-r ${chain.color} opacity-40 -mt-3`} />
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
