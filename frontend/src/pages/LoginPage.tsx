import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { LogIn } from "lucide-react";
import { useForm } from "react-hook-form";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/useAuth";

const loginSchema = z.object({
  email: z.string().email("Внесете валидна е-пошта."),
  password: z.string().min(1, "Внесете лозинка."),
});

type LoginFormValues = z.infer<typeof loginSchema>;

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const { isAuthenticated, isLoadingSession, login, sessionError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;
  const destination = state?.from?.pathname ?? "/dashboard";

  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const loginMutation = useMutation({
    mutationFn: (values: LoginFormValues) => login(values),
    onSuccess: () => {
      navigate(destination, { replace: true });
    },
  });

  if (isAuthenticated && !isLoadingSession) {
    return <Navigate to={destination} replace />;
  }

  if (isAuthenticated && isLoadingSession) {
    return (
      <main className="grid min-h-screen place-items-center bg-paper px-4 text-ink">
        <p className="ui-card text-sm font-semibold">
          Се вчитува сесијата...
        </p>
      </main>
    );
  }

  const errorMessage =
    loginMutation.error instanceof ApiError && loginMutation.error.status === 401
      ? "Е-поштата или лозинката не се точни."
      : "Најавата не успеа. Проверете ги податоците и обидете се повторно.";
  const visibleErrorMessage = loginMutation.isError ? errorMessage : sessionError;

  return (
    <main className="grid min-h-screen place-items-center bg-paper px-4 py-10 text-ink">
      <section className="ui-card w-full max-w-md p-6">
        <div className="mb-6">
          <p className="text-sm font-semibold text-brand">BuildIQ</p>
          <h1 className="mt-2 text-2xl font-bold tracking-normal">Најава</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Најавете се за пристап до проектите, клиентите, понудите и финансиските записи.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit((values) => loginMutation.mutate(values))}>
          <div>
            <label htmlFor="email" className="ui-field-label">
              Е-пошта
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              className="ui-input h-11"
              {...register("email")}
            />
            {errors.email ? <p className="mt-2 text-sm text-red-700">{errors.email.message}</p> : null}
          </div>

          <div>
            <label htmlFor="password" className="ui-field-label">
              Лозинка
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="ui-input h-11"
              {...register("password")}
            />
            {errors.password ? <p className="mt-2 text-sm text-red-700">{errors.password.message}</p> : null}
          </div>

          {visibleErrorMessage ? (
            <div className="ui-message border-red-200 bg-red-50 text-red-800">
              {visibleErrorMessage}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="ui-button-primary h-11 w-full px-4"
          >
            <LogIn aria-hidden="true" className="h-4 w-4" />
            {loginMutation.isPending ? "Се најавувате..." : "Најава"}
          </button>
        </form>
      </section>
    </main>
  );
}
