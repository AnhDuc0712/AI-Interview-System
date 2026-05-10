export type UserRole = 'candidate' | 'interviewer' | 'admin';

export type UserProfile = {
  headline: string | null;
  biography: string | null;
  location: string | null;
  timezone: string | null;
  target_role: string | null;
  years_of_experience: number | null;
  skills: string[];
  preferences: Record<string, string>;
};

export type UserResponse = {
  user: {
    _id?: string;
    public_id: string;
    role: UserRole;
    clerk: {
      clerk_user_id: string;
      email: string | null;
      issuer: string | null;
      profile: {
        first_name: string | null;
        last_name: string | null;
        full_name: string | null;
        username: string | null;
        image_url: string | null;
      };
    };
    profile: UserProfile;
    metadata: {
      created_at: string;
      updated_at: string;
      last_sign_in_at: string;
      last_profile_updated_at: string | null;
      clerk_synced_at: string;
      profile_completion_score: number;
      profile_completion_fields_completed: number;
      profile_completion_fields_total: number;
      profile_completed_at: string | null;
    };
    state: {
      is_deleted: boolean;
      deleted_at: string | null;
    };
  };
  profile_completion: {
    score: number;
    fields_completed: number;
    fields_total: number;
    is_complete: boolean;
  };
};
