# Proposed correction to OVH ticket CS16961562

Further comparison with the predecessor domain has identified the actual cause of
our earlier connection failures: this Mac's resolver still returned the old OVH
parking address 213.186.33.5 for www.flexagon.fr.

OVH's authoritative DNS and public resolvers 1.1.1.1 and 8.8.8.8 correctly return
188.165.51.93. Connecting directly to that IP with normal TLS validation and SNI
www.flexagon.fr succeeds. The certificate already covers www.flexagon.fr, and the
server returns HTTP 301 to https://flexagon.fr/. Chrome reaches this alias correctly.

The original www.le-probleme-du-jour.fr alias likewise works without being listed
as a separate domain in the Managed WordPress domain array. It therefore appears
that www is provisioned automatically and our attempt to add it separately was
unnecessary. Please do not detach domains, re-provision the site, replace the
database or modify private content. We are completing the canonical www URL in
WordPress. The original provisioning incident can be closed.
