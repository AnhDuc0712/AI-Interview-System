import { create } from 'zustand';

type UploadFeedback = {
  cached: boolean;
  processingTimeSeconds: number | null;
  fileName: string;
  uploadedAt: number;
};

type AppState = {
  sidebarOpen: boolean;
  learningPlanSkills: string[];
  lastUploadFeedback: UploadFeedback | null;
  toggleSidebar: () => void;
  addSkillToLearningPlan: (skill: string) => void;
  removeSkillFromLearningPlan: (skill: string) => void;
  setLastUploadFeedback: (feedback: UploadFeedback) => void;
  clearLastUploadFeedback: () => void;
};

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: false,
  learningPlanSkills: [],
  lastUploadFeedback: null,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  addSkillToLearningPlan: (skill) =>
    set((state) => {
      if (state.learningPlanSkills.includes(skill)) {
        return state;
      }
      return {
        learningPlanSkills: [...state.learningPlanSkills, skill]
      };
    }),
  removeSkillFromLearningPlan: (skill) =>
    set((state) => ({
      learningPlanSkills: state.learningPlanSkills.filter((entry) => entry !== skill)
    })),
  setLastUploadFeedback: (feedback) => set({ lastUploadFeedback: feedback }),
  clearLastUploadFeedback: () => set({ lastUploadFeedback: null })
}));
