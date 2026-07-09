import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, Save } from "lucide-react";
import { useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import {
  archiveCustomer,
  createCustomer,
  createCustomerContact,
  getCustomer,
  listCustomerContacts,
  listCustomers,
  updateCustomer,
} from "../api/customers";
import {
  archiveProperty,
  createProperty,
  createPropertyContact,
  createPropertyNote,
  getProperty,
  listProperties,
  listPropertyContacts,
  listPropertyNotes,
  updateProperty,
} from "../api/properties";
import type {
  ContactCreateRequest,
  CustomerCreateRequest,
  CustomerResponse,
  PropertyCreateRequest,
  PropertyResponse,
} from "../api/types";

type CustomerFormState = {
  name: string;
  phone: string;
  email: string;
  address: string;
  note: string;
};

type ContactFormState = {
  full_name: string;
  phone: string;
  email: string;
  role: string;
  note: string;
  is_primary: boolean;
};

type PropertyFormState = {
  customer_id: string;
  name: string;
  address: string;
  city: string;
  note: string;
};

type PropertyNoteFormState = {
  content: string;
};

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

const emptyCustomerForm: CustomerFormState = {
  name: "",
  phone: "",
  email: "",
  address: "",
  note: "",
};

const emptyContactForm: ContactFormState = {
  full_name: "",
  phone: "",
  email: "",
  role: "",
  note: "",
  is_primary: false,
};

const emptyPropertyForm: PropertyFormState = {
  customer_id: "",
  name: "",
  address: "",
  city: "",
  note: "",
};

const emptyPropertyNoteForm: PropertyNoteFormState = {
  content: "",
};

const entityStatusLabels: Record<string, string> = {
  active: "Активен",
  archived: "Архивиран",
};

function toNullable(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}

function customerPayloadFromForm(form: CustomerFormState): CustomerCreateRequest {
  return {
    name: form.name.trim(),
    phone: toNullable(form.phone),
    email: toNullable(form.email),
    address: toNullable(form.address),
    note: toNullable(form.note),
  };
}

function contactPayloadFromForm(form: ContactFormState): ContactCreateRequest {
  return {
    full_name: form.full_name.trim(),
    phone: toNullable(form.phone),
    email: toNullable(form.email),
    role: toNullable(form.role),
    note: toNullable(form.note),
    is_primary: form.is_primary,
  };
}

function propertyPayloadFromForm(form: PropertyFormState): PropertyCreateRequest {
  return {
    customer_id: form.customer_id,
    name: form.name.trim(),
    address: toNullable(form.address),
    city: toNullable(form.city),
    note: toNullable(form.note),
  };
}

function customerFormFromEntity(customer: CustomerResponse): CustomerFormState {
  return {
    name: customer.name,
    phone: customer.phone ?? "",
    email: customer.email ?? "",
    address: customer.address ?? "",
    note: customer.note ?? "",
  };
}

function propertyFormFromEntity(property: PropertyResponse): PropertyFormState {
  return {
    customer_id: property.customer_id,
    name: property.name,
    address: property.address ?? "",
    city: property.city ?? "",
    note: property.note ?? "",
  };
}

function formatStatus(status: string): string {
  return entityStatusLabels[status] ?? "Непознат";
}

function displayValue(value: string | null | undefined): string {
  return value?.trim() ? value : "Не е внесено";
}

function Panel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section className="ui-card">
      <h2 className="ui-card-title">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function FormField({
  label,
  name,
  onChange,
  required = false,
  type = "text",
  value,
}: {
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  type?: string;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        required={required}
        onChange={onChange}
        className="ui-input"
      />
    </label>
  );
}

function TextAreaField({
  label,
  name,
  onChange,
  value,
}: {
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        rows={3}
        className="ui-textarea"
      />
    </label>
  );
}

function Message({ children, tone = "neutral" }: { children: ReactNode; tone?: MessageTone }) {
  const toneClass =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-800"
      : tone === "success"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : "border-line bg-slate-50 text-slate-700";

  return <p className={`ui-message ${toneClass}`}>{children}</p>;
}

function PrimaryButton({ children, disabled = false }: { children: ReactNode; disabled?: boolean }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="ui-button-primary"
    >
      <Plus aria-hidden="true" className="h-4 w-4" />
      {children}
    </button>
  );
}

function SecondaryButton({
  children,
  disabled = false,
  onClick,
  type = "button",
}: {
  children: ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className="ui-button-secondary"
    >
      {children}
    </button>
  );
}

function DetailRow({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{displayValue(value)}</dd>
    </div>
  );
}

export function CustomersPage() {
  const queryClient = useQueryClient();
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);
  const [customerForm, setCustomerForm] = useState<CustomerFormState>(emptyCustomerForm);
  const [customerEditForm, setCustomerEditForm] = useState<CustomerFormState>(emptyCustomerForm);
  const [customerContactForm, setCustomerContactForm] = useState<ContactFormState>(emptyContactForm);
  const [propertyForm, setPropertyForm] = useState<PropertyFormState>(emptyPropertyForm);
  const [propertyEditForm, setPropertyEditForm] = useState<PropertyFormState>(emptyPropertyForm);
  const [propertyContactForm, setPropertyContactForm] = useState<ContactFormState>(emptyContactForm);
  const [propertyNoteForm, setPropertyNoteForm] = useState<PropertyNoteFormState>(emptyPropertyNoteForm);
  const [customerMessage, setCustomerMessage] = useState<PageMessage | null>(null);
  const [propertyMessage, setPropertyMessage] = useState<PageMessage | null>(null);

  const customersQuery = useQuery({
    queryKey: ["customers"],
    queryFn: listCustomers,
  });

  const propertiesQuery = useQuery({
    queryKey: ["properties"],
    queryFn: listProperties,
  });

  const selectedCustomerQuery = useQuery({
    queryKey: ["customers", selectedCustomerId],
    queryFn: () => getCustomer(selectedCustomerId ?? ""),
    enabled: Boolean(selectedCustomerId),
  });

  const selectedPropertyQuery = useQuery({
    queryKey: ["properties", selectedPropertyId],
    queryFn: () => getProperty(selectedPropertyId ?? ""),
    enabled: Boolean(selectedPropertyId),
  });

  const customerContactsQuery = useQuery({
    queryKey: ["customer-contacts", selectedCustomerId],
    queryFn: () => listCustomerContacts(selectedCustomerId ?? ""),
    enabled: Boolean(selectedCustomerId),
  });

  const propertyContactsQuery = useQuery({
    queryKey: ["property-contacts", selectedPropertyId],
    queryFn: () => listPropertyContacts(selectedPropertyId ?? ""),
    enabled: Boolean(selectedPropertyId),
  });

  const propertyNotesQuery = useQuery({
    queryKey: ["property-notes", selectedPropertyId],
    queryFn: () => listPropertyNotes(selectedPropertyId ?? ""),
    enabled: Boolean(selectedPropertyId),
  });

  const customerById = useMemo(() => {
    return new Map((customersQuery.data ?? []).map((customer) => [customer.id, customer.name]));
  }, [customersQuery.data]);

  const createCustomerMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: (createdCustomer) => {
      setCustomerMessage({ text: "Клиентот е додаден.", tone: "success" });
      setCustomerForm(emptyCustomerForm);
      setSelectedCustomerId(createdCustomer.id);
      setCustomerEditForm(customerFormFromEntity(createdCustomer));
      void queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
    onError: () => setCustomerMessage({ text: "Клиентот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const updateCustomerMutation = useMutation({
    mutationFn: (payload: CustomerCreateRequest) => {
      if (!selectedCustomerId) {
        throw new Error("Missing selected customer");
      }

      return updateCustomer(selectedCustomerId, payload);
    },
    onSuccess: (updatedCustomer) => {
      setCustomerMessage({ text: "Клиентот е ажуриран.", tone: "success" });
      setCustomerEditForm(customerFormFromEntity(updatedCustomer));
      void queryClient.invalidateQueries({ queryKey: ["customers"] });
      void queryClient.invalidateQueries({ queryKey: ["customers", updatedCustomer.id] });
    },
    onError: () => setCustomerMessage({ text: "Клиентот не беше ажуриран. Обидете се повторно.", tone: "error" }),
  });

  const archiveCustomerMutation = useMutation({
    mutationFn: (customerId: string) => archiveCustomer(customerId),
    onSuccess: (archivedCustomer) => {
      setCustomerMessage({ text: "Клиентот е архивиран.", tone: "success" });
      setSelectedCustomerId(archivedCustomer.id);
      void queryClient.invalidateQueries({ queryKey: ["customers"] });
      void queryClient.invalidateQueries({ queryKey: ["customers", archivedCustomer.id] });
    },
    onError: () => setCustomerMessage({ text: "Клиентот не беше архивиран. Обидете се повторно.", tone: "error" }),
  });

  const createCustomerContactMutation = useMutation({
    mutationFn: (payload: ContactCreateRequest) => {
      if (!selectedCustomerId) {
        throw new Error("Missing selected customer");
      }

      return createCustomerContact(selectedCustomerId, payload);
    },
    onSuccess: () => {
      setCustomerMessage({ text: "Контактот е додаден.", tone: "success" });
      setCustomerContactForm(emptyContactForm);
      void queryClient.invalidateQueries({ queryKey: ["customer-contacts", selectedCustomerId] });
    },
    onError: () => setCustomerMessage({ text: "Контактот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const createPropertyMutation = useMutation({
    mutationFn: createProperty,
    onSuccess: (createdProperty) => {
      setPropertyMessage({ text: "Објектот е додаден.", tone: "success" });
      setPropertyForm(emptyPropertyForm);
      setSelectedPropertyId(createdProperty.id);
      setPropertyEditForm(propertyFormFromEntity(createdProperty));
      void queryClient.invalidateQueries({ queryKey: ["properties"] });
    },
    onError: () => setPropertyMessage({ text: "Објектот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const updatePropertyMutation = useMutation({
    mutationFn: (payload: PropertyCreateRequest) => {
      if (!selectedPropertyId) {
        throw new Error("Missing selected property");
      }

      return updateProperty(selectedPropertyId, {
        name: payload.name,
        address: payload.address,
        city: payload.city,
        note: payload.note,
      });
    },
    onSuccess: (updatedProperty) => {
      setPropertyMessage({ text: "Објектот е ажуриран.", tone: "success" });
      setPropertyEditForm(propertyFormFromEntity(updatedProperty));
      void queryClient.invalidateQueries({ queryKey: ["properties"] });
      void queryClient.invalidateQueries({ queryKey: ["properties", updatedProperty.id] });
    },
    onError: () => setPropertyMessage({ text: "Објектот не беше ажуриран. Обидете се повторно.", tone: "error" }),
  });

  const archivePropertyMutation = useMutation({
    mutationFn: (propertyId: string) => archiveProperty(propertyId),
    onSuccess: (archivedProperty) => {
      setPropertyMessage({ text: "Објектот е архивиран.", tone: "success" });
      setSelectedPropertyId(archivedProperty.id);
      void queryClient.invalidateQueries({ queryKey: ["properties"] });
      void queryClient.invalidateQueries({ queryKey: ["properties", archivedProperty.id] });
    },
    onError: () => setPropertyMessage({ text: "Објектот не беше архивиран. Обидете се повторно.", tone: "error" }),
  });

  const createPropertyContactMutation = useMutation({
    mutationFn: (payload: ContactCreateRequest) => {
      if (!selectedPropertyId) {
        throw new Error("Missing selected property");
      }

      return createPropertyContact(selectedPropertyId, payload);
    },
    onSuccess: () => {
      setPropertyMessage({ text: "Контактот за објектот е додаден.", tone: "success" });
      setPropertyContactForm(emptyContactForm);
      void queryClient.invalidateQueries({ queryKey: ["property-contacts", selectedPropertyId] });
    },
    onError: () => setPropertyMessage({ text: "Контактот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const createPropertyNoteMutation = useMutation({
    mutationFn: (payload: PropertyNoteFormState) => {
      if (!selectedPropertyId) {
        throw new Error("Missing selected property");
      }

      return createPropertyNote(selectedPropertyId, { content: payload.content.trim() });
    },
    onSuccess: () => {
      setPropertyMessage({ text: "Белешката е додадена.", tone: "success" });
      setPropertyNoteForm(emptyPropertyNoteForm);
      void queryClient.invalidateQueries({ queryKey: ["property-notes", selectedPropertyId] });
    },
    onError: () => setPropertyMessage({ text: "Белешката не беше додадена. Обидете се повторно.", tone: "error" }),
  });

  function handleCustomerField(field: keyof CustomerFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setCustomerForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCustomerEditField(field: keyof CustomerFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setCustomerEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCustomerContactField(field: keyof ContactFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setCustomerContactForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handlePropertyField(field: keyof PropertyFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setPropertyForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handlePropertyEditField(field: keyof PropertyFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setPropertyEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handlePropertyContactField(field: keyof ContactFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setPropertyContactForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function selectCustomer(customer: CustomerResponse) {
    setSelectedCustomerId(customer.id);
    setCustomerEditForm(customerFormFromEntity(customer));
    setCustomerMessage(null);
  }

  function selectProperty(property: PropertyResponse) {
    setSelectedPropertyId(property.id);
    setPropertyEditForm(propertyFormFromEntity(property));
    setPropertyMessage(null);
  }

  function handleCreateCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = customerPayloadFromForm(customerForm);

    if (!payload.name) {
      setCustomerMessage({ text: "Внесете име на клиент.", tone: "error" });
      return;
    }

    createCustomerMutation.mutate(payload);
  }

  function handleUpdateCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = customerPayloadFromForm(customerEditForm);

    if (!payload.name) {
      setCustomerMessage({ text: "Внесете име на клиент.", tone: "error" });
      return;
    }

    updateCustomerMutation.mutate(payload);
  }

  function handleCreateCustomerContact(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = contactPayloadFromForm(customerContactForm);

    if (!payload.full_name) {
      setCustomerMessage({ text: "Внесете име на контакт.", tone: "error" });
      return;
    }

    createCustomerContactMutation.mutate(payload);
  }

  function handleCreateProperty(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = propertyPayloadFromForm(propertyForm);

    if (!payload.customer_id) {
      setPropertyMessage({ text: "Изберете клиент за објектот.", tone: "error" });
      return;
    }

    if (!payload.name) {
      setPropertyMessage({ text: "Внесете име на објект.", tone: "error" });
      return;
    }

    createPropertyMutation.mutate(payload);
  }

  function handleUpdateProperty(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = propertyPayloadFromForm(propertyEditForm);

    if (!payload.name) {
      setPropertyMessage({ text: "Внесете име на објект.", tone: "error" });
      return;
    }

    updatePropertyMutation.mutate(payload);
  }

  function handleCreatePropertyContact(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = contactPayloadFromForm(propertyContactForm);

    if (!payload.full_name) {
      setPropertyMessage({ text: "Внесете име на контакт.", tone: "error" });
      return;
    }

    createPropertyContactMutation.mutate(payload);
  }

  function handleCreatePropertyNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!propertyNoteForm.content.trim()) {
      setPropertyMessage({ text: "Внесете белешка за објект.", tone: "error" });
      return;
    }

    createPropertyNoteMutation.mutate(propertyNoteForm);
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Клиенти</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Управувајте со клиентите, нивните контакти, објекти и белешки преку серверот.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section aria-label="Клиенти" className="space-y-4">
          <Panel title="Додај клиент">
            <form className="grid gap-3" onSubmit={handleCreateCustomer}>
              <FormField
                label="Име на клиент"
                name="customer-name"
                value={customerForm.name}
                required
                onChange={handleCustomerField("name")}
              />
              <div className="grid gap-3 md:grid-cols-2">
                <FormField
                  label="Телефон на клиент"
                  name="customer-phone"
                  value={customerForm.phone}
                  onChange={handleCustomerField("phone")}
                />
                <FormField
                  label="Е-пошта на клиент"
                  name="customer-email"
                  type="email"
                  value={customerForm.email}
                  onChange={handleCustomerField("email")}
                />
              </div>
              <FormField
                label="Адреса на клиент"
                name="customer-address"
                value={customerForm.address}
                onChange={handleCustomerField("address")}
              />
              <TextAreaField
                label="Белешка за клиент"
                name="customer-note"
                value={customerForm.note}
                onChange={handleCustomerField("note")}
              />
              <div>
                <PrimaryButton disabled={createCustomerMutation.isPending}>
                  {createCustomerMutation.isPending ? "Се додава..." : "Додај клиент"}
                </PrimaryButton>
              </div>
            </form>
          </Panel>

          <Panel title="Листа на клиенти">
            {customersQuery.isLoading ? <Message>Се вчитуваат клиенти...</Message> : null}
            {customersQuery.isError ? <Message tone="error">Клиентите не може да се вчитаат.</Message> : null}
            {!customersQuery.isLoading && customersQuery.data?.length === 0 ? (
              <Message>Нема додадени клиенти. Започнете со формата погоре.</Message>
            ) : null}
            <div className="grid gap-2">
              {(customersQuery.data ?? []).map((customer) => (
                <button
                  key={customer.id}
                  type="button"
                  onClick={() => selectCustomer(customer)}
                  className={[
                    "rounded-md border px-3 py-3 text-left text-sm transition focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2",
                    selectedCustomerId === customer.id
                      ? "border-brand bg-teal-50 text-ink"
                      : "border-line bg-white hover:border-brand",
                  ].join(" ")}
                >
                  <span className="block font-semibold">{customer.name}</span>
                  <span className="mt-1 block text-slate-600">{displayValue(customer.phone)}</span>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Детали за клиент">
            {!selectedCustomerId ? <Message>Изберете клиент за да ги видите деталите.</Message> : null}
            {selectedCustomerQuery.isLoading ? <Message>Се вчитува клиентот...</Message> : null}
            {selectedCustomerQuery.isError ? <Message tone="error">Клиентот не може да се вчита.</Message> : null}
            {selectedCustomerQuery.data ? (
              <div className="space-y-4">
                <dl className="grid gap-3 md:grid-cols-2">
                  <DetailRow label="Име" value={selectedCustomerQuery.data.name} />
                  <DetailRow label="Статус" value={formatStatus(selectedCustomerQuery.data.status)} />
                  <DetailRow label="Телефон" value={selectedCustomerQuery.data.phone} />
                  <DetailRow label="Е-пошта" value={selectedCustomerQuery.data.email} />
                  <DetailRow label="Адреса" value={selectedCustomerQuery.data.address} />
                  <DetailRow label="Белешка" value={selectedCustomerQuery.data.note} />
                </dl>

                <form className="grid gap-3 border-t border-line pt-4" onSubmit={handleUpdateCustomer}>
                  <h3 className="text-sm font-bold text-ink">Уреди клиент</h3>
                  <FormField
                    label="Име за уредување"
                    name="customer-edit-name"
                    value={customerEditForm.name}
                    required
                    onChange={handleCustomerEditField("name")}
                  />
                  <div className="grid gap-3 md:grid-cols-2">
                    <FormField
                      label="Телефон за уредување"
                      name="customer-edit-phone"
                      value={customerEditForm.phone}
                      onChange={handleCustomerEditField("phone")}
                    />
                    <FormField
                      label="Е-пошта за уредување"
                      name="customer-edit-email"
                      type="email"
                      value={customerEditForm.email}
                      onChange={handleCustomerEditField("email")}
                    />
                  </div>
                  <TextAreaField
                    label="Белешка за уредување"
                    name="customer-edit-note"
                    value={customerEditForm.note}
                    onChange={handleCustomerEditField("note")}
                  />
                  <div className="flex flex-wrap gap-2">
                    <SecondaryButton type="submit" disabled={updateCustomerMutation.isPending}>
                      <Save aria-hidden="true" className="h-4 w-4" />
                      {updateCustomerMutation.isPending ? "Се зачувува..." : "Зачувај клиент"}
                    </SecondaryButton>
                    <SecondaryButton
                      disabled={archiveCustomerMutation.isPending}
                      onClick={() => archiveCustomerMutation.mutate(selectedCustomerQuery.data.id)}
                    >
                      <Archive aria-hidden="true" className="h-4 w-4" />
                      Архивирај клиент
                    </SecondaryButton>
                  </div>
                </form>

                <div className="border-t border-line pt-4">
                  <h3 className="text-sm font-bold text-ink">Контакти за клиент</h3>
                  {customerContactsQuery.isLoading ? <Message>Се вчитуваат контакти...</Message> : null}
                  {customerContactsQuery.isError ? <Message tone="error">Контактите не може да се вчитаат.</Message> : null}
                  {(customerContactsQuery.data ?? []).length === 0 && !customerContactsQuery.isLoading ? (
                    <Message>Нема контакти за овој клиент.</Message>
                  ) : null}
                  <ul className="mt-3 grid gap-2">
                    {(customerContactsQuery.data ?? []).map((contact) => (
                      <li key={contact.id} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm">
                        <p className="font-semibold text-ink">{contact.full_name}</p>
                        <p className="text-slate-600">{displayValue(contact.phone)}</p>
                        {contact.role ? <p className="text-slate-600">{contact.role}</p> : null}
                      </li>
                    ))}
                  </ul>
                  <form className="mt-4 grid gap-3" onSubmit={handleCreateCustomerContact}>
                    <FormField
                      label="Име на контакт"
                      name="customer-contact-name"
                      value={customerContactForm.full_name}
                      required
                      onChange={handleCustomerContactField("full_name")}
                    />
                    <div className="grid gap-3 md:grid-cols-2">
                      <FormField
                        label="Телефон на контакт"
                        name="customer-contact-phone"
                        value={customerContactForm.phone}
                        onChange={handleCustomerContactField("phone")}
                      />
                      <FormField
                        label="Улога на контакт"
                        name="customer-contact-role"
                        value={customerContactForm.role}
                        onChange={handleCustomerContactField("role")}
                      />
                    </div>
                    <div>
                      <PrimaryButton disabled={createCustomerContactMutation.isPending}>
                        {createCustomerContactMutation.isPending ? "Се додава..." : "Додај контакт"}
                      </PrimaryButton>
                    </div>
                  </form>
                </div>
              </div>
            ) : null}
            {customerMessage ? <div className="mt-4"><Message tone={customerMessage.tone}>{customerMessage.text}</Message></div> : null}
          </Panel>
        </section>

        <section aria-label="Објекти" className="space-y-4">
          <Panel title="Објекти">
            <form className="grid gap-3" onSubmit={handleCreateProperty}>
              <label htmlFor="property-customer-id" className="block text-sm font-semibold text-slate-700">
                Клиент за објект
                <select
                  id="property-customer-id"
                  name="property-customer-id"
                  value={propertyForm.customer_id}
                  onChange={handlePropertyField("customer_id")}
                  required
                  className="ui-select"
                >
                  <option value="">Изберете клиент</option>
                  {(customersQuery.data ?? []).map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name}
                    </option>
                  ))}
                </select>
              </label>
              <FormField
                label="Име на објект"
                name="property-name"
                value={propertyForm.name}
                required
                onChange={handlePropertyField("name")}
              />
              <div className="grid gap-3 md:grid-cols-2">
                <FormField
                  label="Адреса на објект"
                  name="property-address"
                  value={propertyForm.address}
                  onChange={handlePropertyField("address")}
                />
                <FormField
                  label="Град"
                  name="property-city"
                  value={propertyForm.city}
                  onChange={handlePropertyField("city")}
                />
              </div>
              <TextAreaField
                label="Белешка за објект"
                name="property-note"
                value={propertyForm.note}
                onChange={handlePropertyField("note")}
              />
              <div>
                <PrimaryButton disabled={createPropertyMutation.isPending}>
                  {createPropertyMutation.isPending ? "Се додава..." : "Додај објект"}
                </PrimaryButton>
              </div>
            </form>
          </Panel>

          <Panel title="Листа на објекти">
            {propertiesQuery.isLoading ? <Message>Се вчитуваат објекти...</Message> : null}
            {propertiesQuery.isError ? <Message tone="error">Објектите не може да се вчитаат.</Message> : null}
            {!propertiesQuery.isLoading && propertiesQuery.data?.length === 0 ? (
              <Message>Нема додадени објекти.</Message>
            ) : null}
            <div className="grid gap-2">
              {(propertiesQuery.data ?? []).map((property) => (
                <button
                  key={property.id}
                  type="button"
                  onClick={() => selectProperty(property)}
                  className={[
                    "rounded-md border px-3 py-3 text-left text-sm transition focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2",
                    selectedPropertyId === property.id
                      ? "border-brand bg-teal-50 text-ink"
                      : "border-line bg-white hover:border-brand",
                  ].join(" ")}
                >
                  <span className="block font-semibold">{property.name}</span>
                  <span className="mt-1 block text-slate-600">{displayValue(property.city)}</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    Клиент: {customerById.get(property.customer_id) ?? "Непознат клиент"}
                  </span>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Детали за објект">
            {!selectedPropertyId ? <Message>Изберете објект за да ги видите деталите.</Message> : null}
            {selectedPropertyQuery.isLoading ? <Message>Се вчитува објектот...</Message> : null}
            {selectedPropertyQuery.isError ? <Message tone="error">Објектот не може да се вчита.</Message> : null}
            {selectedPropertyQuery.data ? (
              <div className="space-y-4">
                <dl className="grid gap-3 md:grid-cols-2">
                  <DetailRow label="Име" value={selectedPropertyQuery.data.name} />
                  <DetailRow label="Статус" value={formatStatus(selectedPropertyQuery.data.status)} />
                  <DetailRow label="Клиент" value={customerById.get(selectedPropertyQuery.data.customer_id)} />
                  <DetailRow label="Град" value={selectedPropertyQuery.data.city} />
                  <DetailRow label="Адреса" value={selectedPropertyQuery.data.address} />
                  <DetailRow label="Белешка" value={selectedPropertyQuery.data.note} />
                </dl>

                <form className="grid gap-3 border-t border-line pt-4" onSubmit={handleUpdateProperty}>
                  <h3 className="text-sm font-bold text-ink">Уреди објект</h3>
                  <FormField
                    label="Име на објект за уредување"
                    name="property-edit-name"
                    value={propertyEditForm.name}
                    required
                    onChange={handlePropertyEditField("name")}
                  />
                  <div className="grid gap-3 md:grid-cols-2">
                    <FormField
                      label="Адреса за уредување"
                      name="property-edit-address"
                      value={propertyEditForm.address}
                      onChange={handlePropertyEditField("address")}
                    />
                    <FormField
                      label="Град за уредување"
                      name="property-edit-city"
                      value={propertyEditForm.city}
                      onChange={handlePropertyEditField("city")}
                    />
                  </div>
                  <TextAreaField
                    label="Белешка за објект за уредување"
                    name="property-edit-note"
                    value={propertyEditForm.note}
                    onChange={handlePropertyEditField("note")}
                  />
                  <div className="flex flex-wrap gap-2">
                    <SecondaryButton type="submit" disabled={updatePropertyMutation.isPending}>
                      <Save aria-hidden="true" className="h-4 w-4" />
                      {updatePropertyMutation.isPending ? "Се зачувува..." : "Зачувај објект"}
                    </SecondaryButton>
                    <SecondaryButton
                      disabled={archivePropertyMutation.isPending}
                      onClick={() => archivePropertyMutation.mutate(selectedPropertyQuery.data.id)}
                    >
                      <Archive aria-hidden="true" className="h-4 w-4" />
                      Архивирај објект
                    </SecondaryButton>
                  </div>
                </form>

                <div className="border-t border-line pt-4">
                  <h3 className="text-sm font-bold text-ink">Контакти за објект</h3>
                  {propertyContactsQuery.isLoading ? <Message>Се вчитуваат контакти...</Message> : null}
                  {propertyContactsQuery.isError ? <Message tone="error">Контактите не може да се вчитаат.</Message> : null}
                  {(propertyContactsQuery.data ?? []).length === 0 && !propertyContactsQuery.isLoading ? (
                    <Message>Нема контакти за овој објект.</Message>
                  ) : null}
                  <ul className="mt-3 grid gap-2">
                    {(propertyContactsQuery.data ?? []).map((contact) => (
                      <li key={contact.id} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm">
                        <p className="font-semibold text-ink">{contact.full_name}</p>
                        <p className="text-slate-600">{displayValue(contact.phone)}</p>
                        {contact.role ? <p className="text-slate-600">{contact.role}</p> : null}
                      </li>
                    ))}
                  </ul>
                  <form className="mt-4 grid gap-3" onSubmit={handleCreatePropertyContact}>
                    <FormField
                      label="Име на контакт за објект"
                      name="property-contact-name"
                      value={propertyContactForm.full_name}
                      required
                      onChange={handlePropertyContactField("full_name")}
                    />
                    <div className="grid gap-3 md:grid-cols-2">
                      <FormField
                        label="Телефон на контакт за објект"
                        name="property-contact-phone"
                        value={propertyContactForm.phone}
                        onChange={handlePropertyContactField("phone")}
                      />
                      <FormField
                        label="Улога на контакт за објект"
                        name="property-contact-role"
                        value={propertyContactForm.role}
                        onChange={handlePropertyContactField("role")}
                      />
                    </div>
                    <div>
                      <PrimaryButton disabled={createPropertyContactMutation.isPending}>
                        {createPropertyContactMutation.isPending ? "Се додава..." : "Додај контакт за објект"}
                      </PrimaryButton>
                    </div>
                  </form>
                </div>

                <div className="border-t border-line pt-4">
                  <h3 className="text-sm font-bold text-ink">Белешки за објект</h3>
                  {propertyNotesQuery.isLoading ? <Message>Се вчитуваат белешки...</Message> : null}
                  {propertyNotesQuery.isError ? <Message tone="error">Белешките не може да се вчитаат.</Message> : null}
                  {(propertyNotesQuery.data ?? []).length === 0 && !propertyNotesQuery.isLoading ? (
                    <Message>Нема белешки за овој објект.</Message>
                  ) : null}
                  <ul className="mt-3 grid gap-2">
                    {(propertyNotesQuery.data ?? []).map((note) => (
                      <li key={note.id} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm text-slate-700">
                        {note.content}
                      </li>
                    ))}
                  </ul>
                  <form className="mt-4 grid gap-3" onSubmit={handleCreatePropertyNote}>
                    <TextAreaField
                      label="Нова белешка за објект"
                      name="property-new-note"
                      value={propertyNoteForm.content}
                      onChange={(event) => setPropertyNoteForm({ content: event.target.value })}
                    />
                    <div>
                      <PrimaryButton disabled={createPropertyNoteMutation.isPending}>
                        {createPropertyNoteMutation.isPending ? "Се додава..." : "Додај белешка"}
                      </PrimaryButton>
                    </div>
                  </form>
                </div>
              </div>
            ) : null}
            {propertyMessage ? <div className="mt-4"><Message tone={propertyMessage.tone}>{propertyMessage.text}</Message></div> : null}
          </Panel>
        </section>
      </div>
    </section>
  );
}
