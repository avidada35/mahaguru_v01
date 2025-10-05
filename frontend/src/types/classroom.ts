/**
 * Type definitions for Classroom feature
 * 
 * Contains interfaces and types for:
 * - Chat messages and conversation flow
 * - Refinement suggestions and data
 * - API requests and responses
 * - Component props
 */

// Message Types
export interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp?: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  isRefined?: boolean;
  originalQuery?: string;
  refinementApplied?: string[];
}

// Refinement Types
export interface RefinementSuggestion {
  text: string;
  adds: string;
}

export interface RefinementData {
  needs_refinement: boolean;
  suggestions: RefinementSuggestion[];
  reasoning: string;
  original_query: string;
}

// API Response Types
export interface DirectResponse {
  type: 'direct_response';
  bot_message: string;
  timestamp?: string;
  success: boolean;
  source?: string;
}

export interface RefinementNeededResponse {
  type: 'refinement_needed';
  refinement_data: RefinementData;
  success: boolean;
}

// Backend Response Types (matches actual backend structure)
export interface BackendDirectResponse {
  response_type: 'direct_response';
  bot_message: string;
  timestamp?: string;
  success: boolean;
  source?: string;
}

export interface BackendRefinementNeededResponse {
  response_type: 'refinement_needed';
  refinement_data: RefinementData;
  success: boolean;
}

export type ClassroomApiResponse = DirectResponse | RefinementNeededResponse;
export type BackendClassroomApiResponse = BackendDirectResponse | BackendRefinementNeededResponse;

// API Request Type
export interface ClassroomChatRequest {
  user_message: string;
  user_id?: string;
  conversation_history?: Message[];
}

// Component Prop Types
export interface RefinementPanelProps {
  originalQuery: string;
  suggestions: RefinementSuggestion[];
  reasoning: string;
  selectedSuggestions: number[];
  onToggleSuggestion: (index: number) => void;
  onConfirm: () => void;
  onSkip: () => void;
}

// State Management Types
export interface ClassroomPageState {
  messages: Message[];
  input: string;
  showRefinement: boolean;
  refinementData: RefinementData | null;
  selectedSuggestions: number[];
  loading: boolean;
  error: string | null;
}

// Utility Types
export type ResponseType = 'direct_response' | 'refinement_needed';
export type SuggestionIndex = number;
export type ChatRole = 'user' | 'assistant';