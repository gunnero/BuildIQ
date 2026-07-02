# AI Boundary

BuildIQ V1 must not include AI features.

## Rule

BuildIQ must never call LLM providers directly.

Direct integration with the following is prohibited:

- OpenAI
- Anthropic
- Gemini
- Any provider-specific LLM API
- Any provider SDK for model generation

## Future Integration Direction

When AI features are introduced later, BuildIQ will send work requests to OneFiveFour OS.

OneFiveFour OS owns:

- AI Employees
- Knowledge
- Brains
- Providers
- Assignments
- Brain Sessions
- Brain Responses

BuildIQ owns:

- Construction workflows
- Calculations
- Customers
- Projects
- Payments
- Expenses
- Reports
- PDFs

## Allowed in V1

- Deterministic construction formulas
- User-entered measurements
- User-entered material prices and labor values
- Generated material lists
- Generated estimates/offers
- Payment and expense tracking
- Macedonian PDF output

## Not Allowed in V1

- Prompt templates
- LLM provider API keys
- Direct model calls
- AI chat screens
- AI estimate generation
- AI document generation
- Provider-specific retry, usage, or billing logic

## Future Request Boundary

Future AI requests must use a product boundary similar to this:

1. BuildIQ creates a construction-domain request.
2. BuildIQ sends the request to OneFiveFour OS.
3. OneFiveFour OS chooses the AI Employee, Brain, Knowledge, Provider, Assignment, Brain Session, and Brain Response.
4. OneFiveFour OS returns a response to BuildIQ.
5. BuildIQ stores only the construction-domain result needed by BuildIQ workflows.

Provider details must not leak into BuildIQ.
