'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import {
  getNextQuestion,
  submitAnswer,
  QuestionResponse,
  AnswerResponse,
} from '@/app/api';

export default function AssessmentPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = Number(params.id);

  const [question, setQuestion] = useState<QuestionResponse | null>(null);
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState<AnswerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState({ answered: 0, correct: 0, total: 0 });
  const [difficulty, setDifficulty] = useState('beginner');
  const startTime = useRef(Date.now());

  const fetchQuestion = async () => {
    setLoading(true);
    setResult(null);
    setAnswer('');
    try {
      const q = await getNextQuestion(sessionId);
      setQuestion(q);
      setDifficulty(q.difficulty);
      startTime.current = Date.now();
    } catch (e) {
      console.error('Failed to get question:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestion();
  }, [sessionId]);

  const handleSubmit = async () => {
    if (!question || !answer.trim()) return;
    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - startTime.current) / 1000);
    try {
      const res = await submitAnswer({
        question_id: question.id,
        user_answer: answer,
        time_taken_seconds: timeTaken,
      });
      setResult(res);
      setProgress((p) => ({
        answered: p.answered + 1,
        correct: p.correct + (res.is_correct ? 1 : 0),
        total: p.total + 1,
      }));
      if (res.difficulty_changed) {
        setDifficulty(res.new_difficulty || difficulty);
      }
    } catch (e) {
      console.error('Failed to submit answer:', e);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (result?.session_complete) {
      router.push(`/review/${sessionId}`);
    } else {
      fetchQuestion();
    }
  };

  return (
    <div className="container">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-muted text-sm">Session #{sessionId}</span>
        </div>
        <div className="flex items-center gap-4">
          {progress.answered > 0 && (
            <span className="text-sm text-muted">
              {progress.correct}/{progress.answered} correct
            </span>
          )}
          <span className={`badge badge-${difficulty}`}>{difficulty}</span>
          <button className="btn btn-sm btn-secondary" onClick={() => router.push('/dashboard')}>
            Dashboard
          </button>
        </div>
      </div>

      {loading && (
        <div className="card text-center" style={{ padding: '60px' }}>
          <p className="text-muted">Generating question...</p>
        </div>
      )}

      {question && !result && !loading && (
        <div className="card">
          <div className="card-header">Question</div>
          <p style={{ fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '20px' }}>
            {question.question_text}
          </p>
          <div className="flex flex-col gap-2">
            <textarea
              className="textarea"
              placeholder="Type your answer here..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={submitting}
            />
            <div className="flex gap-2">
              <button
                className="btn"
                onClick={handleSubmit}
                disabled={!answer.trim() || submitting}
              >
                {submitting ? 'Evaluating...' : 'Submit Answer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="card">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px',
          }}>
            <span style={{
              fontSize: '1.5rem',
              color: result.is_correct ? 'var(--accent)' : 'var(--danger)',
            }}>
              {result.is_correct ? '✓' : '✗'}
            </span>
            <span style={{
              fontWeight: 600,
              fontSize: '1.1rem',
              color: result.is_correct ? 'var(--accent)' : 'var(--danger)',
            }}>
              {result.is_correct ? 'Correct!' : 'Incorrect'}
            </span>
          </div>

          <p className="text-sm" style={{ marginBottom: '12px' }}>
            <strong>Your answer:</strong> {answer}
          </p>
          <p className="text-sm" style={{ marginBottom: '12px' }}>
            <strong>Correct answer:</strong> {result.correct_answer}
          </p>
          <p className="text-sm text-muted" style={{ marginBottom: '16px', lineHeight: '1.5' }}>
            <strong>Explanation:</strong> {result.explanation}
          </p>

          {result.difficulty_changed && (
            <div style={{
              background: 'var(--accent)',
              color: '#0f0f1a',
              padding: '8px 16px',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '16px',
              fontWeight: 600,
              fontSize: '0.9rem',
            }}>
              Level up! Difficulty increased to {result.new_difficulty}
            </div>
          )}

          <button className="btn" onClick={handleNext}>
            {result.session_complete ? 'View Results' : 'Next Question'}
          </button>
        </div>
      )}

      {progress.answered > 0 && (
        <div className="card">
          <div className="card-header">Session Progress</div>
          <div style={{
            width: '100%',
            height: '8px',
            background: 'var(--surface2)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}>
            <div style={{
              width: `${Math.min((progress.answered / 20) * 100, 100)}%`,
              height: '100%',
              background: 'var(--primary)',
              borderRadius: '4px',
              transition: 'width 0.3s',
            }} />
          </div>
          <p className="text-sm text-muted mt-4">
            {progress.answered} questions answered ({progress.correct} correct, {progress.answered - progress.correct} wrong)
          </p>
        </div>
      )}
    </div>
  );
}
