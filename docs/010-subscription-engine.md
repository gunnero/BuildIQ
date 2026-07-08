# Subscription Engine

The Subscription Engine manages BuildIQ platform access for companies.

This is separate from customer payments on construction projects.

## V1 Subscription Model

V1 supports manual subscription payments by bank transfer.

BuildIQ HQ reviews manual payments and updates company subscription status.

## Core Concepts

### Plans

Plans define what a company can access.

Plan examples:

- Starter
- Professional
- Business

Final plan packaging will be decided before commercial launch.

### Subscriptions

A subscription links a company to a plan and status.

Subscription statuses may include:

- `trialing`
- `active`
- `past_due`
- `suspended`
- `cancelled`

### Manual Subscription Payments

Manual bank transfer payments must store:

- Company
- Subscription
- Amount in MKD
- Payment date
- Bank reference
- Status
- HQ reviewer
- Review date
- Note

Manual payment statuses may include:

- `pending_review`
- `approved`
- `rejected`
- `voided`

## BuildIQ HQ Workflow

1. Company sends bank transfer.
2. BuildIQ HQ records or reviews the payment.
3. HQ approves or rejects the payment.
4. Subscription status is updated.
5. Audit log records the decision.

## Future Online Payment Provider Abstraction

Future online payments must use a provider abstraction.

The domain should model:

- Payment provider
- Provider customer reference
- Provider subscription reference
- Provider invoice reference
- Provider payment reference
- Webhook event snapshot

The product must not hard-code a provider into business logic.

## V1 Prohibitions

Do not add online payment provider SDKs in V1.

Do not add provider-specific webhook code in the Blueprint scaffold.

Do not mix BuildIQ subscription payments with construction project payments.

## Feature Flags

Subscription state may activate feature flags for a company.

Feature flags must still be resolved by backend authorization logic.
