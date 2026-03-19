/**
 * ZeroTrust AI — API Call Wrappers
 */
import axios from 'axios';
import { Packet, ThreatVerdict, FirewallRule, DeviceTrust, AnalystReport, SelfHealResult, EventLog } from './types';

const API = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || '',
    timeout: 10000,
});

// Add a request interceptor to include the JWT token
API.interceptors.request.use((config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ─── Detection ───
export async function detectThreat(packet: Packet): Promise<ThreatVerdict> {
    const { data } = await API.post('/api/detect', packet);
    return data;
}

// ─── Rules ───
export async function getRules(): Promise<{ rules: FirewallRule[] }> {
    const { data } = await API.get('/api/rules');
    return data;
}

export async function overrideRule(ruleId: string, approved: boolean) {
    const { data } = await API.post('/api/rules/override', { rule_id: ruleId, approved });
    return data;
}

// ─── Trust Scores ───
export async function getTrustScores(): Promise<{ devices: DeviceTrust[] }> {
    const { data } = await API.get('/api/trust');
    return data;
}

export async function getDeviceTrust(deviceId: string): Promise<DeviceTrust> {
    const { data } = await API.get(`/api/trust/${deviceId}`);
    return data;
}

// ─── Analyst ───
export async function getSummary(): Promise<AnalystReport> {
    const { data } = await API.post('/api/summarize');
    return data;
}

// ─── Self-Heal ───
export async function triggerSelfHeal(): Promise<SelfHealResult> {
    const { data } = await API.post('/api/selfheal');
    return data;
}

export async function getHealthScore(): Promise<{ health_score: number; total_healed: number }> {
    const { data } = await API.get('/api/health-score');
    return data;
}

// ─── Logs ───
export async function getLogs(page = 1, limit = 20, severity?: string): Promise<{ total: number; events: EventLog[] }> {
    const params: any = { page, limit };
    if (severity) params.severity = severity;
    const { data } = await API.get('/api/logs', { params });
    return data;
}

// ─── Health ───
export async function healthCheck(): Promise<{ status: string }> {
    const { data } = await API.get('/api/health');
    return data;
}
