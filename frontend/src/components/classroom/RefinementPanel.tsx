
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
  console.log('RefinementPanel mounted with:', { originalQuery, suggestions, selectedSuggestions });

  const handleToggle = (index: number) => {
    console.log('Checkbox toggled for index:', index);
    onToggleSuggestion(index);
  };

  const handleConfirm = () => {
    console.log('Confirm button clicked');
    onConfirm();
  };

  const handleSkip = () => {
    console.log('Skip button clicked');
    onSkip();
  };

  return (
    <div className="my-4 p-6 bg-blue-50 border border-blue-200 rounded-xl">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">💡</span>
          <h3 className="text-lg font-semibold text-gray-800">Let's refine your question</h3>
        </div>
        <p className="text-gray-500 text-sm">{reasoning}</p>
      </div>

      {/* Original Query */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Your question:</label>
        <div className="bg-gray-100 p-3 rounded-lg">
          <p className="text-gray-800 font-medium">{originalQuery}</p>
        </div>
      </div>

      {/* Suggestions */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">Suggested improvements:</label>
        {suggestions.length === 0 ? (
          <p className="text-gray-500 text-sm italic">No refinements suggested. Your query is already clear!</p>
        ) : (
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <label
                key={index}
                htmlFor={`suggestion-${index}`}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-blue-100/50 cursor-pointer transition-colors duration-150"
              >
                <input
                  id={`suggestion-${index}`}
                  type="checkbox"
                  checked={selectedSuggestions.includes(index)}
                  onChange={() => handleToggle(index)}
                  className="mt-0.5 h-4 w-4 text-sky-600 border-gray-300 rounded focus:ring-sky-500 flex-shrink-0"
                />
                <div className="flex-1">
                  <span className="text-gray-800">{suggestion.text}</span>
                  <div className="text-xs text-gray-500 mt-1">→ Adds: {suggestion.adds}</div>
                </div>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={handleSkip}
          className="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition-colors"
          aria-label="Skip refinement and use original query"
        >
          Skip Refinement
        </button>
        <button
          onClick={handleConfirm}
          className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors flex-1 font-medium"
          aria-label="Send refined query with selected suggestions"
        >
          Send Refined Query ✓
        </button>
      </div>
    </div>
  );
};

export default RefinementPanel;