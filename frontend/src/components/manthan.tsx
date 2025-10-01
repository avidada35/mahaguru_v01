import { Link } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';

export function ManthanButton() {
  return (
    <Link
      to="/studentgpt"
      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white transition-colors rounded-lg bg-sky-500 hover:bg-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
    >
      <BrainCircuit className="w-5 h-5" />
      <span>Manthan AI</span>
    </Link>
  );
}
