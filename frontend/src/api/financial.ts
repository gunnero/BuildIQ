import { apiRequest } from "./client";
import type {
  ExpenseCategoryCreateRequest,
  ExpenseCategoryResponse,
  ExpenseCategoryUpdateRequest,
  ExpenseCreateRequest,
  ExpenseResponse,
  PaymentCreateRequest,
  PaymentResponse,
  ProjectFinancialSummaryResponse,
  ReverseRequest,
} from "./types";

export function listPayments(): Promise<PaymentResponse[]> {
  return apiRequest<PaymentResponse[]>("/api/v1/payments");
}

export function createPayment(payload: PaymentCreateRequest): Promise<PaymentResponse> {
  return apiRequest<PaymentResponse>("/api/v1/payments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getPayment(paymentId: string): Promise<PaymentResponse> {
  return apiRequest<PaymentResponse>(`/api/v1/payments/${paymentId}`);
}

export function reversePayment(paymentId: string, payload: ReverseRequest): Promise<PaymentResponse> {
  return apiRequest<PaymentResponse>(`/api/v1/payments/${paymentId}/reverse`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function archivePayment(paymentId: string): Promise<PaymentResponse> {
  return apiRequest<PaymentResponse>(`/api/v1/payments/${paymentId}/archive`, {
    method: "POST",
  });
}

export function getProjectFinancialSummary(projectId: string): Promise<ProjectFinancialSummaryResponse> {
  return apiRequest<ProjectFinancialSummaryResponse>(`/api/v1/projects/${projectId}/financial-summary`);
}

export function listExpenseCategories(): Promise<ExpenseCategoryResponse[]> {
  return apiRequest<ExpenseCategoryResponse[]>("/api/v1/expense-categories");
}

export function createExpenseCategory(payload: ExpenseCategoryCreateRequest): Promise<ExpenseCategoryResponse> {
  return apiRequest<ExpenseCategoryResponse>("/api/v1/expense-categories", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateExpenseCategory(
  categoryId: string,
  payload: ExpenseCategoryUpdateRequest,
): Promise<ExpenseCategoryResponse> {
  return apiRequest<ExpenseCategoryResponse>(`/api/v1/expense-categories/${categoryId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveExpenseCategory(categoryId: string): Promise<ExpenseCategoryResponse> {
  return apiRequest<ExpenseCategoryResponse>(`/api/v1/expense-categories/${categoryId}/archive`, {
    method: "POST",
  });
}

export function listExpenses(): Promise<ExpenseResponse[]> {
  return apiRequest<ExpenseResponse[]>("/api/v1/expenses");
}

export function createExpense(payload: ExpenseCreateRequest): Promise<ExpenseResponse> {
  return apiRequest<ExpenseResponse>("/api/v1/expenses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getExpense(expenseId: string): Promise<ExpenseResponse> {
  return apiRequest<ExpenseResponse>(`/api/v1/expenses/${expenseId}`);
}

export function reverseExpense(expenseId: string, payload: ReverseRequest): Promise<ExpenseResponse> {
  return apiRequest<ExpenseResponse>(`/api/v1/expenses/${expenseId}/reverse`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function archiveExpense(expenseId: string): Promise<ExpenseResponse> {
  return apiRequest<ExpenseResponse>(`/api/v1/expenses/${expenseId}/archive`, {
    method: "POST",
  });
}
