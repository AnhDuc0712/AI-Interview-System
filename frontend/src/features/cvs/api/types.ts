export type CVStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type CVRecord = {
  _id?: string;
  public_id: string;
  ownership: {
    user_public_id: string;
    user_role: string;
  };
  status: CVStatus;
  original_file: {
    original_filename: string;
    content_type: string;
    file_type: 'pdf' | 'docx';
    size_bytes: number;
  };
  stored_file: {
    provider: 'local';
    path: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    checksum_sha256: string;
    uploaded_at: string;
  };
  extraction: {
    extractor_name: string;
    extractor_version: string;
    extracted_at: string | null;
    raw_text_length: number;
    normalized_text_length: number;
  };
  parser: {
    parser_name: string;
    parser_version: string;
    parsed_at: string | null;
  };
  normalized_content: {
    personal_info: {
      full_name: string | null;
      email: string | null;
      phone: string | null;
      location: string | null;
      summary: string | null;
    };
    skills: string[];
    experience: Array<{
      title: string;
      company: string | null;
      start_date: string | null;
      end_date: string | null;
      description: string | null;
    }>;
    education: Array<{
      institution: string;
      degree: string | null;
      field_of_study: string | null;
      graduation_date: string | null;
    }>;
    projects: Array<{
      name: string;
      description: string | null;
    }>;
    certifications: string[];
    languages: string[];
    raw_sections: Record<string, string[]>;
  } | null;
  normalized_text: string | null;
  metadata: {
    created_at: string;
    updated_at: string;
    processing_started_at: string | null;
    processing_completed_at: string | null;
    failed_at: string | null;
    last_error: string | null;
  };
};

export type CVUploadResponse = {
  cv: CVRecord;
};

export type CVListResponse = {
  items: CVRecord[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
};

export type CVDetailResponse = {
  cv: CVRecord;
};
