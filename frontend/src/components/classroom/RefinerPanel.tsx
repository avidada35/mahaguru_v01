import React from 'react';
import type { RefinedQueryResponse } from '../../services/refinerService';

export interface RefinerPanelProps {
  originalQuery: string;
  refinedData: RefinedQueryResponse;
  onAccept: (query: string) => void;
  onSkip: () => void;
  isLoading?: boolean;
  error?: string;
}

export const RefinerPanel: React.FC<RefinerPanelProps> = ({
  originalQuery,
  refinedData,
  onAccept,
  onSkip,
  isLoading,
  error,
}) => {
  // Interactive suggestion selection state
  const [selectedSuggestions, setSelectedSuggestions] = React.useState<boolean[]>(refinedData.suggestions.map(() => true));
  const [sliderValues, setSliderValues] = React.useState<number[]>(refinedData.suggestions.map(() => 1));
  // Real-time preview of refined query (simulate changes)
  const getPreviewQuery = () => {
    // For demo: only include suggestions that are checked
    let preview = refinedData.refined_query;
    refinedData.suggestions.forEach((s, idx) => {
      if (!selectedSuggestions[idx]) {
        preview = preview.replace(s, '');
      }
    });
    return preview.trim();
  };
  return (
    <div className="refiner-panel p-4 rounded shadow bg-white max-w-xl mx-auto">
      <h2 className="text-lg font-bold mb-2">Refined Query Preview</h2>
      <div className="mb-4">
        <span className="font-semibold">Refined:</span>
        <div className="text-blue-700 font-mono mt-1">{getPreviewQuery()}</div>
      </div>
      <div className="mb-2">
        <span className="font-semibold">Original:</span>
        <div className="text-gray-600 font-mono mt-1">{originalQuery}</div>
      </div>
      {refinedData.query_type === 'academic' && (
        <div className="mb-2">
          <div><span className="font-semibold">Subject:</span> {refinedData.subject || <span className="text-red-500">(missing)</span>}</div>
          <div><span className="font-semibold">Syllabus:</span> {refinedData.syllabus || <span className="text-red-500">(missing)</span>}</div>
          <div><span className="font-semibold">Exam Focus:</span> {refinedData.exam_focus || <span className="text-red-500">(missing)</span>}</div>
        </div>
      )}
      <div className="mb-2">
        <span className="font-semibold">Missing Info:</span>
        <ul className="list-disc ml-6">
          {refinedData.missing_info.map((info, idx) => (
            <li key={idx} className="text-red-600">{info}</li>
          ))}
        </ul>
      </div>
      <div className="mb-4">
        <span className="font-semibold">Suggestions:</span>
        <ul className="list-disc ml-6">
          {refinedData.suggestions.map((s, idx) => (
            <li key={idx} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedSuggestions[idx]}
                onChange={() => {
                  const updated = [...selectedSuggestions];
                  updated[idx] = !updated[idx];
                  setSelectedSuggestions(updated);
                }}
              />
              <span className="text-green-700 cursor-pointer hover:underline">{s}</span>
              <input
                type="range"
                min={1}
                max={3}
                value={sliderValues[idx]}
                onChange={e => {
                  const updated = [...sliderValues];
                  updated[idx] = Number(e.target.value);
                  setSliderValues(updated);
                }}
                className="ml-2"
              />
              <span className="text-xs text-gray-500">Level: {sliderValues[idx]}</span>
            </li>
          ))}
        </ul>
      </div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => onAccept(getPreviewQuery())}
          disabled={isLoading}
        >
          Accept
        </button>
        <button
          className="bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400"
          onClick={onSkip}
          disabled={isLoading}
        >
          Skip
        </button>
      </div>
      {isLoading && <div className="mt-2 text-gray-500">Refining...</div>}
    </div>
  );
};
