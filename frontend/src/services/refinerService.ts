import axios from 'axios';
import { 
  RefinementData, 
  UserAnswer, 
  ContinueRefinementRequest, 
  ContinueRefinementResponse 
} from '../types/classroom';

// Note: The current backend uses ClassroomChatRequest/Response, not direct refiner endpoints
// This service handles refinement through the classroom chat API

export interface ClassroomChatRequest {
  user_message: string;
  user_id?: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ClassroomChatResponse {
  response_type: 'direct_response' | 'refinement_needed';
  bot_message?: string;
  source?: string;
  refinement_data?: RefinementData;
  timestamp: string;
  success: boolean;
}

export const refineQuery = async (originalQuery: string): Promise<ClassroomChatResponse> => {
  try {
    const response = await axios.post<ClassroomChatResponse>(
      '/api/v1/classroom/chat',
      { 
        user_message: originalQuery,
        user_id: 'default_user'
      } as ClassroomChatRequest,
      { timeout: 10000 }
    );
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // API returned error response
      throw new Error(error.response.data?.detail || 'Refiner API error');
    } else if (error.request) {
      // Network error
      throw new Error('Network error: Unable to reach Refiner API');
    } else {
      // Other errors
      throw new Error(error.message || 'Unknown error');
    }
  }
};

export const continueRefinement = async (
  originalQuery: string, 
  answers: UserAnswer[]
): Promise<ContinueRefinementResponse> => {
  try {
    const response = await axios.post<ContinueRefinementResponse>(
      '/api/v1/refiner/continue',
      { 
        original_query: originalQuery,
        answers: answers
      } as ContinueRefinementRequest,
      { timeout: 10000 }
    );
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // API returned error response
      throw new Error(error.response.data?.detail || 'Continue refinement API error');
    } else if (error.request) {
      // Network error
      throw new Error('Network error: Unable to reach Continue Refinement API');
    } else {
      // Other errors
      throw new Error(error.message || 'Unknown error');
    }
  }
};
