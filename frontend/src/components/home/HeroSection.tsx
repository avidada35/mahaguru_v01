import { useState } from 'react';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface HeroSectionProps {
  // onSearch is now optional since HeroSection handles navigation directly
  onSearch?: (query: string) => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({ onSearch }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [selectedMode, setSelectedMode] = useState<string>('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      if (selectedMode === 'Brainstorming') {
        // Navigate to StudentGPT with the query
        navigate(`/studentgpt?query=${encodeURIComponent(searchQuery)}`);
      } else if (selectedMode === 'Classroom') {
        // Navigate to Classroom chat with the query - this connects to classroom.ts → main.py → classroom.py
        navigate(`/classroom/chat?query=${encodeURIComponent(searchQuery)}`);
      } else {
        // Fallback: if no mode selected and onSearch is provided, use it
        if (onSearch) {
          onSearch(searchQuery);
        } else {
          // Default: treat as general search/classroom if no mode selected
          navigate(`/classroom/chat?query=${encodeURIComponent(searchQuery)}`);
        }
      }
    }
  };

  const handleChipClick = (mode: string) => {
    setSelectedMode(mode);
    let starterText = '';
    switch (mode) {
      case 'Brainstorming':
        starterText = "What's going on in your mind?";
        break;
      case 'Classroom':
        starterText = "Let's learn together...";
        break;
      default:
        starterText = mode;
    }
    setSearchQuery(starterText);
  };

  const quickActionChips = [
    {
      id: 'manthan',
      label: 'Brainstorming',
      description: 'Brainstorm & Ideate'
    },
    {
      id: 'vidya',
      label: 'Classroom',
      description: 'Wisdom & Knowledge'
    },
  ];

  return (
    <section className="mg-sky mg-neurogrid text-ink relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 0.8, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <h3 className="text-5xl md:text-6xl font-serif font-bold text-ink mb-6">
          नमस्ते, Let's begin.
          </h3>
          <p className="text-xl text-muted max-w-2xl mx-auto leading-relaxed">
            Guidance for mind, heart, and path.
          </p>
        </motion.div>

        {/* Supreme Search Bar */}
        <motion.div 
          className="relative max-w-3xl mx-auto"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
        >
          <form onSubmit={handleSearch}>
            <div className={`relative ${isFocused ? 'ring-2 ring-primary ring-offset-4' : ''} rounded-2xl shadow-lg border border-sky-200 bg-surface transition-all duration-300 p-6`}>
              <div className="flex items-start space-x-4">
                <div className="flex-1">
                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    className="block w-full bg-transparent outline-none text-ink placeholder:text-muted text-xl md:text-2xl placeholder:leading-snug py-6 border-0 focus:ring-0 resize-none"
                    placeholder="Describe your dilemma in one line — I'll help you think."
                    aria-label="Clarity input"
                  />
                  
                  {/* Quick Action Chips */}
                  <div className="flex flex-wrap gap-3 mt-4">
                    {quickActionChips.map((chip) => (
                      <motion.button
                        key={chip.id}
                        type="button"
                        onClick={() => handleChipClick(chip.label)}
                        className={`px-4 py-2 rounded-full border transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                          selectedMode === chip.label
                            ? 'bg-white border-primary text-primary shadow-sm'
                            : 'bg-sky-100 border-sky-200 text-ink/80 hover:bg-white hover:text-ink hover:shadow-sm'
                        }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        aria-label={`Use ${chip.label} mode: ${chip.description}`}
                      >
                        {chip.label}
                      </motion.button>
                    ))}
                  </div>
                </div>
                
                <button
                  type="submit"
                  className="ml-3 shrink-0 inline-flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-primary to-primary-600 shadow-[0_6px_20px_rgba(58,130,247,0.35)] ring-1 ring-ring hover:translate-y-[-1px] active:translate-y-[0px] transition-transform"
                  aria-label="Send"
                >
                  <Send className="h-5 w-5 text-white" strokeWidth={2} />
                </button>
              </div>
            </div>
          </form>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
