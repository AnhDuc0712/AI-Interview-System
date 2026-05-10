import { Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import MyCVsPage from './pages/MyCVsPage';
import CVDetailPage from './pages/CVDetailPage';
import NotFoundPage from './pages/NotFoundPage';
import Navbar from './components/Navbar';
import AuthenticatedLayout from './features/auth/AuthenticatedLayout';
import { ProtectedRoute } from './features/auth/ProtectedRoute';

const App = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AuthenticatedLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/cvs" element={<MyCVsPage />} />
            <Route path="/cvs/:publicId" element={<CVDetailPage />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
};

export default App;
