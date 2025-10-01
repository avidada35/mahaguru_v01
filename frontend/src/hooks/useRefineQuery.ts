import { useMutation } from '@tanstack/react-query';
import { refineQuery, RefinedQueryResponse } from '../services/refinerService';

export const useRefineQuery = () => {
  return useMutation<RefinedQueryResponse, Error, string>({
    mutationFn: refineQuery,
    onSuccess: (data) => {
      // Optionally handle success globally
    },
    onError: (error) => {
      // Optionally handle error globally
    },
  });
};
