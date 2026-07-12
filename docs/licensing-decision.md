# BuildIQ Licensing Decision

## Decision required

BuildIQ is publicly visible but currently has no owner-approved license. Public visibility does not grant permission to copy, modify, redistribute, or operate the software. Until the owner makes an explicit decision, the repository should continue to state that all rights are reserved.

## Options

| Option | Commercial SaaS | Portfolio visibility | Competitor reuse | Contributor expectations |
|---|---|---|---|---|
| Proprietary source-visible | Preserves the strongest control over commercial use and redistribution | Code can remain visible for interview and portfolio review | Reuse is not licensed; enforcement still depends on clear terms and copyright law | External contributions are awkward without contributor terms and an explicit inbound-license policy |
| MIT | Fully permits commercial SaaS use by the owner and others | Familiar and highly recruiter-friendly | Competitors may copy, modify, sell, and host the software with attribution | Simple, low-friction expectations; broad ecosystem familiarity |
| Apache-2.0 | Fully permits commercial use and distribution | Strong open-source signal with explicit patent terms | Competitors may reuse and commercialize it under notice and license obligations | Clear contribution/patent framework, but more text and compliance overhead than MIT |

## Recommendation

**Use a proprietary source-visible posture for the current BuildIQ stage.** BuildIQ is positioned as a commercial SaaS product and an engineering portfolio, while limiting competitor reuse is an explicit consideration. MIT and Apache-2.0 cannot satisfy that reuse constraint: both permit competitors to run, modify, redistribute, and commercialize the code.

This recommendation requires clear repository terms drafted or reviewed for the intended jurisdictions; “all rights reserved” communicates the interim position but is not a complete contributor or evaluation license. If accepting external contributions becomes a real objective, define contributor terms before merging unsolicited patches.

## When to reconsider

- Choose **MIT** if maximizing adoption, examples, forks, and low-friction contributions becomes more important than limiting commercial reuse.
- Choose **Apache-2.0** if BuildIQ intentionally becomes an open-source ecosystem and explicit patent grants and defensive termination are valuable.
- Consider an open-core or separate commercial-license model only as a dedicated legal and product decision; do not improvise a custom license in a documentation commit.

## Next action

Obtain explicit owner approval for the proprietary source-visible direction and approved legal text. Only then add a `LICENSE` or source-available terms file and align README, contribution guidance, package metadata, and repository settings. No license file is added by this program.
