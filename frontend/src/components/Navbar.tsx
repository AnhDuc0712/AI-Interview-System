import { NavLink } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, SignOutButton } from '@clerk/clerk-react';

const navLinkClassName = (isActive: boolean) =>
  isActive
    ? 'rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-950'
    : 'rounded-full px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 hover:text-slate-950';

const Navbar = () => (
  <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
    <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
      <NavLink to="/" className="text-xl font-semibold tracking-tight text-slate-950">
        AI Interview System
      </NavLink>
      <nav className="flex items-center gap-2">
        <NavLink to="/" className={({ isActive }) => navLinkClassName(isActive)}>
          Home
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => navLinkClassName(isActive)}>
          Dashboard
        </NavLink>
        <NavLink to="/cvs" className={({ isActive }) => navLinkClassName(isActive)}>
          My CVs
        </NavLink>
        <SignedIn>
          <SignOutButton>
            <button className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
              Sign out
            </button>
          </SignOutButton>
        </SignedIn>
        <SignedOut>
          <SignInButton>
            <button className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
              Sign in
            </button>
          </SignInButton>
        </SignedOut>
      </nav>
    </div>
  </header>
);

export default Navbar;
