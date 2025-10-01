import axios from 'axios';

export interface RefinedQueryResponse {
  original_query: string;
  refined_query: string;
  query_type: 'academic' | 'general';
  subject?: string;
  syllabus?: string;
  exam_focus?: string;
  missing_info: string[];
  suggestions: string[];
}

export const refineQuery = async (originalQuery: string): Promise<RefinedQueryResponse> => {
  try {
    const response = await axios.post<RefinedQueryResponse>(
      '/api/v1/refiner/refine',
      { original_query: originalQuery },
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
