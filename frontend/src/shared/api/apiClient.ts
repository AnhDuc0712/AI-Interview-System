const FALLBACK_API_PORT = '8000';
const FALLBACK_API_PREFIX = '/api/v1';
const UNAUTHORIZED_STATUS = 401;
const MAX_AUTH_RETRY_ATTEMPTS = 1;

const normalizeBaseUrl = (value: string): string => value.replace(/\/+$/, '');

const resolveApiBaseUrl = (): string => {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  const currentHost = window.location.hostname;
  const isLanHost =
    currentHost !== 'localhost' &&
    currentHost !== '127.0.0.1' &&
    currentHost !== '';

  if (configuredBaseUrl) {
    const parsedUrl = new URL(configuredBaseUrl, window.location.origin);
    const usesLocalhostTarget =
      parsedUrl.hostname === 'localhost' || parsedUrl.hostname === '127.0.0.1';

    if (isLanHost && usesLocalhostTarget) {
      parsedUrl.hostname = currentHost;
    }

    return normalizeBaseUrl(parsedUrl.toString());
  }

  const protocol = window.location.protocol || 'http:';
  const hostname = currentHost || 'localhost';
  return `${protocol}//${hostname}:${FALLBACK_API_PORT}${FALLBACK_API_PREFIX}`;
};

const apiBaseUrl = resolveApiBaseUrl();

export type TokenProvider = (options?: {
  skipCache?: boolean;
}) => Promise<string | null>;

export type AuthenticatedRequestOptions = RequestInit & {
  retryOnUnauthorized?: boolean;
};

type AuthenticatedRequestConfig = {
  path: string;
  getToken: TokenProvider;
  options?: AuthenticatedRequestOptions;
  contentType?: string | null;
};

type UploadAuthenticatedFileParams = {
  path: string;
  file: File;
  fieldName?: string;
  getToken: TokenProvider;
  onProgress?: (progress: number) => void;
};

export type UploadResponseMeta = {
  headers: Record<string, string>;
  status: number;
};

export type UploadWithMetaResponse<T> = {
  data: T;
  meta: UploadResponseMeta;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const parseErrorMessage = async (response: Response): Promise<string> => {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    const body = await response.json().catch(() => null);
    if (body && typeof body.detail === 'string') {
      return body.detail;
    }
  }

  const errorBody = await response.text();
  return errorBody || 'Request failed';
};

const getFreshToken = async (getToken: TokenProvider): Promise<string> => {
  const token = await getToken({
    skipCache: true
  });

  if (!token) {
    throw new ApiError('Authentication token is unavailable', UNAUTHORIZED_STATUS);
  }

  return token;
};

const createHeaders = (
  headers?: HeadersInit,
  contentType: string | null = 'application/json'
): Headers => {
  const requestHeaders = new Headers(headers);
  if (contentType) {
    requestHeaders.set('Content-Type', contentType);
  }
  return requestHeaders;
};

const createAuthenticatedRequestInit = async (
  options: AuthenticatedRequestOptions | undefined,
  getToken: TokenProvider,
  contentType: string | null
): Promise<RequestInit> => {
  const requestHeaders = createHeaders(options?.headers, contentType);
  const token = await getFreshToken(getToken);
  requestHeaders.set('Authorization', `Bearer ${token}`);

  return {
    ...options,
    headers: requestHeaders
  };
};

const shouldRetryUnauthorized = (
  status: number,
  retryAttempt: number,
  retryOnUnauthorized: boolean
): boolean =>
  status === UNAUTHORIZED_STATUS &&
  retryOnUnauthorized &&
  retryAttempt < MAX_AUTH_RETRY_ATTEMPTS;

const performAuthenticatedFetch = async (
  config: AuthenticatedRequestConfig,
  retryAttempt = 0
): Promise<Response> => {
  const { getToken, options, path, contentType = 'application/json' } = config;
  const retryOnUnauthorized = options?.retryOnUnauthorized ?? true;
  const requestInit = await createAuthenticatedRequestInit(options, getToken, contentType);
  const response = await fetch(`${apiBaseUrl}${path}`, requestInit);

  if (shouldRetryUnauthorized(response.status, retryAttempt, retryOnUnauthorized)) {
    return performAuthenticatedFetch(config, retryAttempt + 1);
  }

  return response;
};

const handleJsonResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  return response.json();
};

const uploadWithFreshToken = async <T>(
  params: UploadAuthenticatedFileParams,
  retryAttempt = 0
): Promise<UploadWithMetaResponse<T>> => {
  const { file, fieldName = 'file', getToken, onProgress, path } = params;
  const token = await getFreshToken(getToken);

  return new Promise<UploadWithMetaResponse<T>>((resolve, reject) => {
    const formData = new FormData();
    formData.append(fieldName, file);

    const request = new XMLHttpRequest();
    request.open('POST', `${apiBaseUrl}${path}`);
    request.responseType = 'json';
    request.setRequestHeader('Authorization', `Bearer ${token}`);

    request.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };

    request.onload = async () => {
      const status = request.status;
      const response = request.response;
      const rawHeaders = request.getAllResponseHeaders();
      const headers = rawHeaders
        .trim()
        .split(/[\r\n]+/)
        .filter(Boolean)
        .reduce<Record<string, string>>((accumulator, line) => {
          const separatorIndex = line.indexOf(':');
          if (separatorIndex === -1) {
            return accumulator;
          }
          const key = line.slice(0, separatorIndex).trim().toLowerCase();
          const value = line.slice(separatorIndex + 1).trim();
          accumulator[key] = value;
          return accumulator;
        }, {});

      if (status >= 200 && status < 300) {
        resolve({
          data: response as T,
          meta: {
            headers,
            status
          }
        });
        return;
      }

      if (shouldRetryUnauthorized(status, retryAttempt, true)) {
        try {
          resolve(await uploadWithFreshToken(params, retryAttempt + 1));
          return;
        } catch (error) {
          reject(error);
          return;
        }
      }

      const detail =
        response && typeof response === 'object' && 'detail' in response
          ? String((response as { detail?: string }).detail || 'Upload failed')
          : request.statusText || 'Upload failed';

      reject(new ApiError(detail, status));
    };

    request.onerror = () => {
      reject(new ApiError('Network error during file upload', 0));
    };

    request.send(formData);
  });
};

export const fetchJson = async <T>(path: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: createHeaders(options?.headers)
  });

  return handleJsonResponse<T>(response);
};

export const fetchAuthenticatedJson = async <T>(
  path: string,
  getToken: TokenProvider,
  options?: AuthenticatedRequestOptions
): Promise<T> => {
  const response = await performAuthenticatedFetch({
    path,
    getToken,
    options
  });

  return handleJsonResponse<T>(response);
};

export const uploadAuthenticatedFile = async <T>(
  params: UploadAuthenticatedFileParams
): Promise<T> => {
  const response = await uploadWithFreshToken<T>(params);
  return response.data;
};

export const uploadAuthenticatedFileWithMeta = async <T>(
  params: UploadAuthenticatedFileParams
): Promise<UploadWithMetaResponse<T>> => uploadWithFreshToken<T>(params);
