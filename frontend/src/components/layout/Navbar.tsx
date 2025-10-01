import { useState } from 'react';
import { Menu, X, BookOpen } from 'lucide-react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-30 bg-sky-100/90 backdrop-blur-sm border-b border-sky-200 shadow-sm"
    >
      <nav className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-center">
          {/* Brand Name */}
          <span className="text-base sm:text-lg font-semibold tracking-wide text-ink/90">Mahaguru AI</span>
        </div>
      </nav>

      {/* Mobile menu button */}
      <div className="md:hidden absolute top-4 right-4">
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="inline-flex items-center justify-center p-2 rounded-md text-ink hover:text-primary focus:outline-none"
        >
          <span className="sr-only">Open main menu</span>
          {isMobileMenuOpen ? (
            <X className="block h-6 w-6" aria-hidden="true" />
          ) : (
            <Menu className="block h-6 w-6" aria-hidden="true" />
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white shadow-lg rounded-b-lg mt-16">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <a
              href="#"
              className="block px-3 py-2 rounded-md text-base font-medium text-ink hover:bg-sky-50 hover:text-primary"
            >
              <BookOpen className="w-5 h-5 inline-block mr-2" />
              Classroom
            </a>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
