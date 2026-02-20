/**
 * ZeroTrust AI — TypeScript Interfaces
 */

export interface Packet {
    src_ip: string;
    dst_ip: string;
    port: number;
    protocol: string;
    bytes: number;
    duration: number;
    packet_count: number;
    timestamp: string;
    attack_type?: string;
}

export interface ThreatVerdict {
    threat_id: string;
    is_threat: boolean;
    attack_type: string;
    confidence: number;
    severity: string;
    reasoning: string;
    agent: string;
    timestamp: string;
    rule_generated?: FirewallRule;
    trust_score_after?: number;
    action?: string;
}

export interface FirewallRule {
    id: string;
    event_id?: string;
    action: string;
    rule_text: string;
    iptables_cmd: string;
    created_at?: string;
    expires_at?: string;
    active: boolean;
    human_approved?: boolean | null;
}

export interface DeviceTrust {
    device_id: string;
    ip_address: string;
    trust_score: number;
    anomaly_count: number;
    last_threat?: string;
    last_updated?: string;
}

export interface AnalystReport {
    report_id: string;
    summary: string;
    correlations: any[];
    mitre_mappings: any[];
    predicted_next: string;
    event_count: number;
    llm_insight?: any;
}

export interface SelfHealResult {
    heal_id: string;
    incidents_healed: number;
    health_score_before: number;
    health_score_after: number;
    health_score_delta: number;
    permanent_rules: string[];
    hardening_recommendations: string[];
    lessons_learned: string;
}

export interface EventLog {
    id: string;
    timestamp: string;
    src_ip: string;
    dst_ip: string;
    port: number;
    protocol: string;
    attack_type: string;
    confidence: number;
    severity: string;
    agent: string;
    reasoning: string;
    resolved: boolean;
}

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
