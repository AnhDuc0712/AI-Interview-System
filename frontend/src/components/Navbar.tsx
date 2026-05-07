import { NavLink } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, SignOutButton } from '@clerk/clerk-react';

const Navbar = () => (
  <header className="border-b border-slate-200 bg-white">
    <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
      <NavLink to="/" className="text-xl font-semibold text-slate-900">
        AI Interview
      </NavLink>
      <nav className="flex items-center gap-2">
        <NavLink to="/" className={({ isActive }) => (isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900')}>
          Home
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'text-slate-900 font-semibold' : 'text-slate-600 hover:text-slate-900')}>
          Dashboard
        </NavLink>
        <SignedIn>
          <SignOutButton>
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
              Sign out
            </button>
          </SignOutButton>
        </SignedIn>
        <SignedOut>
          <SignInButton>
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">
              Sign in
            </button>
          </SignInButton>
        </SignedOut>
      </nav>
    </div>
  </header>
);

export default Navbar;
