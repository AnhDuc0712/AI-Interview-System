import { create } from 'zustand';

type AppState = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
};

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
}));
