import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, forkJoin, map, of } from 'rxjs';
import {
  AppConfig,
  ComposeRequest,
  ComposeResult,
  DependencyStatus,
  TokenResponse,
  TokenState,
} from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  healthCheck(config: AppConfig): Observable<DependencyStatus> {
    return forkJoin({
      apiUp: this.http
        .get(`${config.apiHost}/version`, { responseType: 'text' })
        .pipe(
          map(() => true),
          catchError(() => of(false))
        ),
      authUp: this.http
        .get(config.authHost, { responseType: 'text' })
        .pipe(
          map(() => true),
          catchError(() => of(false))
        ),
    });
  }

  getToken(config: AppConfig): Observable<TokenState> {
    const body = new URLSearchParams({
      grant_type: 'password',
      username: config.authUsername,
      password: config.authPassword,
      client_id: config.authClientId,
      client_secret: config.authClientSecret,
    });

    return this.http
      .post<TokenResponse>(
        `${config.authHost}/realms/${config.authRealm}/protocol/openid-connect/token`,
        body.toString(),
        {
          headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' }),
        }
      )
      .pipe(map(this.mapToken));
  }

  refreshToken(config: AppConfig, token: TokenState): Observable<TokenState> {
    const body = new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: token.refreshToken,
      client_id: config.authClientId,
      client_secret: config.authClientSecret,
    });

    return this.http
      .post<TokenResponse>(
        `${config.authHost}/realms/${config.authRealm}/protocol/openid-connect/token`,
        body.toString(),
        {
          headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' }),
        }
      )
      .pipe(map(this.mapToken));
  }

  generateCompose(config: AppConfig, token: TokenState, payload: ComposeRequest): Observable<ComposeResult[]> {
    return this.http.post<ComposeResult[]>(
      `${config.apiHost}/${config.apiVersion}/gen/compose`,
      payload,
      {
        headers: new HttpHeaders({ Authorization: `Bearer ${token.accessToken}` }),
      }
    );
  }

  private mapToken(response: TokenResponse): TokenState {
    const now = Date.now();
    return {
      accessToken: response.access_token,
      accessExp: now + response.expires_in * 1000,
      refreshToken: response.refresh_token,
      refreshExp: now + response.refresh_expires_in * 1000,
    };
  }
}
