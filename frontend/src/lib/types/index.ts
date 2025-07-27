export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'MAINTAINER' | 'REPORTER';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Issue {
  id: number;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'TRIAGED' | 'IN_PROGRESS' | 'DONE';
  tags?: string;
  file_path?: string;
  file_name?: string;
  reporter_id: number;
  assignee_id?: number;
  created_at: string;
  updated_at?: string;
  reporter: User;
  assignee?: User;
}

export interface AIAnalysis {
  classification: {
    suggested_severity: string;
    suggested_tags: string[];
    category: string;
    confidence: number;
  };
  time_prediction: {
    estimated_hours: number;
    confidence: number;
    factors: string[];
  };
  assignment_suggestion: {
    user_id?: number;
    user_name?: string;
    confidence: number;
    reasoning: string;
  };
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface DashboardStats {
  total_issues: number;
  open_issues: number;
  triaged_issues: number;
  in_progress_issues: number;
  done_issues: number;
  issues_by_severity: Record<string, number>;
  recent_activity: Issue[];
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
