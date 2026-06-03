import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import UploadPage from './pages/UploadPage';
import RecordsPage from './pages/RecordsPage';
import SearchPage from './pages/SearchPage';

export default function App() {
  return (
    <BrowserRouter>
      {/* Subtle grid background */}
      <div className="min-h-screen bg-navy-900 bg-grid-pattern bg-grid">
        <Navbar />
        <main className="pb-20">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/records" element={<RecordsPage />} />
            <Route path="/search" element={<SearchPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <div className="border-t border-white/5 py-5 text-center text-xs text-slate-600">
          ShipMail Extractor · Shipping Email Segregation &amp; Data Extraction System
        </div>
      </div>
    </BrowserRouter>
  );
}
