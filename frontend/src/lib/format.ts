export function formatNumber(value: number): string {
  return value.toFixed(4).replace(/\.?0+$/, "");
}

function toDate(value: string): Date | null {
  const parsedDate = new Date(value);
  return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
}

function twoDigits(value: number): string {
  return value.toString().padStart(2, "0");
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "Не е внесено";
  }

  const parsedDate = toDate(value);
  if (!parsedDate) {
    return value;
  }

  return `${twoDigits(parsedDate.getDate())}.${twoDigits(parsedDate.getMonth() + 1)}.${parsedDate.getFullYear()}`;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "Не е внесено";
  }

  const parsedDate = toDate(value);
  if (!parsedDate) {
    return value;
  }

  return `${formatDate(value)}, ${twoDigits(parsedDate.getHours())}:${twoDigits(parsedDate.getMinutes())}`;
}

export function formatUnit(unit: string | null | undefined): string {
  if (!unit) {
    return "";
  }

  const labels: Record<string, string> = {
    bag: "вреќа",
    bucket: "кофа",
    hour: "час",
    kg: "kg",
    liter: "литар",
    m: "m",
    m2: "m²",
    m3: "m³",
    piece: "парче",
    roll: "ролна",
  };

  return labels[unit] ?? unit;
}
