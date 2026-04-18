import { useEffect, useState } from 'react';
import Icon from '@/components/ui/icon';
import siteConfig from '@/data/site-config.json';

const TRIPS_URL = 'https://functions.poehali.dev/edae194a-306d-463f-aebc-aa3f31fcc94d';

interface Trip {
  id: number;
  title: string;
  date: string;
  participants_count: number;
  organizer: string;
  spot_name: string;
  region: string;
  fish_types: string;
  difficulty: string;
}

const DIFFICULTY_LABEL: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
}

const HERO_IMAGE = 'https://cdn.poehali.dev/projects/c7dc2163-4b08-4088-8826-268daa1f8992/files/78ded997-ab28-45ce-b258-27852f0b333d.jpg';

const NAV_LINKS = ['Главная', 'О сообществе'];

const STATS = [
  { value: '340+', label: 'участников' },
  { value: '12', label: 'лет традиций' },
  { value: '80+', label: 'водоёмов' },
];

const VALUES = [
  {
    icon: 'Anchor',
    title: 'Традиции',
    text: 'Рыбалка — это не просто хобби. Это способ передавать знания, уважение к природе и дружбу из поколения в поколение.',
  },
  {
    icon: 'Users',
    title: 'Сообщество',
    text: 'Мы объединяем людей, которые ценят тишину утреннего клёва, честный разговор у костра и помощь новичку с первой снастью.',
  },
  {
    icon: 'Map',
    title: 'Маршруты',
    text: 'От тихих озёр Подмосковья до северных рек — наши участники знают лучшие места и готовы делиться картой.',
  },
];

const TEAM = [
  { name: 'Алексей Громов', role: 'Основатель', years: 'с 2012 года' },
  { name: 'Сергей Ильин', role: 'Организатор выездов', years: 'с 2015 года' },
  { name: 'Виктор Смолов', role: 'Эксперт по снастям', years: 'с 2018 года' },
];

export default function Index() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(TRIPS_URL)
      .then((r) => r.json())
      .then((data) => setTrips(data.trips ?? []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-[hsl(var(--water-50))] font-golos text-[hsl(var(--water-900))]">

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[hsl(var(--water-50))]/90 backdrop-blur-md border-b border-[hsl(var(--water-100))]">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <span className="font-cormorant text-xl font-semibold tracking-wide text-[hsl(var(--water-900))]">
            {siteConfig.title}
          </span>
          <div className="hidden md:flex gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link}
                href="#"
                className="text-sm text-[hsl(var(--water-600))] hover:text-[hsl(var(--water-900))] transition-colors duration-200"
              >
                {link}
              </a>
            ))}
          </div>
          <button className="text-sm px-5 py-2 border border-[hsl(var(--water-600))] text-[hsl(var(--water-600))] hover:bg-[hsl(var(--water-600))] hover:text-white transition-all duration-300 rounded-sm">
            Вступить
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative h-screen flex items-end pb-20 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${HERO_IMAGE})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[hsl(210,35%,10%)] via-[hsl(210,35%,10%)]/40 to-transparent" />

        <div className="relative z-10 max-w-5xl mx-auto px-6 w-full">
          <p
            className="text-[hsl(var(--water-100))]/70 text-sm uppercase tracking-[0.25em] mb-4 opacity-0 animate-fade-in"
            style={{ animationDelay: '0.2s' }}
          >
            Сообщество рыбаков
          </p>
          <h1
            className="font-cormorant text-6xl md:text-8xl font-light text-white leading-none mb-6 opacity-0 animate-fade-in"
            style={{ animationDelay: '0.4s' }}
          >
            Тишина воды.
            <br />
            <em className="italic font-extralight text-[hsl(var(--water-100))]/80">Сила братства.</em>
          </h1>
          <p
            className="text-[hsl(var(--water-100))]/75 text-base md:text-lg max-w-md leading-relaxed opacity-0 animate-fade-in"
            style={{ animationDelay: '0.65s' }}
          >
            Мы — рыбаки, которые ценят не только улов, но и людей рядом. Присоединяйся к сообществу.
          </p>
        </div>
      </section>

      {/* Stats strip */}
      <section className="bg-[hsl(var(--water-900))] text-white py-12">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-3 divide-x divide-white/10">
          {STATS.map(({ value, label }) => (
            <div key={label} className="text-center px-6">
              <p className="font-cormorant text-4xl md:text-5xl font-light mb-1">{value}</p>
              <p className="text-sm text-white/50 uppercase tracking-widest">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* About */}
      <section id="about" className="py-24 max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-16 items-start">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-4">О сообществе</p>
            <h2 className="font-cormorant text-5xl md:text-6xl font-light leading-tight mb-8 text-[hsl(var(--water-900))]">
              Двенадцать лет<br />
              <em className="italic">у воды</em>
            </h2>
            <p className="text-[hsl(var(--water-600))] leading-relaxed mb-6">
              Рыбацкий Круг появился в 2012 году как небольшая группа друзей,
              которые раз в месяц выбирались на утреннюю рыбалку. Сегодня нас
              более 340 человек по всей стране.
            </p>
            <p className="text-[hsl(var(--water-600))] leading-relaxed">
              Мы организуем совместные выезды, делимся опытом, помогаем
              новичкам освоить снасти и подобрать первые места. У нас нет
              соревнований — только уважение, природа и настоящий отдых.
            </p>
          </div>

          <div className="space-y-8 pt-2">
            {VALUES.map(({ icon, title, text }) => (
              <div key={title} className="flex gap-5">
                <div className="flex-shrink-0 w-10 h-10 rounded-full border border-[hsl(var(--water-100))] flex items-center justify-center text-[hsl(var(--water-600))]">
                  <Icon name={icon} size={18} />
                </div>
                <div>
                  <h3 className="font-cormorant text-xl font-semibold mb-1 text-[hsl(var(--water-900))]">{title}</h3>
                  <p className="text-sm text-[hsl(var(--water-600))] leading-relaxed">{text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="max-w-5xl mx-auto px-6">
        <div className="border-t border-[hsl(var(--water-100))]" />
      </div>

      {/* Team */}
      <section className="py-20 max-w-5xl mx-auto px-6">
        <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-12">Команда</p>
        <div className="grid md:grid-cols-3 gap-0 divide-y md:divide-y-0 md:divide-x divide-[hsl(var(--water-100))]">
          {TEAM.map(({ name, role, years }) => (
            <div key={name} className="py-8 md:py-0 md:px-10 first:pl-0 last:pr-0">
              <p className="text-xs text-[hsl(var(--water-600))]/60 uppercase tracking-wider mb-3">{years}</p>
              <h3 className="font-cormorant text-2xl font-semibold text-[hsl(var(--water-900))] mb-1">{name}</h3>
              <p className="text-sm text-[hsl(var(--water-600))]">{role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Trips */}
      <section className="py-24 bg-[hsl(var(--water-100))]/40">
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-4">Выезды</p>
          <h2 className="font-cormorant text-5xl md:text-6xl font-light leading-tight mb-12 text-[hsl(var(--water-900))]">
            Ближайшие <em className="italic">маршруты</em>
          </h2>

          {loading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-52 rounded-sm bg-[hsl(var(--water-100))] animate-pulse" />
              ))}
            </div>
          ) : trips.length === 0 ? (
            <p className="text-[hsl(var(--water-600))]">Выездов пока нет — следите за обновлениями.</p>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {trips.map((trip) => (
                <div
                  key={trip.id}
                  className="bg-white border border-[hsl(var(--water-100))] rounded-sm p-6 flex flex-col gap-4 hover:shadow-md transition-shadow duration-300"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-cormorant text-2xl font-semibold text-[hsl(var(--water-900))] leading-tight">{trip.title}</h3>
                    <span className="flex-shrink-0 text-xs px-2 py-1 rounded-full border border-[hsl(var(--water-100))] text-[hsl(var(--water-600))]">
                      {DIFFICULTY_LABEL[trip.difficulty] ?? trip.difficulty}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-[hsl(var(--water-600))]">
                    <div className="flex items-center gap-2">
                      <Icon name="Calendar" size={14} />
                      <span>{formatDate(trip.date)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icon name="MapPin" size={14} />
                      <span>{trip.spot_name}, {trip.region}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icon name="Fish" size={14} />
                      <span>{trip.fish_types}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icon name="Users" size={14} />
                      <span>{trip.participants_count} участников</span>
                    </div>
                  </div>

                  <div className="mt-auto pt-2 border-t border-[hsl(var(--water-100))] flex items-center justify-between">
                    <span className="text-xs text-[hsl(var(--water-600))]/60">Организатор: {trip.organizer}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-[hsl(var(--water-900))] text-white py-24">
        <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
            <h2 className="font-cormorant text-4xl md:text-5xl font-light mb-3">
              Готов к первому выезду?
            </h2>
            <p className="text-white/50 text-sm">Оставь заявку — мы напишем в течение дня.</p>
          </div>
          <button className="flex-shrink-0 flex items-center gap-3 px-8 py-4 bg-white text-[hsl(var(--water-900))] hover:bg-[hsl(var(--water-100))] transition-colors duration-300 font-medium text-sm tracking-wide rounded-sm">
            <Icon name="Mail" size={16} />
            Оставить заявку
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[hsl(var(--water-100))] py-8">
        <div className="max-w-5xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-cormorant text-lg text-[hsl(var(--water-900))]">Рыбацкий Круг</span>
          <p className="text-xs text-[hsl(var(--water-600))]/60">© 2012–2026. Все права защищены.</p>
          <div className="flex gap-6">
            {['ВКонтакте', 'Telegram'].map((s) => (
              <a key={s} href="#" className="text-sm text-[hsl(var(--water-600))] hover:text-[hsl(var(--water-900))] transition-colors">
                {s}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}