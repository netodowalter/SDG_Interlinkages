# Additional IGES and JRC aggregate codes

The region selector retains the continental regions and adds five explicitly matched entries from the official UNSD GeoArea/List catalog. The same JSON catalog is used by the GitHub/Gradio package and the webapp.

| UNSD code | UNSD catalog label | SDGIndex comparison |
| --- | --- | --- |
| 198 | Organisation for Economic Co-operation and Development (OECD) Member States | OECD |
| 910 | High income economies (WB) | HIC |
| 911 | Low income economies (WB) | LIC |
| 912 | Lower middle economies (WB) | LMIC |
| 914 | Upper middle economies (WB) | UMIC |

Source: https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/GeoArea/List (verified 2026-11-04 UTC).

## Availability and comparability

These are real API identifiers, not newly constructed aggregates. During verification, Indicator/Data returned no observations for the selected aggregate codes, including a query without an indicator restriction. The World control returned observations, confirming that the endpoint and geographic filter worked. Catalog membership alone therefore does not establish usable data coverage. Selecting an aggregate retries live collection; an empty response is reported explicitly rather than replaced with another area's data.

The webapp displays this limitation when an additional aggregate is selected. Gradio describes it below the IGES/JRC selector. An uploaded CSV for the matching code can still be used in Gradio if appropriate observations are available separately. Coverage, country membership, reference year for income classification and aggregation rules must be checked before comparing with SDGIndex. Do not equate the two methods' group names with identical composition.

BRICS and BRICSplus have no entry in the verified UNSD catalog and are not added under invented codes. Creating them from country series requires a separately specified aggregation method. Middle East and North Africa (ILO) is also not silently substituted for the SDGIndex MENA group.
