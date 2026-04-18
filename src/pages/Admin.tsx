import { useState, useEffect, useCallback } from 'react';
import Icon from '@/components/ui/icon';

const DB_MONITOR_URL = 'https://functions.poehali.dev/86db669a-df3b-4650-a2cc-ce71ae6e3e4d';
const TABLES = ['members', 'spots', 'trips'] as const;
const AUTO_REFRESH_SEC = 30;

interface TableStats {
  count: number;
  last_updated: string | null;
  size_bytes: number;
  seq_scan: number | null;
  idx_scan: number | null;
  n_live_tup: number | null;
  n_dead_tup: number | null;
  last_autovacuum: string | null;
  last_autoanalyze: string | null;
}

interface MonitorData {
  tables: Record<string, TableStats>;
  db_size_bytes: number;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} ГБ`;
}

function formatDate(iso: string | null) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('ru-RU');
}

function deadTuplesStatus(n_dead: number | null, n_live: number | null): 'ok' | 'warn' | 'crit' {
  if (n_dead === null || n_live === null || n_live === 0) return 'ok';
  const pct = n_dead / (n_live + n_dead) * 100;
  if (pct > 20) return 'crit';
  if (pct > 10) return 'warn';
  return 'ok';
}

function scanStatus(seq: number | null, idx: number | null): 'ok' | 'warn' {
  if (seq === null || idx === null || seq === 0) return 'ok';
  if (seq > 100 && seq > idx * 3) return 'warn';
  return 'ok';
}

const STATUS_DOT: Record<string, string> = {
  ok: 'bg-green-400',
  warn: 'bg-yellow-400',
  crit: 'bg-red-500',
};

const TABLE_LABELS: Record<string, string> = {
  members: 'Участники',
  spots: 'Водоёмы',
  trips: 'Выезды',
};

export default function Admin() {
  const [token, setToken] = useState('');
  const [input, setInput] = useState('');
  const [data, setData] = useState<MonitorData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [countdown, setCountdown] = useState(AUTO_REFRESH_SEC);

  useEffect(() => {
    const saved = sessionStorage.getItem('admin_token');
    if (saved) setToken(saved);
  }, []);

  const load = useCallback(async (t: string, silent = false) => {
    if (!silent) setLoading(true);
    setError('');
    try {
      const res = await fetch(DB_MONITOR_URL, {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.status === 401) { setError('Неверный токен'); setLoading(false); return; }
      const json = await res.json();
      setData(json);
      setToken(t);
      setLastUpdated(new Date());
      setCountdown(AUTO_REFRESH_SEC);
      sessionStorage.setItem('admin_token', t);
    } catch {
      setError('Ошибка подключения');
    }
    if (!silent) setLoading(false);
  }, []);

  useEffect(() => {
    if (!token) return;
    const interval = setInterval(() => {
      setCountdown(c => {
        if (c <= 1) { load(token, true); return AUTO_REFRESH_SEC; }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [token, load]);

  useEffect(() => {
    if (token && !data) load(token);
  }, [token]);

  if (!token) {
    return (
      <div className="min-h-screen bg-[hsl(var(--water-50))] flex items-center justify-center px-4">
        <div className="border border-[hsl(var(--water-100))] rounded-sm p-8 w-full max-w-sm bg-white">
          <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-4">Мониторинг</p>
          <h1 className="font-cormorant text-2xl font-light text-[hsl(var(--water-900))] mb-6">Вход</h1>
          <input
            type="password"
            placeholder="Токен доступа"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && load(input)}
            className="w-full border border-[hsl(var(--water-100))] rounded-sm px-3 py-2 text-sm mb-3 outline-none focus:border-[hsl(var(--water-600))] text-[hsl(var(--water-900))]"
          />
          {error && <p className="text-red-500 text-xs mb-3">{error}</p>}
          <button
            onClick={() => load(input)}
            disabled={loading || !input}
            className="w-full bg-[hsl(var(--water-900))] text-[hsl(var(--water-50))] text-sm py-2 rounded-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? 'Загрузка...' : 'Войти'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[hsl(var(--water-50))] px-6 py-12">
      <div className="max-w-4xl mx-auto">

        <div className="flex items-start justify-between mb-10">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-1">Панель</p>
            <h1 className="font-cormorant text-3xl font-light text-[hsl(var(--water-900))]">Мониторинг базы данных</h1>
            {lastUpdated && (
              <p className="text-xs text-[hsl(var(--water-600))] mt-1">
                Обновлено: {lastUpdated.toLocaleTimeString('ru-RU')} · следующее через {countdown}с
              </p>
            )}
          </div>
          <div className="flex gap-3 mt-1">
            <button
              onClick={() => load(token)}
              disabled={loading}
              className="flex items-center gap-2 text-sm text-[hsl(var(--water-600))] hover:text-[hsl(var(--water-900))] transition-colors disabled:opacity-50"
            >
              <Icon name="RefreshCw" size={14} className={loading ? 'animate-spin' : ''} />
              Обновить
            </button>
            <button
              onClick={() => { sessionStorage.removeItem('admin_token'); setToken(''); setData(null); }}
              className="flex items-center gap-2 text-sm text-[hsl(var(--water-600))] hover:text-[hsl(var(--water-900))] transition-colors"
            >
              <Icon name="LogOut" size={14} />
              Выйти
            </button>
          </div>
        </div>

        {loading && !data && <p className="text-sm text-[hsl(var(--water-600))]">Загрузка...</p>}
        {error && <p className="text-sm text-red-500 mb-4">{error}</p>}

        {data && (
          <>
            <div className="border border-[hsl(var(--water-100))] rounded-sm p-5 mb-6 bg-white inline-flex items-center gap-3">
              <Icon name="Database" size={16} className="text-[hsl(var(--water-600))]" />
              <span className="text-sm text-[hsl(var(--water-900))]">Размер базы данных:</span>
              <span className="font-semibold text-sm text-[hsl(var(--water-900))]">{formatBytes(data.db_size_bytes)}</span>
            </div>

            <div className="grid gap-4">
              {TABLES.map(table => {
                const t = data.tables[table];
                if (!t) return null;

                const deadPct = t.n_live_tup && t.n_dead_tup !== null
                  ? ((t.n_dead_tup / (t.n_live_tup + t.n_dead_tup)) * 100).toFixed(1)
                  : null;
                const deadStatus = deadTuplesStatus(t.n_dead_tup, t.n_live_tup);
                const scanSt = scanStatus(t.seq_scan, t.idx_scan);
                const overallStatus = deadStatus === 'crit' ? 'crit' : (deadStatus === 'warn' || scanSt === 'warn') ? 'warn' : 'ok';

                return (
                  <div key={table} className="border border-[hsl(var(--water-100))] rounded-sm p-6 bg-white">
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-3">
                        <span className={`w-2 h-2 rounded-full ${STATUS_DOT[overallStatus]}`} />
                        <h2 className="font-cormorant text-xl text-[hsl(var(--water-900))]">{TABLE_LABELS[table]}</h2>
                      </div>
                      <span className="text-xs uppercase tracking-[0.15em] text-[hsl(var(--water-600))]">{table}</span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Записей</p>
                        <p className="text-lg font-semibold text-[hsl(var(--water-900))]">{t.count}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Размер</p>
                        <p className="text-lg font-semibold text-[hsl(var(--water-900))]">{formatBytes(t.size_bytes)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Живых строк</p>
                        <p className="text-lg font-semibold text-[hsl(var(--water-900))]">{t.n_live_tup ?? '—'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Мёртвых строк</p>
                        <div className="flex items-baseline gap-2">
                          <p className={`text-lg font-semibold ${deadStatus === 'crit' ? 'text-red-500' : deadStatus === 'warn' ? 'text-yellow-500' : 'text-[hsl(var(--water-900))]'}`}>
                            {t.n_dead_tup ?? '—'}
                          </p>
                          {deadPct !== null && (
                            <span className="text-xs text-[hsl(var(--water-600))]">{deadPct}%</span>
                          )}
                        </div>
                        {deadStatus === 'warn' && <p className="text-xs text-yellow-600 mt-0.5">Рекомендуется VACUUM</p>}
                        {deadStatus === 'crit' && <p className="text-xs text-red-500 mt-0.5">Нужен срочный VACUUM</p>}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-[hsl(var(--water-100))]">
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Последняя запись</p>
                        <p className="text-sm text-[hsl(var(--water-900))]">{formatDate(t.last_updated)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Seq / Idx scans</p>
                        <p className={`text-sm ${scanSt === 'warn' ? 'text-yellow-500' : 'text-[hsl(var(--water-900))]'}`}>
                          {t.seq_scan ?? '—'} / {t.idx_scan ?? '—'}
                        </p>
                        {scanSt === 'warn' && <p className="text-xs text-yellow-600 mt-0.5">Много seq scans — нужен индекс</p>}
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Автовакуум</p>
                        <p className="text-sm text-[hsl(var(--water-900))]">{formatDate(t.last_autovacuum)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Автоанализ</p>
                        <p className="text-sm text-[hsl(var(--water-900))]">{formatDate(t.last_autoanalyze)}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
