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
        title="Оваа област е во подготовка."
        description="Во оваа верзија нема внес и уредување за овој дел. Приказот не користи лажни пресметки или фиксни деловни суми."
      />
    </section>
  );
}
