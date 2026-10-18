# OVH support request — www.flexagon.fr domain creation failure

Please resolve a Managed Hosting for WordPress domain-mapping failure.

Resource: 7e282435-69cd-4ec7-b460-4721b2c3fe78
Website: 25001813-0b83-4b14-b848-3feaf223fd6a
Technical hostname: 00950f03e7.0ea.mcms.ovh.net
Working current primary domain: flexagon.fr
Required final primary domain: www.flexagon.fr

The website is READY and has no current tasks. The existing mapped domains are
flexagon.fr, le-probleme-du-jour.fr and its technical hostname. Both flexagon.fr
and www.flexagon.fr have DNS A records pointing to 188.165.51.93.
https://flexagon.fr returns HTTP 200 with the correct website. HTTPS for
www.flexagon.fr fails with a connection reset.

The control-panel Add Domain form did not add www.flexagon.fr. On 18 October 2026,
the authenticated official API console was used for:
PUT /v2/managedCMS/resource/7e282435-69cd-4ec7-b460-4721b2c3fe78/website/25001813-0b83-4b14-b848-3feaf223fd6a

The request changed only targetSpec.domains, preserving the three current mappings
and adding {"fqdn":"www.flexagon.fr"}. The response was HTTP 400:
{"class":"Client::BadRequest","message":"could not request domain creation for \"www.flexagon.fr\""}

Please provision the www.flexagon.fr mapping and valid HTTPS certificate, or identify
the precise conflicting configuration. Preserve the existing website, database,
accounts, private content and working domain mappings. We will promote www to the
primary domain only once its HTTPS access has been verified.


## Support ticket submitted

With the owner's explicit authorization, OVH ticket **CS16961562** was created
on 18 October 2026 at 07:46:41 Paris time. Status: Nouveau. The ticket contains
the prepared domain-provisioning request and exact HTTP 400 error.

https://help.ovhcloud.com/csm?id=csm_ticket&table=sn_customerservice_case&sys_id=aa0beaf8f5cc1750de96fa2f34c71a27

The working site remains https://flexagon.fr/. The www mapping, HTTPS validation,
final primary address and redirects remain pending OVH's response.
