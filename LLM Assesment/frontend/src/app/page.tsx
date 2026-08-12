'use client';

import { useRouter } from 'next/navigation';
import { createSession } from './api';
import { useState } from 'react';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const startAssessment = async () => {
    setLoading(true);
    try {
      const session = await createSession();
      router.push(`/assessment/${session.session_id}`);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card text-center" style={{ marginTop: '80px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>
          LLM Assessment Agent
        </h1>
        <p className="text-muted" style={{ marginBottom: '24px', fontSize: '1.05rem' }}>
          Test your knowledge of Large Language Models
        </p>
        <p className="text-muted text-sm" style={{ marginBottom: '32px', maxWidth: '500px', margin: '0 auto 32px', lineHeight: '1.6' }}>
          Adaptive difficulty from beginner to expert. Answer questions, track your progress,
          and get personalized recommendations.
        </p>
        <div className="flex gap-4" style={{ justifyContent: 'center', marginBottom: '24px' }}>
          <button className="btn" onClick={startAssessment} disabled={loading}>
            {loading ? 'Starting...' : 'Start Assessment'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => router.push('/dashboard')}
          >
            Dashboard
          </button>
        </div>
        <div className="flex gap-4" style={{ justifyContent: 'center', flexWrap: 'wrap' }}>
          <span className="badge badge-beginner">Beginner</span>
          <span className="badge badge-intermediate">Intermediate</span>
          <span className="badge badge-advanced">Advanced</span>
          <span className="badge badge-expert">Expert</span>
        </div>
      </div>
    </div>
  );
}
