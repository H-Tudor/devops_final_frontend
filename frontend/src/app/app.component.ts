import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { of, switchMap } from 'rxjs';
import { finalize, tap } from 'rxjs/operators';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { ApiService } from './api.service';
import { AppConfig, ComposeResult, TokenState } from './models';
import { loadConfig } from './config';

const MAX_SERVICE_NAME = 64;

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="page">
      <header class="header">
        <div>
          <p class="eyebrow">DevOps Final</p>
          <h1>LLM Compose Generator</h1>
          <p class="muted">Automate the creation of Docker Compose configurations using the power of LLMs.</p>
          <div class="status-row" *ngIf="dependencyStatus() as status">
            <span class="pill" [class.ok]="status.apiUp" [class.bad]="!status.apiUp">API {{ status.apiUp ? 'Up' : 'Down' }}</span>
            <span class="pill" [class.ok]="status.authUp" [class.bad]="!status.authUp">
              Auth {{ status.authUp ? 'Up' : 'Down' }}
            </span>
          </div>
        </div>
        <div class="user-card">
          <div>
            <div class="label">Backend</div>
            <div class="muted small">{{ config.apiHost }}</div>
          </div>
          <button type="button" class="secondary" (click)="authenticate()" [disabled]="authBusy()">Authenticate</button>
        </div>
      </header>

      <main class="grid">
        <section class="card">
          <div class="card-header">
            <div>
              <h2>Input Services</h2>
              <p class="muted small">Add the services you want the LLM to include in your compose file.</p>
            </div>
            <div class="actions">
              <button
                type="button"
                class="ghost"
                (click)="clearServices()"
                [disabled]="servicesArray.length === 1 && !(servicesArray.at(0)?.value?.trim())"
              >
                Clear
              </button>
              <button type="button" class="ghost" (click)="addService()" [disabled]="lastEmpty()">Add</button>
            </div>
          </div>

          <form [formGroup]="form" class="form">
            <div class="form-grid">
              <div class="field full">
                <label for="networkName">Docker Network</label>
                <input
                  id="networkName"
                  type="text"
                  formControlName="networkName"
                  placeholder="devops-final"
                  maxlength="128"
                />
              </div>
              <label class="checkbox">
                <input type="checkbox" formControlName="networkExists" />
                <span>Network already exists</span>
              </label>
              <label class="checkbox">
                <input type="checkbox" formControlName="volumeMount" />
                <span>Mount volumes in project folder</span>
              </label>
            </div>

            <div class="service-list">
              <div class="field" *ngFor="let control of servicesArray.controls; let i = index">
                <label>Service {{ i + 1 }}</label>
                <div class="service-row">
                  <input
                    type="text"
                    [formControl]="control"
                    [attr.placeholder]="'e.g. postgres:16'"
                    [maxlength]="serviceMaxLength"
                  />
                  <button
                    type="button"
                    class="icon"
                    (click)="removeService(i)"
                    [disabled]="servicesArray.length === 1"
                    aria-label="Remove service"
                  >
                    ✕
                  </button>
                </div>
                <div class="error" *ngIf="control.invalid && control.touched">Max length {{ serviceMaxLength }}</div>
              </div>
            </div>

            <div class="buttons">
              <button type="button" class="primary" (click)="generate()" [disabled]="!canGenerate()">Generate</button>
              <button type="button" class="secondary" (click)="downloadBundle()" [disabled]="!canDownload()">Download</button>
            </div>
          </form>

          <div class="helper">
            <strong>Tip:</strong> Include versions in your service names for better results (e.g. <code>postgres:16</code>).
          </div>
        </section>

        <section class="card">
          <div class="card-header">
            <div>
              <h2>Results</h2>
              <p class="muted small">Generated docker-compose and environment files.</p>
            </div>
          </div>

          <div *ngIf="error()" class="alert error">{{ error() }}</div>
          <div *ngIf="success()" class="alert success">{{ success() }}</div>

          <div *ngIf="loading()" class="alert info">Generation in progress...</div>

          <div class="result-grid" *ngIf="composeText()">
            <div>
              <h3>Docker Compose</h3>
              <pre class="code">{{ composeText() }}</pre>
            </div>
            <div>
              <h3>Environment Files</h3>
              <div class="warning">
                AI Models might have deprecated knowledge, some configuration data such as environment variables might be
                outdated. Cross-reference official documentation.
              </div>
              <div *ngIf="envFiles().length === 0" class="muted">No env files generated.</div>
              <div *ngFor="let env of envFiles()">
                <p class="env-title">{{ env.title }}</p>
                <pre class="code">{{ env.body }}</pre>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        min-height: 100vh;
        background: linear-gradient(180deg, #0c111d, #0b1325 40%, #0c111d);
        color: #e6e8f0;
        font-family: "Inter", system-ui, -apple-system, sans-serif;
      }

      .page {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 24px 48px;
      }

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        padding: 16px 0 24px;
      }

      .eyebrow {
        letter-spacing: 0.08em;
        font-size: 12px;
        text-transform: uppercase;
        color: #8ea2c8;
        margin: 0 0 8px;
      }

      h1 {
        margin: 0;
        font-size: 32px;
      }

      h2 {
        margin: 0;
        font-size: 22px;
      }

      h3 {
        margin: 0 0 8px;
      }

      .muted {
        color: #9fb1d3;
      }

      .muted.small {
        font-size: 13px;
      }

      .status-row {
        display: flex;
        gap: 12px;
        margin-top: 12px;
      }

      .pill {
        padding: 6px 10px;
        border-radius: 12px;
        font-size: 12px;
        background: #1c2333;
        color: #cdd7f3;
        border: 1px solid #1f2a3f;
      }

      .pill.ok {
        border-color: #3cc76a;
        color: #d4ffe5;
      }

      .pill.bad {
        border-color: #e45757;
        color: #ffc7c7;
      }

      .user-card {
        padding: 12px 16px;
        border-radius: 12px;
        background: #12192a;
        border: 1px solid #1f2a3f;
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .grid {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      }

      .card {
        background: #0f1729;
        border: 1px solid #1f2a3f;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 12px;
      }

      .form {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 12px;
        align-items: center;
      }

      .field {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .field.full {
        grid-column: 1 / -1;
      }

      label {
        font-size: 14px;
        color: #cdd7f3;
      }

      input[type='text'] {
        width: 100%;
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid #24314a;
        background: #0c1221;
        color: #e6e8f0;
      }

      input[type='text']:focus {
        outline: 2px solid #3f83f8;
        border-color: #3f83f8;
      }

      .checkbox {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #cdd7f3;
      }

      .service-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }

      .service-row {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 8px;
      }

      .buttons {
        display: flex;
        gap: 10px;
      }

      button {
        cursor: pointer;
        padding: 10px 14px;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        color: #0c111d;
      }

      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .primary {
        background: linear-gradient(120deg, #3f83f8, #5b9bff);
        color: #fff;
      }

      .secondary {
        background: #1c2438;
        color: #dfe8ff;
        border: 1px solid #30405f;
      }

      .ghost {
        background: transparent;
        color: #cdd7f3;
        border: 1px dashed #30405f;
      }

      .icon {
        background: #1c2438;
        color: #dfe8ff;
        border: 1px solid #24314a;
      }

      .actions {
        display: flex;
        gap: 8px;
      }

      .helper {
        font-size: 13px;
        color: #9fb1d3;
        padding: 10px;
        border-radius: 10px;
        background: #121a2b;
        border: 1px dashed #24314a;
      }

      .alert {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
      }

      .alert.error {
        background: #2a1117;
        color: #ffc7c7;
        border: 1px solid #e45757;
      }

      .alert.success {
        background: #0f2418;
        color: #d4ffe5;
        border: 1px solid #3cc76a;
      }

      .alert.info {
        background: #0f1b2d;
        color: #d6e6ff;
        border: 1px solid #3f83f8;
      }

      .warning {
        background: #24190b;
        color: #ffd9a0;
        border: 1px solid #e0a14f;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 13px;
      }

      .code {
        background: #0b1020;
        border: 1px solid #1f2a3f;
        border-radius: 12px;
        padding: 12px;
        white-space: pre-wrap;
        overflow: auto;
        color: #d7e2ff;
      }

      .result-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
      }

      .env-title {
        margin: 8px 0 4px;
        font-weight: 600;
      }

      .label {
        font-size: 12px;
        text-transform: uppercase;
        color: #8ea2c8;
        letter-spacing: 0.04em;
      }

      .service-row button {
        min-width: 42px;
      }
    `,
  ],
})
export class AppComponent implements OnInit {
  config: AppConfig = loadConfig();
  serviceMaxLength = MAX_SERVICE_NAME;

  dependencyStatus = signal<{ apiUp: boolean; authUp: boolean } | null>(null);
  token = signal<TokenState | null>(null);
  composeText = signal<string>('');
  envFiles = signal<{ title: string; body: string }[]>([]);
  error = signal<string>('');
  success = signal<string>('');
  loading = signal<boolean>(false);
  authBusy = signal<boolean>(false);

  readonly form: ReturnType<AppComponent['buildForm']>;

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.form = this.buildForm();
  }

  private buildForm() {
    return this.fb.nonNullable.group({
      services: this.fb.array<FormControl<string>>([
        this.fb.control('', { validators: Validators.maxLength(MAX_SERVICE_NAME), nonNullable: true }),
      ]),
      networkName: [''],
      networkExists: [false],
      volumeMount: [true],
    });
  }

  ngOnInit(): void {
    this.checkHealth();
  }

  get servicesArray(): FormArray<FormControl<string>> {
    return this.form.get('services') as FormArray<FormControl<string>>;
  }

  lastEmpty(): boolean {
    if (this.servicesArray.length === 0) return true;
    return this.servicesArray.at(this.servicesArray.length - 1)?.value.trim().length === 0;
  }

  addService(): void {
    if (this.lastEmpty()) {
      return;
    }

    this.servicesArray.push(
      this.fb.control('', { validators: Validators.maxLength(MAX_SERVICE_NAME), nonNullable: true })
    );
  }

  removeService(index: number): void {
    if (this.servicesArray.length === 1) {
      return;
    }
    this.servicesArray.removeAt(index);
  }

  clearServices(): void {
    this.servicesArray.clear();
    this.servicesArray.push(
      this.fb.control('', { validators: Validators.maxLength(MAX_SERVICE_NAME), nonNullable: true })
    );
  }

  canGenerate(): boolean {
    const hasService = this.servicesArray.controls.some((ctrl) => ctrl.value.trim().length > 0);
    return hasService && !this.loading();
  }

  canDownload(): boolean {
    return !!this.composeText() && !this.loading();
  }

  authenticate(): void {
    this.error.set('');
    this.success.set('');
    this.authBusy.set(true);
    this.api
      .getToken(this.config)
      .pipe(
        tap((token) => this.token.set(token)),
        finalize(() => this.authBusy.set(false))
      )
      .subscribe({
        next: () => this.success.set('Authenticated with backend'),
        error: () => this.error.set('Backend authentication failed. Check Keycloak credentials.'),
      });
  }

  private ensureToken() {
    const token = this.token();
    const now = Date.now();

    if (token && token.accessExp > now + 5000) {
      return of(token);
    }

    if (token && token.refreshExp > now) {
      return this.api.refreshToken(this.config, token).pipe(tap((t) => this.token.set(t)));
    }

    return this.api.getToken(this.config).pipe(tap((t) => this.token.set(t)));
  }

  generate(): void {
    if (!this.canGenerate()) return;

    this.loading.set(true);
    this.error.set('');
    this.success.set('');

    const payload = this.composePayload();

    this.ensureToken()
      .pipe(
        switchMap((token) => this.api.generateCompose(this.config, token, payload)),
        finalize(() => this.loading.set(false))
      )
      .subscribe({
        next: (results) => this.handleCompose(results),
        error: () => this.error.set('Service failed to respond. Please verify connectivity and credentials.'),
      });
  }

  private composePayload() {
    return {
      services: this.servicesArray.controls
        .map((ctrl) => ctrl.value.trim())
        .filter((val) => val.length > 0),
      network_name: this.form.controls.networkName.value,
      network_exists: this.form.controls.networkExists.value,
      volume_mount: this.form.controls.volumeMount.value,
    };
  }

  private handleCompose(results: ComposeResult[]) {
    const composeParts: string[] = [];
    const envs: { title: string; body: string }[] = [];

    results.forEach((result) => {
      const typeVal = result.type;
      if (typeVal === 3 || typeVal === 'COMPOSE_FILE') {
        composeParts.push(result.data);
      }
      if (typeVal === 2 || typeVal === 'ENV_FILE') {
        envs.push({ title: result.name ?? 'env', body: result.data });
      }
    });

    this.composeText.set(composeParts.join('\n'));
    this.envFiles.set(envs);
    this.success.set('Compose generated successfully.');
  }

  async downloadBundle() {
    if (!this.composeText()) return;
    const zip = new JSZip();
    zip.file('compose.yml', this.composeText());
    this.envFiles().forEach((env) => zip.file(env.title || 'env', env.body));
    const blob = await zip.generateAsync({ type: 'blob' });
    saveAs(blob, 'compose_export.zip');
  }

  private checkHealth() {
    this.api.healthCheck(this.config).subscribe({
      next: (status) => this.dependencyStatus.set(status),
      error: () => this.dependencyStatus.set({ apiUp: false, authUp: false }),
    });
  }
}
