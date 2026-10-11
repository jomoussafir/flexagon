# Shared data contract — planning

The website, iPhone and future Android app will use one WordPress service. Endpoints
have not been implemented; final schemas will be versioned here with the code.

Preserve stable problem IDs, bilingual title and LaTeX text, per-language review and
publication status, keywords, category, difficulty 1–5, sources/page references,
author attribution, figure filenames and revision history.

The inherited iPhone reader uses schema version 1 in `PublishedCatalogue` (see
`ios/ProblemOfTheDay/App/Models.swift`). Its old feed is intentionally disconnected.
The new authenticated API must not expose drafts through a public catalogue route.
Contributors may access their own drafts; admins review all submissions; verified
members read published versions. Database checks must enforce these permissions.
