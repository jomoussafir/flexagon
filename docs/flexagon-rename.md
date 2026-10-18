# Flexagon rename — 18 October 2026

Canonical website: https://www.flexagon.fr/

> Latest verified state: OVH already provisions www.flexagon.fr automatically as
> an alias. The certificate covers both Flexagon names. Direct certificate-verified
> HTTPS to 188.165.51.93 returns 301 from www to https://flexagon.fr/. OVH's authoritative
> DNS and public resolvers 1.1.1.1 and 8.8.8.8 all return 188.165.51.93. This Mac's
> resolver still returns the old OVH parking IP 213.186.33.5; that caused the earlier
> connection-reset diagnosis. Earlier statements below calling this a missing
> hosting mapping/certificate are superseded. Duplicate www domain creation is
> unnecessary. The remaining change is WordPress's home/site URL to the www alias.


The entire source folder was copied to `/Users/msfr/Documents/flexagon`, including
private data, local WordPress, dependencies, backups and Git history. The original
folder was left intact. Website headings, accessibility text, page titles, account
email subjects, WordPress plugin/theme names and paths, package names, documentation,
iPhone display name, Xcode project/scheme and hosted website URL now use Flexagon.
The existing logo is retained. Local preview uses http://127.0.0.1:9410/.

## Compatibility and archives

The `lpdj`/`LPDJ` internal database keys, roles, post types, REST endpoints, request
headers and encrypted-storage names remain unchanged so existing catalogue,
accounts, permissions and ciphertext stay readable. Renaming these requires a data
migration and offers no visible branding change. Historical backups, private source
exports, copied WordPress state and Git history retain their original content.
Previous deployment ZIPs are preserved under `dist/pre-flexagon/`; deploy only the
new Flexagon packages. The existing external review service URL is retained because
that independently hosted service has not moved.

## Hosting

Target OVH account: same account as the predecessor. Before declaring the move live,
verify the domain mapping and HTTPS certificate, back up the hosted database, install
the Flexagon packages, deactivate the predecessor plugin, select the Flexagon theme,
change WordPress home/site URLs and site title, and update embedded old-origin URLs
using a serialization-aware database replacement. Check login, protected content,
reference PDFs and mail links. Redirect the old domain after the new site passes.
Do not copy the local database over the hosted member database.

Local build/test results and live deployment status are recorded below.

## Verified results

- Website build and both Flexagon 0.2.1 ZIP packages: passed.
- 60 isolated WordPress integration checks: passed.
- 8 LaTeX checks and 7 progress checks: passed.
- Shared branding consistency: passed.
- Renamed Xcode project, target and scheme recognized; Debug simulator build succeeded.
- Local HTTP homepage and session: 200; Flexagon theme active, no predecessor brand in homepage HTML.
- Local administrator catalogue: 1,856 problems.
- All 250 private-data files and 23 backup files match the original byte-for-byte.
- OVH completed a full hosting backup and the flexagon.fr domain association on 18 October.
- https://flexagon.fr/ responds with HTTP 200 and private/no-store headers.
- www.flexagon.fr association and HTTPS remain unverified; the OVH subdomain form did not produce a visible completed association.
- Hosted WordPress administrator access was established. Flexagon plugin 0.2.1 is installed and active; the predecessor plugin is inactive. The theme archive is awaiting manual selection in Chrome because its upload helper lacks file access. The canonical address and live site title are not yet changed.
- OVH DNS has matching A records (188.165.51.93) for flexagon.fr and www.flexagon.fr. The hosting panel still lists only flexagon.fr and the predecessor domain; repeated www submissions have not produced a visible association. Do not switch WordPress to www until its HTTPS hosting association is verified.

The renamed iPhone app uses bundle identifier com.flexagon.community. It installs
as a separate app; existing App Store/signing identities are not migrated by this copy.

## Live update after theme selection

Flexagon plugin and theme 0.2.1 are installed and active on OVH. The WordPress
site title is Flexagon, and OVH lists flexagon.fr as the primary domain.
https://flexagon.fr/ returns HTTP 200, serves the Flexagon theme, contains no
predecessor brand in homepage HTML, and retains private/no-store headers.
The public session endpoint returns 200 and the anonymous problems endpoint
returns 401. The authenticated live admin review still shows 1,856 submissions.
The predecessor domain still serves the same renamed site (no redirect yet).

www.flexagon.fr still resets its TLS connection. Repeated domain submissions
through OVH's managed-WordPress form did not create a visible association.
The official OVH API console supports updating the website's domains and primary
FQDN, but its OAuth consent requests management of the whole account and all
services. Approval is pending before granting that broader access. The final
canonical www address and old-domain redirects remain unfinished.

## Official OVH API result

The owner authorized the official OVH API console. Its authenticated GET confirmed
the website is READY with no current tasks and primaryFQDN flexagon.fr.
Current and target domains are le-probleme-du-jour.fr, flexagon.fr and
00950f03e7.0ea.mcms.ovh.net.

A narrowly scoped PUT preserved all three mappings and added only
www.flexagon.fr to targetSpec.domains. OVH returned HTTP 400:
`Client::BadRequest: could not request domain creation for "www.flexagon.fr"`.
The final www association is blocked by the hosting backend, not by the local
project or a missing approval. Do not change WordPress to the failing www host.
OVH support must resolve the domain-creation failure before HTTPS verification,
primary-domain promotion to www and old-domain redirects can be completed.


## Support ticket submitted

With the owner's explicit authorization, OVH ticket **CS16961562** was created
on 18 October 2026 at 07:46:41 Paris time. Status: Nouveau. The ticket contains
the prepared domain-provisioning request and exact HTTP 400 error.

https://help.ovhcloud.com/csm?id=csm_ticket&table=sn_customerservice_case&sys_id=aa0beaf8f5cc1750de96fa2f34c71a27

The working site remains https://flexagon.fr/. The www mapping, HTTPS validation,
final primary address and redirects remain pending OVH's response.

## Comparison with the predecessor domain

The original www.le-probleme-du-jour.fr alias also works without being listed as
a separate domain in OVH's current/target domain arrays. The server certificate
already includes the technical hostname and both bare/www forms of both domains.
No domain detachment, site recreation, data reimport or certificate replacement is
required. The official API refuses primaryFQDN www.flexagon.fr because the hosting
resource manages the bare domain; WordPress's canonical URL can use the valid alias.

A regular dscacheutil cache flush did not refresh this Mac's answer. Refreshing the
mDNSResponder cache requires a local administrator password, which was not entered.
Chrome already reaches the correct www host.
