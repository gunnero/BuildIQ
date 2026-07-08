const companyStatusLabels: Record<string, string> = {
  active: "Активна",
  inactive: "Неактивна",
  suspended: "Суспендирана",
  archived: "Архивирана",
};

const subscriptionStatusLabels: Record<string, string> = {
  active: "Активна",
  trialing: "Пробна",
  past_due: "Доцни",
  suspended: "Суспендирана",
  cancelled: "Откажана",
  expired: "Истечена",
};

export function formatCompanyStatus(status: string | undefined): string {
  if (!status) {
    return "Непозната";
  }

  return companyStatusLabels[status] ?? status;
}

export function formatSubscriptionStatus(status: string | undefined): string {
  if (!status) {
    return "Непозната";
  }

  return subscriptionStatusLabels[status] ?? status;
}
