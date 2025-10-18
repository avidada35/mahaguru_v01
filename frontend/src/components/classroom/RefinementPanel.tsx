
import { useState, useEffect } from 'react';
import type { RefinementSuggestion } from '@/types/classroom';

interface RefinementPanelProps {
  originalQuery: string;
  suggestions: RefinementSuggestion[];
  reasoning: string;
  onSubmitAnswers: (answers: Array<{ question_id: string; answer: string }>) => void;
  onSkip: () => void;
}

const RefinementPanel = ({
  originalQuery,
  suggestions,
  reasoning,
  onSubmitAnswers,
  onSkip,
}: RefinementPanelProps) => {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  // Sync answers state when suggestions change
  useEffect(() => {
    setAnswers(prev => {
      const newAnswers: Record<string, string> = {};
      suggestions.forEach(s => {
        newAnswers[s.question_id] = prev[s.question_id] || '';
      });
      return newAnswers;
    });
  }, [suggestions]);

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmit = () => {
    const answerArray = suggestions.map(suggestion => ({
      question_id: suggestion.question_id,
      answer: answers[suggestion.question_id] || ''
    }));
    onSubmitAnswers(answerArray);
  };

  const hasAllAnswers = suggestions.every(suggestion => 
    answers[suggestion.question_id]?.trim().length > 0
  );

  // Debug logging
  console.log('Suggestions question_ids:', suggestions.map(s => s.question_id));
  console.log('Answers state:', answers);

  return (
    <div className="my-4 p-6 bg-blue-50 border border-blue-200 rounded-xl shadow-sm">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl" role="img" aria-label="lightbulb">💡</span>
          <h3 className="text-lg font-semibold text-gray-800">Let's refine your question</h3>
        </div>
        <p className="text-gray-600 text-sm leading-relaxed">{reasoning}</p>
      </div>

      {/* Original Query */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Your question:</label>
        <div className="bg-gray-100 p-4 rounded-lg border border-gray-200">
          <p className="text-gray-800">{originalQuery}</p>
        </div>
      </div>

      {/* Questions */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">Please answer these questions:</label>
        {suggestions.length === 0 ? (
          <div className="text-center py-6 px-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-medium">No refinements suggested. Your query is already clear! ✓</p>
          </div>
        ) : (
          <div className="space-y-4">
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion.question_id}
                className="p-4 rounded-lg border border-blue-100 bg-white"
              >
                <div className="mb-3">
                  <label 
                    htmlFor={`answer-${suggestion.question_id}`}
                    className="block text-gray-800 font-medium leading-relaxed mb-1"
                  >
                    {index + 1}. {suggestion.text}
                  </label>
                  <p className="text-xs text-gray-500 font-medium">
                    → This helps us understand: {suggestion.adds}
                  </p>
                </div>
                <textarea
                  id={`answer-${suggestion.question_id}`}
                  value={answers[suggestion.question_id] || ''}
                  onChange={(e) => handleAnswerChange(suggestion.question_id, e.target.value)}
                  placeholder="Type your answer here..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 resize-none"
                  rows={2}
                  aria-describedby={`suggestion-${suggestion.question_id}-description`}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onSkip}
          className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:bg-gray-600 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 font-medium"
          aria-label="Skip refinement and use original query"
        >
          Skip Refinement
        </button>
        <button
          onClick={handleSubmit}
          disabled={!hasAllAnswers}
          className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 flex-1 focus:ring-2 focus:ring-offset-2 ${
            hasAllAnswers
              ? 'bg-sky-600 text-white hover:bg-sky-700 focus:bg-sky-700 focus:ring-sky-500'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          aria-label="Submit answers to continue refinement"
        >
          Submit Answers ✓
        </button>
      </div>
    </div>
  );
};

export default RefinementPanel;