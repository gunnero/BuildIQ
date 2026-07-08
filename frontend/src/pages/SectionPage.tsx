import { EmptyState } from "../components/EmptyState";

type SectionPageProps = {
  title: string;
  description: string;
};

export function SectionPage({ title, description }: SectionPageProps) {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">{title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
      </div>
      <EmptyState
        title="Сè уште нема записи."
        description="Екраните за внес и уредување ќе бидат додадени во следен спринт. Овој приказ не користи лажни пресметки или фиксни деловни суми."
      />
    </section>
  );
}
