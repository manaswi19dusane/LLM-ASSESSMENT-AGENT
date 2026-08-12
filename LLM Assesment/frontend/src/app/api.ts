const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface CreateSessionResponse {
  session_id: number;
  started_at: string;
}

export interface QuestionResponse {
  id: number;
  session_id: number;
  difficulty: string;
  question_text: string;
  asked_at: string;
}

export interface AnswerSubmit {
  question_id: number;
  user_answer: string;
  time_taken_seconds: number;
}

export interface AnswerResponse {
  question_id: number;
  is_correct: boolean;
  explanation: string;
  correct_answer: string;
  session_complete: boolean;
  difficulty_changed: boolean;
  new_difficulty?: string;
}

export interface SessionSummary {
  session_id: number;
  started_at: string;
  ended_at?: string;
  current_difficulty: string;
  total_questions: number;
  correct_answers: number;
  wrong_answers: number;
  accuracy: number;
}

export interface QuestionReviewItem {
  question_id: number;
  difficulty: string;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface SessionReview {
  session_id: number;
  total_questions: number;
  correct_answers: number;
  wrong_answers: number;
  accuracy: number;
  difficulty_progression: string[];
  questions: QuestionReviewItem[];
  recommendations: string[];
  weak_areas: string[];
  strong_areas: string[];
}

export interface PeriodStats {
  total_questions: number;
  correct_answers: number;
  wrong_answers: number;
  accuracy: number;
  sessions: number;
}

export interface TrendPoint {
  date: string;
  accuracy: number;
  questions_answered: number;
  average_difficulty: number;
}

export interface DashboardData {
  daily: PeriodStats;
  weekly: PeriodStats;
  monthly: PeriodStats;
  trend_data: TrendPoint[];
}

export async function createSession(): Promise<CreateSessionResponse> {
  return request('/sessions', { method: 'POST' });
}

export async function listSessions(): Promise<SessionSummary[]> {
  return request('/sessions');
}

export async function getSession(id: number): Promise<SessionSummary> {
  return request(`/sessions/${id}`);
}

export async function getNextQuestion(sessionId: number): Promise<QuestionResponse> {
  return request(`/questions/next/${sessionId}`, { method: 'POST' });
}

export async function submitAnswer(data: AnswerSubmit): Promise<AnswerResponse> {
  return request('/questions/answer', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSessionReview(sessionId: number): Promise<SessionReview> {
  return request(`/sessions/${sessionId}/review`);
}

export async function getDashboard(): Promise<DashboardData> {
  return request('/dashboard');
}
