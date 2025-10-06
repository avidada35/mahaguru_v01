
import type { RefinementPanelProps } from '@/types/classroom';

const RefinementPanel = ({
  originalQuery,
  suggestions,
  reasoning,
  selectedSuggestions,
  onToggleSuggestion,
  onConfirm,
  onSkip,
}: RefinementPanelProps) => {
  const handleToggle = (index: number) => {
    onToggleSuggestion(index);
  };

  const handleSuggestionRowClick = (index: number) => {
    handleToggle(index);
  };

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

      {/* Suggestions */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">Suggested improvements:</label>
        {suggestions.length === 0 ? (
          <div className="text-center py-6 px-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-medium">No refinements suggested. Your query is already clear! ✓</p>
          </div>
        ) : (
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                onClick={() => handleSuggestionRowClick(index)}
                className="flex items-start gap-3 p-4 rounded-lg border border-blue-100 hover:bg-blue-100/70 hover:border-blue-200 cursor-pointer transition-all duration-200 ease-in-out"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSuggestionRowClick(index);
                  }
                }}
                aria-label={`Toggle suggestion: ${suggestion.text}`}
              >
                <input
                  id={`suggestion-${index}`}
                  type="checkbox"
                  checked={selectedSuggestions.includes(index)}
                  onChange={() => handleToggle(index)}
                  onClick={(e) => e.stopPropagation()}
                  className="mt-0.5 h-4 w-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500 focus:ring-2 flex-shrink-0"
                  aria-describedby={`suggestion-${index}-description`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-800 font-medium leading-relaxed">{suggestion.text}</p>
                  <p 
                    id={`suggestion-${index}-description`}
                    className="text-xs text-gray-500 mt-1.5 font-medium"
                  >
                    → Adds: {suggestion.adds}
                  </p>
                </div>
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
          onClick={onConfirm}
          className="px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 focus:bg-sky-700 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 transition-all duration-200 flex-1 font-semibold"
          aria-label="Send refined query with selected suggestions"
        >
          Send Refined Query ✓
        </button>
      </div>
    </div>
  );
};

export default RefinementPanel;