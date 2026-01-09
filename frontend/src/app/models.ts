export interface AppConfig {
  apiHost: string;
  apiVersion: string;
  authHost: string;
  authRealm: string;
  authClientId: string;
  authClientSecret: string;
  authUsername: string;
  authPassword: string;
}

export interface TokenResponse {
  access_token: string;
  expires_in: number;
  refresh_token: string;
  refresh_expires_in: number;
}

export interface TokenState {
  accessToken: string;
  accessExp: number;
  refreshToken: string;
  refreshExp: number;
}

export interface ComposeRequest {
  services: string[];
  network_name: string;
  network_exists: boolean;
  volume_mount: boolean;
}

export interface ComposeResult {
  type: number | string;
  name?: string;
  data: string;
}

export interface DependencyStatus {
  apiUp: boolean;
  authUp: boolean;
}
