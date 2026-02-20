'use client';

// src/components/ZeroTrustLogo.tsx
// Usage: <ZeroTrustLogo size={48} />

export default function ZeroTrustLogo({ size = 48 }: { size?: number }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 160 160"
            xmlns="http://www.w3.org/2000/svg"
            style={{ filter: 'drop-shadow(0 0 10px rgba(0,200,255,0.4))' }}
        >
            <defs>
                <linearGradient id="zt-hex-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#00c8ff" />
                    <stop offset="100%" stopColor="#00ff9d" />
                </linearGradient>
                <radialGradient id="zt-bg-glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(0,200,255,0.12)" />
                    <stop offset="100%" stopColor="rgba(0,0,0,0)" />
                </radialGradient>
                <filter id="zt-glow">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>

                <style>{`
                    @keyframes zt-ring-cw   { to { transform: rotate(360deg);  } }
                    @keyframes zt-ring-ccw  { to { transform: rotate(-360deg); } }
                    @keyframes zt-arc-spin  { to { transform: rotate(360deg);  } }
                    @keyframes zt-pulse-out {
                        0%   { opacity: 0.7; r: 36; }
                        100% { opacity: 0;   r: 54; }
                    }
                    @keyframes zt-blink {
                        0%, 100% { opacity: 1;   }
                        50%      { opacity: 0.2; }
                    }
                    @keyframes zt-breathe {
                        0%, 100% { filter: drop-shadow(0 0 10px rgba(0,200,255,0.35)); }
                        50%      { filter: drop-shadow(0 0 24px rgba(0,200,255,0.7));  }
                    }

                    .zt-svg        { animation: zt-breathe 3s ease-in-out infinite; }
                    .zt-cw         { transform-box: fill-box; transform-origin: center; animation: zt-ring-cw  12s linear infinite; }
                    .zt-ccw        { transform-box: fill-box; transform-origin: center; animation: zt-ring-ccw  8s linear infinite; }
                    .zt-arc        { transform-box: fill-box; transform-origin: center; animation: zt-arc-spin  4s linear infinite; }
                    .zt-pulse      { animation: zt-pulse-out 2.5s ease-out infinite; }
                    .zt-pulse:nth-child(2) { animation-delay: 0.8s;  }
                    .zt-pulse:nth-child(3) { animation-delay: 1.6s;  }
                    .zt-n1 { animation: zt-blink 1.5s ease-in-out infinite 0s;    }
                    .zt-n2 { animation: zt-blink 1.5s ease-in-out infinite 0.5s;  }
                    .zt-n3 { animation: zt-blink 1.5s ease-in-out infinite 1.0s;  }
                `}</style>
            </defs>

            {/* Ambient glow */}
            <circle cx="80" cy="80" r="75" fill="url(#zt-bg-glow)" />

            {/* Pulse rings */}
            <circle className="zt-pulse" cx="80" cy="80" r="36" fill="none" stroke="rgba(0,200,255,0.35)" strokeWidth="1" />
            <circle className="zt-pulse" cx="80" cy="80" r="36" fill="none" stroke="rgba(0,200,255,0.35)" strokeWidth="1" />
            <circle className="zt-pulse" cx="80" cy="80" r="36" fill="none" stroke="rgba(0,200,255,0.35)" strokeWidth="1" />

            {/* Outer hex ring — clockwise */}
            <g className="zt-cw">
                <polygon points="80,22 112,40 112,76 80,94 48,76 48,40"
                    fill="none" stroke="rgba(0,200,255,0.15)" strokeWidth="1" strokeDasharray="6 4" />
                <circle cx="80"  cy="22" r="2.5" fill="#00c8ff" opacity="0.75" />
                <circle cx="112" cy="40" r="2"   fill="#00ff9d" opacity="0.65" />
                <circle cx="112" cy="76" r="2"   fill="#00c8ff" opacity="0.55" />
                <circle cx="80"  cy="94" r="2.5" fill="#00ff9d" opacity="0.75" />
                <circle cx="48"  cy="76" r="2"   fill="#00c8ff" opacity="0.55" />
                <circle cx="48"  cy="40" r="2"   fill="#00ff9d" opacity="0.65" />
            </g>

            {/* Inner ring — counter-clockwise */}
            <g className="zt-ccw">
                <circle cx="80" cy="80" r="48" fill="none"
                    stroke="rgba(0,255,157,0.1)" strokeWidth="1" strokeDasharray="4 8" />
                <circle cx="80"  cy="32" r="2.5" fill="#00c8ff" opacity="0.5" />
                <circle cx="128" cy="80" r="2"   fill="#00ff9d" opacity="0.45" />
                <circle cx="32"  cy="80" r="2"   fill="#00c8ff" opacity="0.4" />
            </g>

            {/* Shield hexagon */}
            <polygon points="80,30 108,46 108,78 80,94 52,78 52,46"
                fill="rgba(0,10,30,0.92)"
                stroke="url(#zt-hex-grad)"
                strokeWidth="2"
                filter="url(#zt-glow)" />

            {/* Inner hex detail */}
            <polygon points="80,38 100,50 100,74 80,86 60,74 60,50"
                fill="rgba(0,200,255,0.04)"
                stroke="rgba(0,200,255,0.18)"
                strokeWidth="0.8" />

            {/* ZT text */}
            <text x="80" y="65"
                textAnchor="middle" dominantBaseline="middle"
                fontFamily="'Orbitron', 'Share Tech Mono', monospace"
                fontSize="28" fontWeight="900"
                fill="url(#zt-hex-grad)"
                filter="url(#zt-glow)">
                ZT
            </text>

            {/* Divider + AI label */}
            <line x1="63" y1="76" x2="97" y2="76" stroke="rgba(0,200,255,0.3)" strokeWidth="0.8" />
            <text x="80" y="85"
                textAnchor="middle"
                fontFamily="'Orbitron', monospace"
                fontSize="7" fill="rgba(0,255,157,0.75)" letterSpacing="4">
                AI
            </text>

            {/* Spinning arc */}
            <g className="zt-arc">
                <path d="M80,15 A65,65 0 0,1 125,45"
                    fill="none" stroke="rgba(0,200,255,0.5)"
                    strokeWidth="2" strokeLinecap="round" />
            </g>

            {/* Network nodes */}
            <g transform="translate(80,112)">
                <line x1="-20" y1="0" x2="0"  y2="-8" stroke="rgba(0,200,255,0.3)" strokeWidth="0.8" />
                <line x1="0"   y1="-8" x2="20" y2="0"  stroke="rgba(0,200,255,0.3)" strokeWidth="0.8" />
                <line x1="-20" y1="0"  x2="20" y2="0"  stroke="rgba(0,255,157,0.2)" strokeWidth="0.8" strokeDasharray="3 3" />
                <circle className="zt-n1" cx="-20" cy="0"  r="3" fill="#00c8ff" />
                <circle className="zt-n2" cx="0"   cy="-8" r="4" fill="#00ff9d" />
                <circle className="zt-n3" cx="20"  cy="0"  r="3" fill="#00c8ff" />
            </g>
        </svg>
    );
}