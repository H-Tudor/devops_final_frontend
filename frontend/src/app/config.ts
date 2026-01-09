import { AppConfig } from './models';

declare global {
  interface Window {
    __APP_CONFIG__?: Partial<AppConfig>;
  }
}

const defaultConfig: AppConfig = {
  apiHost: 'http://localhost:8000',
  apiVersion: 'vNext',
  authHost: 'http://localhost:8080',
  authRealm: 'devops-final',
  authClientId: 'frontend',
  authClientSecret: '',
  authUsername: '',
  authPassword: '',
};

export function loadConfig(): AppConfig {
  return { ...defaultConfig, ...(window.__APP_CONFIG__ ?? {}) };
}
