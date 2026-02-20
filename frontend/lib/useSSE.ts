/**
 * ZeroTrust AI — Server-Sent Events Hook
 * Real-time packet streaming from backend.
 */
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Packet } from './types';

export function useSSE(url: string, maxItems = 50) {
    const [packets, setPackets] = useState<Packet[]>([]);
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    const connect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        try {
            const es = new EventSource(url);
            eventSourceRef.current = es;

            es.onopen = () => {
                setConnected(true);
                setError(null);
            };

            es.addEventListener('packet', (event) => {
                try {
                    const packet: Packet = JSON.parse(event.data);
                    setPackets((prev) => [packet, ...prev].slice(0, maxItems));
                } catch (e) {
                    console.error('Failed to parse SSE packet:', e);
                }
            });

            es.onerror = () => {
                setConnected(false);
                setError('Connection lost — reconnecting...');
                es.close();
                // Reconnect after 3 seconds
                setTimeout(connect, 3000);
            };
        } catch (e) {
            setError('Failed to connect to stream');
            setConnected(false);
        }
    }, [url, maxItems]);

    useEffect(() => {
        connect();
        return () => {
            eventSourceRef.current?.close();
        };
    }, [connect]);

    const disconnect = useCallback(() => {
        eventSourceRef.current?.close();
        setConnected(false);
    }, []);

    return { packets, connected, error, disconnect };
}
