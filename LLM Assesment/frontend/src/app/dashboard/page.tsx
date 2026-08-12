'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { getDashboard, DashboardData, createSession } from '../api';

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    getDashboard().then(setData).catch(console.error);
  }, []);

  const StatCard = ({ title, stats }: { title: string; stats: { total_questions: number; correct_answers: number; wrong_questions?: number; accuracy: number; sessions: number } }) => (
    <div className="card">
      <div className="card-header">{title}</div>
      <div className="grid-3">
        <div>
          <div className="stat-value">{stats.total_questions}</div>
          <div className="stat-label">Questions</div>
        </div>
        <div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{stats.accuracy}%</div>
          <div className="stat-label">Accuracy</div>
        </div>
        <div>
          <div className="stat-value">{stats.sessions}</div>
          <div className="stat-label">Sessions</div>
        </div>
      </div>
      <div className="flex gap-4 mt-4 text-sm">
        <span className="correct-text">✓ {stats.correct_answers} correct</span>
        <span className="wrong-text">✗ {stats.total_questions - stats.correct_answers} wrong</span>
      </div>
    </div>
  );

  return (
    <div className="container">
      <div className="flex items-center justify-between mb-4">
        <h2 style={{ fontSize: '1.5rem' }}>Dashboard</h2>
        <div className="flex gap-2">
          <button className="btn btn-sm btn-secondary" onClick={() => router.push('/')}>Home</button>
          <button className="btn btn-sm" onClick={async () => {
            const session = await createSession();
            router.push(`/assessment/${session.session_id}`);
          }}>New Assessment</button>
        </div>
      </div>

      <StatCard title="Last 24 Hours" stats={data?.daily || { total_questions: 0, correct_answers: 0, accuracy: 0, sessions: 0 }} />
      <StatCard title="Last 7 Days" stats={data?.weekly || { total_questions: 0, correct_answers: 0, accuracy: 0, sessions: 0 }} />
      <StatCard title="Last 30 Days" stats={data?.monthly || { total_questions: 0, correct_answers: 0, accuracy: 0, sessions: 0 }} />

      <div className="card">
        <div className="card-header">Progress Over Time</div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data?.trend_data || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="date"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              />
              <YAxis
                yAxisId="left"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                domain={[0, 100]}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                domain={[0, 3]}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  color: 'var(--text)',
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="accuracy"
                stroke="var(--primary)"
                strokeWidth={2}
                dot={{ fill: 'var(--primary)' }}
                name="Accuracy %"
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="questions_answered"
                stroke="var(--accent)"
                strokeWidth={2}
                dot={{ fill: 'var(--accent)' }}
                name="Questions"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="average_difficulty"
                stroke="var(--warning)"
                strokeWidth={2}
                dot={{ fill: 'var(--warning)' }}
                name="Avg Difficulty (0-3)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Knowledge Improvement Areas</div>
        <div className="flex flex-col gap-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Beginner</span>
              <span className="text-muted">Foundation</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'var(--surface2)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '100%', height: '100%', background: 'var(--accent)', borderRadius: '3px' }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Intermediate</span>
              <span className="text-muted">Core Knowledge</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'var(--surface2)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '60%', height: '100%', background: 'var(--primary)', borderRadius: '3px' }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Advanced</span>
              <span className="text-muted">Deep Understanding</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'var(--surface2)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '30%', height: '100%', background: 'var(--warning)', borderRadius: '3px' }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Expert</span>
              <span className="text-muted">Cutting-edge</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'var(--surface2)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '10%', height: '100%', background: 'var(--danger)', borderRadius: '3px' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
