# OVH setup

Target: OVH Managed Hosting for WordPress, Pack 1 site, with the user's own domain.
Domain, activated hosting and WordPress administrator access have not yet been supplied.

Create the site through OVH's Managed hosting for WordPress area and connect the domain
from Mes sites. Keep a development installation restricted while the application is built.
Install only completed custom plugin/theme packages; do not deploy this entire repository.

Before importing live drafts, configure and verify access restrictions for the site,
API and files. Configure email confirmation and password-reset delivery. The managed
WordPress plan does not include email mailboxes by default; reuse an existing suitable
sending service or choose one during setup.

The new WordPress API and mobile authentication are not yet implemented. The new iPhone
app has no configured feed; it must not download from the original app's public feed.

OVH offer: https://www.ovhcloud.com/fr/managed-hosting-wordpress/
Setup: https://docs.ovhcloud.com/fr/guides/web-cloud/managed-hosting/wordpress
Domains: https://docs.ovhcloud.com/fr/guides/web-cloud/managed-hosting/wordpress-domain-link
