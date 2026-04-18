import config from "@/data/config.json";
import Icon from "@/components/ui/icon";

export default function SiteConfig() {
  return (
    <div className="border border-[hsl(var(--water-100))] rounded-sm p-8 max-w-xl mx-auto">
      <p className="text-xs uppercase tracking-[0.2em] text-[hsl(var(--water-600))] mb-4">
        О сайте
      </p>
      <h2 className="font-cormorant text-3xl font-light text-[hsl(var(--water-900))] mb-2">
        {config.site.name}
      </h2>
      <p className="text-sm text-[hsl(var(--water-600))] italic mb-4">
        {config.site.tagline}
      </p>
      <p className="text-[hsl(var(--water-900))] font-golos mb-8 leading-relaxed">
        {config.site.description}
      </p>

      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3 text-sm text-[hsl(var(--water-900))]">
          <Icon name="Mail" size={16} className="text-[hsl(var(--water-600))]" />
          {config.contacts.email}
        </div>
        <div className="flex items-center gap-3 text-sm text-[hsl(var(--water-900))]">
          <Icon name="Send" size={16} className="text-[hsl(var(--water-600))]" />
          {config.contacts.telegram}
        </div>
        <div className="flex items-center gap-3 text-sm text-[hsl(var(--water-900))]">
          <Icon name="Phone" size={16} className="text-[hsl(var(--water-600))]" />
          {config.contacts.phone}
        </div>
      </div>
    </div>
  );
}
