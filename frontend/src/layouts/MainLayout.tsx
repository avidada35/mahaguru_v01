import { Outlet } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import LeftRail from '@/components/layout/LeftRail';
import { ManthanButton } from '@/components/manthan';

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      {/* ManthanButton floating chat launcher */}
      <div className="fixed bottom-8 right-8 z-50">
        {/* Only show on desktop for now, can add mobile logic if needed */}
        <div className="hidden md:block">
          <ManthanButton />
        </div>
      </div>
      <div className="flex flex-1 min-h-0">
        {/* Left Rail */}
        <div className="hidden md:block">
          <LeftRail />
        </div>
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
      </div>
      <Footer />
      <Toaster />
    </div>
  );
}
