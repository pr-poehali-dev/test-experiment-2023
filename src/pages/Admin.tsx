import { useState, useEffect } from 'react';
import Icon from '@/components/ui/icon';

const DB_MONITOR_URL = 'https://functions.poehali.dev/86db669a-df3b-4650-a2cc-ce71ae6e3e4d';
const TABLES = ['members', 'spots', 'trips'] as const;

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

  useEffect(() => {
    const saved = sessionStorage.getItem('admin_token');
    if (saved) setToken(saved);
  }, []);

  async function load(t: string) {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(DB_MONITOR_URL, {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.status === 401) { setError('Неверный токен'); setLoading(false); return; }
      const json = await res.json();
      setData(json);
      setToken(t);
      sessionStorage.setItem('admin_token', t);
    } catch {
      setError('Ошибка подключения');
    }
    setLoading(false);
  }

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
        <div className="flex items-center justify-between mb-10">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-1">Панель</p>
            <h1 className="font-cormorant text-3xl font-light text-[hsl(var(--water-900))]">Мониторинг базы данных</h1>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => load(token)}
              className="flex items-center gap-2 text-sm text-[hsl(var(--water-600))] hover:text-[hsl(var(--water-900))] transition-colors"
            >
              <Icon name="RefreshCw" size={14} />
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

        {loading && <p className="text-sm text-[hsl(var(--water-600))]">Загрузка...</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}

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
                return (
                  <div key={table} className="border border-[hsl(var(--water-100))] rounded-sm p-6 bg-white">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="font-cormorant text-xl text-[hsl(var(--water-900))]">{TABLE_LABELS[table]}</h2>
                      <span className="text-xs uppercase tracking-[0.15em] text-[hsl(var(--water-600))]">{table}</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
                        <p className={`text-lg font-semibold ${t.n_dead_tup && t.n_dead_tup > 100 ? 'text-red-500' : 'text-[hsl(var(--water-900))]'}`}>
                          {t.n_dead_tup ?? '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Последняя запись</p>
                        <p className="text-sm text-[hsl(var(--water-900))]">{formatDate(t.last_updated)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[hsl(var(--water-600))] mb-1">Seq / Idx scans</p>
                        <p className="text-sm text-[hsl(var(--water-900))]">{t.seq_scan ?? '—'} / {t.idx_scan ?? '—'}</p>
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
