import { Outlet, useLocation } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import LeftRail from '@/components/layout/LeftRail';

export default function MainLayout() {
  const location = useLocation();
  
  // Show footer only on homepage
  const showFooter = location.pathname === '/';

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 min-h-0">
        {/* Left Rail */}
        <div className="hidden md:block">
          <LeftRail />
        </div>
        {/* Main Content Area - Takes full remaining space */}
        <main className="flex-1 min-w-0 min-h-0 flex flex-col">
          <Outlet />
        </main>
      </div>
      {showFooter && <Footer />}
      <Toaster />
    </div>
  );
}