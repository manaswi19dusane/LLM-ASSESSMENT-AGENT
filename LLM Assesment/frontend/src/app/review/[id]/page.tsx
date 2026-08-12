'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { getSessionReview, SessionReview } from '@/app/api';

export default function ReviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = Number(params.id);
  const [review, setReview] = useState<SessionReview | null>(null);

  useEffect(() => {
    getSessionReview(sessionId).then(setReview).catch(console.error);
  }, [sessionId]);

  if (!review) {
    return (
      <div className="container">
        <div className="card text-center" style={{ padding: '60px' }}>
          <p className="text-muted">Loading review...</p>
        </div>
      </div>
    );
  }

  const chartData = review.questions.map((q, i) => ({
    question: i + 1,
    correct: q.is_correct ? 100 : 0,
    difficulty: ['beginner', 'intermediate', 'advanced', 'expert'].indexOf(q.difficulty),
  }));

  return (
    <div className="container">
      <div className="flex items-center justify-between mb-4">
        <h2 style={{ fontSize: '1.5rem' }}>Session Review</h2>
        <div className="flex gap-2">
          <button className="btn btn-sm btn-secondary" onClick={() => router.push('/dashboard')}>
            Dashboard
          </button>
          <button className="btn btn-sm" onClick={() => router.push('/')}>
            Home
          </button>
        </div>
      </div>

      <div className="card text-center" style={{ padding: '32px' }}>
        <div className="grid-3">
          <div>
            <div className="stat-value">{review.total_questions}</div>
            <div className="stat-label">Questions</div>
          </div>
          <div>
            <div className="stat-value correct-text">{review.correct_answers}</div>
            <div className="stat-label">Correct</div>
          </div>
          <div>
            <div className="stat-value wrong-text">{review.wrong_answers}</div>
            <div className="stat-label">Wrong</div>
          </div>
        </div>
        <div style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          border: '6px solid var(--primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '16px auto 0',
          fontSize: '1.8rem',
          fontWeight: 700,
          color: review.accuracy >= 70 ? 'var(--accent)' : review.accuracy >= 40 ? 'var(--warning)' : 'var(--danger)',
        }}>
          {review.accuracy}%
        </div>
      </div>

      <div className="card">
        <div className="card-header">Difficulty Progression</div>
        <div className="flex gap-2">
          {review.difficulty_progression.map((d, i) => (
            <span key={i} className={`badge badge-${d}`}>{d}</span>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">Performance by Question</div>
        <div className="chart-container" style={{ height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="question" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
              <YAxis stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} domain={[0, 3]} />
              <Tooltip
                contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text)' }}
              />
              <Line type="stepAfter" dataKey="difficulty" stroke="var(--warning)" strokeWidth={2} dot={{ fill: 'var(--warning)' }} name="Difficulty Level" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Question Review</div>
        {review.questions.map((q) => (
          <div key={q.question_id} className={`review-item ${q.is_correct ? 'correct' : 'wrong'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`badge badge-${q.difficulty}`}>{q.difficulty}</span>
              <span style={{ color: q.is_correct ? 'var(--accent)' : 'var(--danger)', fontWeight: 600 }}>
                {q.is_correct ? 'Correct' : 'Wrong'}
              </span>
            </div>
            <p className="text-sm" style={{ marginBottom: '8px', lineHeight: '1.5' }}>{q.question_text}</p>
            <div className="text-sm">
              <p><strong>Your answer:</strong> {q.user_answer}</p>
              <p><strong>Correct answer:</strong> {q.correct_answer}</p>
            </div>
            <p className="text-sm text-muted" style={{ marginTop: '8px', lineHeight: '1.4' }}>
              {q.explanation}
            </p>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">Recommendations</div>

        <div style={{ marginBottom: '16px' }}>
          <p className="text-sm font-bold" style={{ color: 'var(--accent)', marginBottom: '8px' }}>Strong Areas</p>
          <div className="flex gap-2 flex-wrap">
            {review.strong_areas.map((area, i) => (
              <span key={i} className="badge badge-beginner">{area}</span>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <p className="text-sm font-bold" style={{ color: 'var(--danger)', marginBottom: '8px' }}>Weak Areas</p>
          <div className="flex gap-2 flex-wrap">
            {review.weak_areas.map((area, i) => (
              <span key={i} className="badge badge-advanced">{area}</span>
            ))}
          </div>
        </div>

        <div>
          <p className="text-sm font-bold" style={{ marginBottom: '8px' }}>Study Recommendations</p>
          <ul style={{ paddingLeft: '20px', lineHeight: '2' }}>
            {review.recommendations.map((r, i) => (
              <li key={i} className="text-sm">{r}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
