# Richmond BC Property Intelligence Dashboard — Complete Project Plan
## Building a Land Discovery Tool for Community Development

## Table of Contents
1. Executive Summary
2. Customer & Context
3. Problem Statement
4. Value Proposition
5. Use Cases
6. Glossary of Key Terms
7. System Architecture Overview
8. Data Sources — Complete Reference
9. Data Model & Join Strategy
10. Technical Roadmap — Phased Implementation
11. Phase 1: Foundation — Static Data Pipeline
12. Phase 2: Spatial Engine & Core Dashboard
13. Phase 3: Live Market Data Integration
14. Phase 4: Synagogue Site Suitability Scoring
15. Phase 5: Polish, Auth, and Deployment
16. Synagogue Suitability Criteria — Deep Dive
17. Infrastructure & Tooling Choices
18. Cost Estimates
19. Risks & Mitigations
20. Timeline
21. Appendices


## 1. Executive Summary
This document is the complete plan for building a web-based interactive map dashboard that combines public municipal data, provincial assessment data, and live real estate listing data for the city of Richmond, British Columbia, Canada. The dashboard answers a question that no existing tool can answer today:

"What land in central Richmond is available — either city-owned and unused, or currently for sale on the private market — that meets the specific zoning, size, location, and community requirements for building a new synagogue?"

The tool is designed to be general-purpose (useful for developers, city planners, housing advocates, investors, and brokers) but is specifically tuned with a scoring and filtering system for a Jewish community organization seeking a synagogue site in central Richmond.

The project assembles data that currently lives in four or five disconnected systems, joins it on common keys (parcel identifiers and spatial coordinates), and presents it through a single searchable, filterable map interface. No new data is created — existing public and semi-public data is stitched together to answer questions none of the source systems can answer alone.

## 2. Customer & Context
### 2.1 Who is the primary customer?
The Jewish community of Richmond, BC — specifically, the leadership committee (board of directors, rabbi, and volunteer planning committee) tasked with finding a suitable site for a new synagogue (also called a "shul" in Yiddish).

Richmond has a small but established Jewish community. As of recent census data, the Jewish population in the Metro Vancouver area is approximately 26,000–30,000, with a portion residing in Richmond. The community currently may use rented spaces, converted houses, or travel to Vancouver for services. A purpose-built synagogue in central Richmond would serve as:

- A place of worship (Shabbat services, High Holidays, daily minyan)
- A community gathering center (social hall, kitchen for kosher catering)
- An educational facility (Hebrew school, adult learning)
- Administrative offices for the congregation
### 2.2 Why Richmond specifically?
Richmond is a city of approximately 220,000 people located on islands in the Fraser River delta, directly south of Vancouver. Key facts relevant to this project:

- Land is scarce and constrained. Much of Richmond is in the Agricultural Land Reserve (ALR) — provincially protected farmland where non-agricultural development is effectively prohibited. The buildable urban area is concentrated in a central corridor.
- Flood risk. Richmond is almost entirely at or below sea level. The city is protected by dikes, but flood plain regulations affect building design and insurance costs. Some parcels have more onerous requirements than others.
- The city owns land it isn't actively using. Like most municipalities, Richmond holds parcels acquired over decades for purposes that never materialized — road widenings that were re-routed, utility corridors that were consolidated, park land that was never developed. Some of these parcels might be available for community use through lease or sale.
- Zoning is complex. Richmond's Zoning Bylaw 8500 defines dozens of zone codes, each permitting specific uses. A synagogue (classified as a "place of worship" or "assembly" use) is only permitted in certain zones. You cannot build one on a parcel zoned for single-family residential without first obtaining a rezoning — a process that can take 1–3 years and is not guaranteed.
- Transit and walkability matter for a synagogue. Observant Jews do not drive on Shabbat (Saturday, from Friday sundown to Saturday nightfall). The synagogue must be within walking distance of where congregants live. This makes location within the central residential core of Richmond critical — not on cheap industrial land at the edge of town.
### 2.3 What does "center of Richmond" mean?
For this project, "central Richmond" is roughly defined as the area bounded by:

- North: Westminster Highway
- South: Steveston Highway
- East: Knight Street / Highway 91
- West: No. 4 Road (approximately)
- The densest residential and commercial core is along No. 3 Road (the main commercial corridor, served by the Canada Line rapid transit) and the surrounding neighborhoods of City Centre, Brighouse, Thompson, and Broadmoor. This is where the highest density of potential congregants live and where walkability is best.

We will define this area as a bounding box and a walkshed polygon in the dashboard.

### 2.4 Secondary customers
While the synagogue search is the primary use case, the dashboard should also serve:

| Customer Segment | What They Need |
|---|---| | Real estate developers | Filter listings by zoning, lot size, and proximity to transit to find development sites |
| City of Richmond planning staff | Inventory of underutilized city-owned parcels with zoning and assessed value |
| Affordable housing advocates | Map of public land suitable for housing relative to transit and services |
| Real estate brokers | Overlay client criteria against all active listings in one view |
| Community organizations (churches, mosques, cultural centers) | Same suitability analysis as the synagogue use case, with different criteria weights |
| Researchers and journalists | Spatial analysis of land use patterns, vacancy, and ownership |

## 3. Problem Statement
### 3.1 The information is siloed
To answer the question "Where in central Richmond can we build a synagogue?", a person today must manually consult the following disconnected systems:

| System | What It Contains | What It Lacks |
|---|---|---| | RIM (Richmond Interactive Map) — maps.richmond.ca/rim | Zoning, parcels, permits, utilities — one property at a time | No filtering by ownership. No bulk queries. No listing data. |
| BC Assessment — bcassessment.ca | Ownership, assessed value, property classification | No map interface. Single-property lookup only (free tier). No zoning data. |
| MLS portals (Realtor.ca, REW.ca) | Active listings with price, photos, details | No zoning filter. No ownership data. Cannot filter by "assembly use permitted." |
| Richmond GeoHub — richmond-geo-hub-cor.hub.arcgis.com | Raw GIS layers (parcels, zoning, building footprints) as downloadable data | No cross-referencing between layers. Requires GIS expertise. No listings. |
| ParcelMap BC — openmaps.gov.bc.ca | Provincial parcel data including Crown land ownership | Very large dataset. No local context. No assessed values. |

### 3.2 The questions that can't be answered
None of these systems individually can answer:

- What land does the City of Richmond own that has no building on it?
- Of that land, which parcels are zoned to permit a place of worship?
- Which of those parcels are in central Richmond, within walking distance of residential neighborhoods?
- What's currently for sale on the private market that meets the same criteria?
- How large are these parcels, and what are they worth?
- Which options are closest to where Jewish families currently live?
- This dashboard answers all six.

### 3.3 The cost of the status quo
Without this tool, the synagogue planning committee's process looks like this:

1. Someone drives around neighborhoods looking for "For Sale" signs or empty lots
1. They note the address, then go home and look it up on RIM to check the zoning
1. If the zoning doesn't permit assembly use, they discard it
1. If it might work, they look it up on BC Assessment to find the owner and assessed value
1. If it's city-owned, they contact the city to ask about availability — often getting no response for weeks
1. Repeat for every candidate parcel, one at a time
1. This process takes months, misses opportunities (listings sell before they're found), and requires specialized knowledge that most volunteer committee members don't have. The dashboard compresses this into minutes.

## 4. Value Proposition
### 4.1 Core value: Cross-dataset join with a spatial interface
The dashboard does not create new data. It assembles existing public and semi-public data into a single queryable map view and answers questions that no source system can answer individually.

Think of it as a search engine for land, where the search criteria span multiple databases simultaneously.

### 4.2 Value by customer segment
| Customer | Value |
|---|---| | Synagogue committee | Instant list of viable sites ranked by suitability score, replacing months of manual research |
| Developers/investors | Filter listings by zoning + lot size + transit proximity — stop manually checking zoning for every listing |
| City planners | Surface city-owned parcels that are vacant/underutilized, with zoning and value attached |
| Housing advocates | Understand spatial distribution of unused public land relative to housing demand |
| Brokers | Overlay client criteria (e.g., "Assembly-permitted, 800m²+, within 1km of Canada Line") against all active listings |

### 4.3 Market comparables
The paid analogues to this tool are:

| Product | Cost | Coverage | Gap |
|---|---|---|---| | Zoneomics | $99–499/month | US-only | No Canadian data |
| Reonomy | $300–1000+/month | US-only, commercial focus | No Canadian data |
| LandVision (CoreLogic) | Enterprise pricing | North America | Very expensive, not community-accessible |
| Realtor.ca | Free | Canada-wide listings | No zoning, no ownership, no vacancy |
| RIM | Free | Richmond only | No listings, no bulk analysis, no scoring |

There is no existing product that provides this cross-referenced view for Richmond, BC at an accessible price point. This is a genuine gap.

## 5. Use Cases
### 5.1 Primary: Synagogue site search
User story: "As the chair of the synagogue building committee, I want to see every parcel in central Richmond that (a) is either for sale or city-owned and unused, (b) is zoned to allow a place of worship or could reasonably be rezoned, (c) is large enough for a synagogue building with parking, and (d) is within walking distance of where our members live — so that I can present a shortlist to the board with confidence that we haven't missed any options."

Acceptance criteria:

Map shows all candidate parcels, color-coded by type (city-owned vacant, private for-sale, potentially rezonable)
Each parcel shows: address, PID, zone code, lot area (m²), assessed value, owner, MLS listing price (if applicable), suitability score
User can filter by: minimum lot area, zoning category, maximum distance from a point, maximum price
User can click a parcel to see a detail panel with all attributes and links to source systems (BC Assessment, MLS listing, RIM)
Suitability score is computed from weighted criteria (see Section 16)
### 5.2 Secondary: General land intelligence
User story: "As a developer, I want to filter all active Richmond listings to show only those zoned C2 (General Commercial) or RM (Multiple Family Residential) with lot area over 1500m², so I can evaluate development sites."

### 5.3 Tertiary: City-owned land audit
User story: "As a city councillor, I want to see all parcels owned by the City of Richmond that have no building on them and are not classified as parkland, so I can understand the city's surplus land inventory."

## 6. Glossary of Key Terms
A junior engineer or community committee member may not know these terms. Here is every term used in this document that requires definition.

| Term | Definition |
|---|---| | PID | Parcel Identifier — a unique 9-digit number assigned to every titled land parcel in BC by the Land Title and Survey Authority (LTSA). Format: XXX-XXX-XXX. This is the universal join key between land datasets. |
| Parcel | A legally defined piece of land with boundaries registered in the BC land title system. One parcel = one PID. A single building can sit on multiple parcels; a single parcel can contain multiple buildings. |
| Zoning | Municipal bylaw rules that define what can be built on a parcel. Each parcel is assigned a zone code (e.g., "RS1" = single-family residential, "C2" = general commercial). The zone code determines permitted uses, maximum building height, floor area ratio, setbacks, parking requirements, etc. |
| Rezoning | The process of changing a parcel's zone code. Requires a formal application to the city, public hearing, and council vote. Takes 1–3 years. Not guaranteed. Costs $50,000–200,000+ in application fees and consultant costs. |
| ALR | Agricultural Land Reserve — a provincial land use zone covering ~95,000 km² of BC farmland. Development is severely restricted. Large portions of south and east Richmond are in the ALR. Parcels in the ALR are essentially unbuildable for non-agricultural uses. |
| Assembly use | A zoning use category that includes places of worship, community halls, and similar gathering spaces. In Richmond's Zoning Bylaw 8500, this is listed under specific zone codes as a permitted or conditional use. |
| Floor Area Ratio (FAR) | The ratio of a building's total floor area to the lot area. A FAR of 1.0 on a 1000m² lot means you can build 1000m² of floor space. Higher FAR = more building allowed. |
| GIS | Geographic Information System — software and data systems for working with spatial (map) data. Think of it as a database where every record has a location (coordinates or polygon boundary). |
| GeoJSON | A standard file format for encoding geographic features (points, lines, polygons) as JSON. It's how map data is transmitted over web APIs. |
| Spatial join | A database operation that links two datasets based on geographic relationship (e.g., "which zoning polygon contains this parcel's center point?"). Analogous to a SQL JOIN but using geometry instead of a shared key. |
| WFS | Web Feature Service — an OGC standard protocol for requesting geographic features from a server. Returns actual geometry data (unlike WMS which returns images). |
| ArcGIS REST API | Esri's proprietary API for accessing GIS data hosted on ArcGIS servers. Richmond's GeoHub uses this. Returns JSON with geometry and attributes. |
| Turf.js | An open-source JavaScript library for performing spatial operations (distance, intersection, buffering) in the browser without a backend. |
| PostGIS | An extension to the PostgreSQL database that adds support for geographic objects and spatial queries. Industry standard for server-side spatial work. |
| Leaflet | An open-source JavaScript library for interactive maps. Lightweight, well-documented, widely used. |
| Mapbox GL JS | A more powerful (but heavier) JavaScript mapping library by Mapbox. Supports vector tiles, 3D, and smooth zooming. Free tier is generous. |
| Canada Line | The rapid transit (SkyTrain) line running from downtown Vancouver through Richmond to YVR airport. Stations in Richmond: Bridgeport, Aberdeen, Lansdowne, Richmond-Brighouse. This is the transit spine of central Richmond. |
| Shabbat / Sabbath | The Jewish day of rest, from Friday sundown to Saturday nightfall. Observant Jews refrain from driving, using electricity (broadly), and other activities. Walking to synagogue is therefore a religious requirement for this population. |
| Eruv | A symbolic boundary (often made of wire/string on existing poles) that permits carrying objects outdoors on Shabbat. Some communities establish an eruv around the neighborhood. The synagogue should ideally be within any planned eruv boundary. This is a "nice to have" criterion, not a hard requirement. |
| Minyan | A quorum of 10 Jewish adults required for communal prayer. The synagogue must be accessible to at least 10 members on foot for Shabbat services. |
| Kosher | Conforming to Jewish dietary laws. A synagogue kitchen must be designed for kosher food preparation (separate areas for meat and dairy). This affects building design but not site selection. |
| MLS | Multiple Listing Service — the shared database used by licensed real estate agents in Canada to list properties for sale. Operated regionally (in Metro Vancouver, by Greater Vancouver Realtors / GVR). |
| IDX | Internet Data Exchange — the rules governing how MLS data can be displayed on third-party websites. Compliance is required for any public-facing display of MLS listings. |
| CREA | Canadian Real Estate Association — the national body. Operates the Data Distribution Facility (DDF) that provides a standardized listing feed. |
| GVR | Greater Vancouver Realtors — the local real estate board covering Metro Vancouver including Richmond. Controls access to detailed MLS data for this area. |
| Repliers | A Canadian proptech company that provides a REST API for MLS data. Requires board membership or broker sponsorship. |
| CORS | Cross-Origin Resource Sharing — a browser security mechanism that prevents web pages from making requests to a different domain unless that domain explicitly allows it. Some government APIs block CORS, requiring a backend proxy. |

## 7. System Architecture Overview
┌─────────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                                │
│                                                                      │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Map View     │  │  Filter Panel     │  │  Detail Panel        │  │
│  │  (Leaflet or  │  │  (Zone, Size,     │  │  (Parcel info,       │  │
│  │  Mapbox GL)   │  │  Price, Score,    │  │  listing details,    │  │
│  │              │  │  Ownership,       │  │  suitability score,  │  │
│  │              │  │  Walk distance)   │  │  links to sources)   │  │
│  └──────┬───────┘  └────────┬─────────┘  └──────────┬───────────┘  │
│         │                   │                        │               │
│         └───────────────────┼────────────────────────┘               │
│                             │                                        │
│                     ┌───────▼───────┐                                │
│                     │  Turf.js      │  (client-side spatial ops)     │
│                     │  (optional)   │                                │
│                     └───────┬───────┘                                │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │  HTTPS / REST
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND SERVER                                │
│                     (Node.js or Python/FastAPI)                       │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │  API Router   │  │  Data Sync    │  │  Suitability Scoring     │ │
│  │  /parcels     │  │  Workers      │  │  Engine                  │ │
│  │  /listings    │  │  (cron jobs)  │  │  (weighted criteria →    │ │
│  │  /zones       │  │              │  │   score per parcel)      │ │
│  │  /score       │  │              │  │                          │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬────────────────┘ │
│         │                 │                      │                   │
│         └─────────────────┼──────────────────────┘                   │
│                           │                                          │
│                   ┌───────▼────────┐                                 │
│                   │   PostGIS DB   │                                  │
│                   │                │                                  │
│                   │  - parcels     │                                  │
│                   │  - zones       │                                  │
│                   │  - buildings   │                                  │
│                   │  - listings    │                                  │
│                   │  - assessments │                                  │
│                   │  - scores      │                                  │
│                   └───────┬────────┘                                  │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────────────┐
            │               │                       │
            ▼               ▼                       ▼
   ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐
   │ Richmond   │  │ ParcelMap BC │  │ MLS API              │
   │ GeoHub     │  │ (WFS)        │  │ (Repliers / CREA DDF)│
   │ ArcGIS API │  │              │  │                      │
   └────────────┘  └──────────────┘  └──────────────────────┘
   ┌────────────┐  ┌──────────────┐
   │ BC         │  │ Geocoding    │
   │ Assessment │  │ (libpostal / │
   │ (bulk/API) │  │ Geocoder.ca) │
   └────────────┘  └──────────────┘
Key architectural decisions:

PostGIS is the central data warehouse. All source data is ingested into a single PostgreSQL/PostGIS database, where spatial joins are performed server-side. This is dramatically faster and more reliable than doing spatial operations in the browser.

The backend serves pre-joined, pre-scored data. The frontend never talks to external data sources directly. It queries our API, which returns enriched records (parcel + zone + assessment + listing + score) as GeoJSON.

Data sync is batch, not real-time. Parcels and zoning change rarely (weekly updates at most). Listings change daily. BC Assessment data changes annually. Each source has a sync worker on an appropriate schedule.

The frontend is a single-page application with a map as the primary interface and filters/details as supporting panels.

## 8. Data Sources — Complete Reference
### 8.1 Richmond GeoHub — Parcels
| Attribute | Detail |
|---|---| | URL | https://richmond-geo-hub-cor.hub.arcgis.com/datasets/cor::parcels-1 |
| API Endpoint | ArcGIS REST FeatureServer — find by clicking "I want to use this" → "View API resources" → copy the FeatureServer URL |
| Authentication | None required (public layer) |
| Cost | Free |
| Format | JSON (ArcGIS format) — can request GeoJSON with f=geojson parameter |
| Contains | Parcel polygons with: OWNER (registered title owner name), PID (parcel identifier), CIVIC_ADDRESS, LOT_AREA (in m²), polygon geometry |
| Key field | OWNER — filter with OWNER LIKE 'CITY OF RICHMOND%' to isolate municipal parcels |
| Update frequency | Weekly |
| Pagination | Max 1000–2000 records per query. Use resultOffset parameter to paginate. Example: ?where=1=1&resultOffset=0&resultRecordCount=1000&f=geojson |
| Limitations | (1) Owner field is the registered legal title — a park and a vacant lot both show as "City of Richmond." No field indicates current use or vacancy. (2) Some parcels have stale owner data if a recent sale hasn't been registered. (3) Coordinates are in BC Albers (EPSG:3005) or WGS84 (EPSG:4326) depending on request parameters — always specify outSR=4326 for web mapping. |
| Ingestion strategy | Paginate through all records, store in PostGIS with geometry. Re-sync weekly via cron. |

### 8.2 Richmond GeoHub — Zoning Districts
| Attribute | Detail |
|---|---| | URL | https://richmond-geo-hub-cor.hub.arcgis.com/datasets/cor::zoning-districts-1 |
| API Endpoint | Same ArcGIS REST FeatureServer pattern |
| Authentication | None |
| Cost | Free |
| Contains | Zoning polygons with: ZONE_DESIGNATION (e.g., RS1, RS2, RT, RM1, RM2, RM3, RM4, C1, C2, C3, C4, CA, CDT1, CDT2, IB, IL, IG, AG1, AG2, PK, INS, ASY, etc.), ZONE_DESCRIPTION, links to Bylaw 8500 sections |
| Limitations | (1) Zoning polygons don't align perfectly with parcel polygons — they're independently digitized. You need a spatial join: intersect each parcel's centroid with the zoning polygon to determine the parcel's zone. (2) Zone boundaries may lag behind recently passed rezoning bylaws by weeks. (3) Some parcels may intersect multiple zones (split-zoned lots) — handle by assigning the zone that covers the largest area of the parcel. |
| Critical for synagogue use case | Must identify which zone codes permit "assembly" or "place of worship" as a use. This requires reading Bylaw 8500 (see Section 16). |
| Ingestion strategy | Full download, store in PostGIS. Re-sync monthly (zoning changes are infrequent). |

### 8.3 Richmond GeoHub — Building Footprints
| Attribute | Detail |
|---|---| | URL | Search Richmond GeoHub for "building footprints" — available as a public layer |
| Contains | Polygon outlines of every physical building structure in Richmond |
| Why needed | This is one of the best free signals for "vacancy." A parcel with no building footprint intersecting it is likely vacant land. Not perfect (a parking lot has no building) but a strong signal. |
| Ingestion strategy | Full download, store in PostGIS. Spatial join against parcels: SELECT parcels.* FROM parcels LEFT JOIN buildings ON ST_Intersects(parcels.geom, buildings.geom) WHERE buildings.gid IS NULL → returns parcels with no building. |

### 8.4 Richmond GeoHub — Building Permits
| Attribute | Detail |
|---|---| | URL | Search Richmond GeoHub, or inspect RIM network requests (see 8.7) |
| Contains | Permit records with address, permit type (new construction, renovation, demolition), date, status |
| Why needed | Secondary vacancy signal. A parcel with no permit activity in 5+ years is likely inactive. Also useful to identify parcels where demolition has occurred (potential vacant lots). |
| Ingestion strategy | Download, store in PostGIS, join to parcels by address or spatial proximity. |

### 8.5 ParcelMap BC (Provincial Parcel Fabric)
| Attribute | Detail |
|---|---| | URL | https://openmaps.gov.bc.ca/geo/pub/WHSE_CADASTRE.PMBC_PARCEL_POLY_SV/wfs |
| Documentation | BC Data Catalogue: catalogue.data.gov.bc.ca/dataset/parcelmap-bc-parcel-fabric |
| Authentication | None |
| Cost | Free (Open Government Licence — British Columbia) |
| Contains | Every titled parcel in BC: polygon geometry, PID, OWNER_TYPE (Private, Municipal, Crown Provincial, Crown Federal), MUNICIPALITY, PARCEL_STATUS |
| Why use alongside GeoHub | GeoHub only has Richmond's own parcels. ParcelMap BC includes provincial Crown land and federal land within Richmond's boundaries — DFO properties, Transport Canada land near YVR, BC Hydro rights-of-way. Some of these may be suitable or available for community use via lease. |
| How to query | WFS request with CQL filter: MUNICIPALITY='CITY OF RICHMOND' and optionally OWNER_TYPE='Municipal' or OWNER_TYPE='Crown Provincial'. Always include a BBOX to limit data volume. Request outputFormat=application/json for GeoJSON. |
| Limitations | (1) CORS restrictions — the WFS endpoint blocks direct browser-side fetch. You must use a backend proxy or ingest via a server-side script. (2) Very large dataset — always filter by municipality and bounding box. (3) No owner names for private parcels, only owner type. (4) Strata buildings (condos) appear as a single parcel polygon — no unit-level data. |
| Ingestion strategy | Server-side Python script using requests or owslib to fetch all Richmond parcels. Store in PostGIS. Join to GeoHub parcels on PID. Re-sync monthly. |

### 8.6 BC Assessment
| Attribute | Detail |
|---|---| | Public web UI | https://bcassessment.ca — free single-property lookup |
| BC OnLine API | https://www.bconline.gov.bc.ca/ — paid per-transaction API. ~$5–10 per property lookup. Useful for enriching a short list, not for bulk. |
| Bulk data product | "Data Advice" product — annual CSV/XML snapshot with assessed value, property class, owner name, land/improvement value split. Requires a commercial licence from BC Assessment (contact: bcassessment.ca/contact). Cost: varies, typically $1,000–5,000+/year. Academic researchers can access via UBC/SFU Abacus data repository. |
| Key fields | PROPERTY_CLASS_CODE: Class 1 = Residential, Class 2 = Utilities, Class 4 = Major Industry, Class 5 = Light Industry, Class 6 = Business/Commercial, Class 8 = Recreational, Class 9 = Farm. Crucially: a code exists for Exempt properties (government, religious institutions, etc.) — identify these to find comparable sites. |
| | ACTUAL_USE_CODE: More granular than class. Codes like 060 = Vacant Residential, 070 = 2 Acres or More (Res), 200 = Retail, 500 = Vacant Industrial. Code 034 = Church/Synagogue/Mosque. |
| | LAND_VALUE and IMPROVEMENT_VALUE: A parcel where IMPROVEMENT_VALUE is $0 or very low relative to LAND_VALUE is likely vacant or has minimal structures. This is the best vacancy proxy available at scale. |
| | OWNER_NAME: Cross-reference with GeoHub owner field. |
| Limitations | (1) Assessed values reflect July 1 of the prior year — not current market value. But they're the best available proxy for land cost. (2) "Vacant" classification is a tax assessment category, not necessarily an accurate on-the-ground status. (3) Bulk access costs money; the free UI cannot be scraped at scale (and scraping violates TOS). (4) BC Assessment data is considered personal information in some contexts — check the licence terms for any public-facing display. |
| Ingestion strategy | For the MVP, use the web UI to manually look up the top 20–30 candidate parcels identified through other means. For the full product, acquire the bulk data product or use BC OnLine API for targeted enrichment. |

### 8.7 Richmond Interactive Map (RIM)
| Attribute | Detail |
|---|---| | URL | https://maps.richmond.ca/rim |
| Access | Public, browser-only. No documented API. |
| Contains | Everything on GeoHub plus additional layers: utilities (water, sewer, drainage), building permits, heritage sites, environmentally sensitive areas (ESAs), flood plain designations, parks, schools, fire halls. |
| How to use programmatically | RIM is built on ArcGIS. Open it in Chrome, press F12 to open DevTools, go to the Network tab, then enable the layer you want in RIM. Watch for XHR requests to URLs like arcgis.com or richmond.ca/arcgis/rest/services/.... Copy those FeatureServer URLs — they are undocumented but functional APIs. |
| Why this matters | Some layers in RIM are not listed on GeoHub. Utility connections (water/sewer), environmental constraints, and flood plain boundaries are extremely valuable for site suitability scoring but may only be discoverable through RIM's network requests. |
| Ingestion strategy | Use DevTools to discover hidden FeatureServer endpoints. Test each with ?f=json to see the schema. Ingest useful layers into PostGIS. |

### 8.8 MLS Listing Data (via Repliers API or CREA DDF)
Option A: Repliers API
| Attribute | Detail |
|---|---| | URL | https://api.repliers.io |
| Documentation | https://repliers.com/documentation |
| Authentication | API key, requires account |
| Cost | Not publicly listed — historically ~$100–300/month depending on volume |
| Access requirement | Must have GVR (Greater Vancouver Realtors) membership or a licensed broker to sponsor your access. Repliers performs a compliance check per GVR's IDX rules. This can take weeks to months. |
| Contains | Active MLS listings: address, list price, property type, lot size, bedrooms, bathrooms, days on market, MLS#, listing agent, status, and often the zoning code (as entered by the listing agent — not always accurate). Geocoded coordinates (lat/lng). |
| Limitations | (1) Access is gated behind real estate board membership — this is the hardest part of the entire project. (2) Listings include geocoded lat/lng but not PIDs — you must match listings to parcels via address normalization or spatial proximity. (3) No sold/historical data without additional agreement. (4) IDX compliance rules restrict how you can display data publicly (e.g., must show listing broker attribution, can't modify listing data). |

Option B: CREA DDF Web API
| Attribute | Detail |
|---|---| | URL | https://ddf.realtor.ca/ |
| Access | Free for CREA members (all licensed REALTORS® in Canada). Must register for API credentials. |
| Contains | Standardized listing feed across all Canadian boards. OData protocol (XML-based, can be JSON). |
| Limitations | Less field depth than direct GVR access. Coverage varies by board. |

Option C: Third-party commercial APIs
| Provider | Notes |
|---|---| | Realtyna (MLS Router API) | Aggregates MLS data, REST API, JSON. Must negotiate access. |
| Bridge API | Similar commercial aggregator. Modern REST API. |
| Zillow/Redfin | US-focused, minimal Canadian data. Not useful here. |

Recommended approach
Partner with a licensed REALTOR® or brokerage in Richmond who is willing to sponsor API access. Many brokerages are interested in data tools and would benefit from the dashboard themselves. This relationship also provides domain expertise on the local market.

### 8.9 Geocoding Services
To match MLS listings (which have addresses) to parcels (which have PIDs and polygons), you need to geocode addresses to coordinates.

| Service | Cost | Notes |
|---|---|---| | Geocoder.ca | Free for limited use, paid for bulk | Canadian-specific, good address normalization |
| libpostal | Free, open source | Address parsing/normalization library — install locally. Does not geocode but normalizes address formats for matching. |
| Google Maps Geocoding API | $5/1000 requests | Very accurate, well-documented |
| Mapbox Geocoding | Free tier: 100,000 requests/month | Good accuracy, modern API |
| BC Address Geocoder | Free | geocoder.api.gov.bc.ca — provincial service, good for BC addresses specifically |

Recommended: Use the BC Address Geocoder (free, BC-specific, government-maintained) as primary, with Google Maps as fallback for addresses it can't resolve.

### 8.10 Basemap Tiles
The background map that sits behind your data layers.

| Provider | Cost | Style | Notes |
|---|---|---|---| | OpenStreetMap (via Leaflet) | Free | Street map | Default, adequate |
| Mapbox | Free tier: 200,000 tile loads/month | Multiple styles including satellite | Requires API key |
| Esri World Imagery | Free for non-commercial use | Satellite | Great for visual ground-truthing (can see if a parcel is actually vacant) |
| CartoDB/CARTO | Free tier available | Dark Matter, Voyager | Clean styles good for data overlays |

Recommended: Use Mapbox GL JS with the Satellite + Streets hybrid style. It's free for this scale of use, looks professional, and lets users see buildings and vacant land in aerial imagery.

### 8.11 Additional Useful Data Sources
| Source | URL/Access | Contains | Use in Dashboard |
|---|---|---|---| | TransLink GTFS | translink.ca/about-us/doing-business-with-translink/app-developer-resources (free) | Transit stops, routes, schedules | Calculate walking time to nearest Canada Line station. Critical for Shabbat walkability scoring. |
| BC Flood Hazard Maps | governmentofbc.maps.arcgis.com or Richmond's own flood plain layer via RIM | Flood hazard areas, dike locations | Flag parcels in high-risk flood zones. Affects insurance and building cost. |
| Agricultural Land Reserve (ALR) Boundary | catalogue.data.gov.bc.ca/dataset/alr-boundary (free WFS) | ALR polygon | Hard filter: exclude any parcel within ALR. You cannot build a synagogue on ALR land. |
| Richmond Zoning Bylaw 8500 | richmond.ca/cityhall/bylaws/zoningbylaw8500 | Full text of permitted uses per zone code | Must read this to build the zone-use permission lookup table (which zones allow "assembly" use). |
| Statistics Canada Census Data | www12.statcan.gc.ca | Population, demographics by census tract/dissemination area | Overlay Jewish population density (if available at fine geographic level — may only be available at CMA level) |
| Google Maps Static API / Street View | Paid (low cost) | Satellite imagery, street-level photos | Embed thumbnail images of candidate parcels in the detail panel for visual assessment |
| Walk Score API | walkscore.com/professional/api.php (free tier: 5000/day) | Walkability score for an address | Secondary scoring input |

## 9. Data Model & Join Strategy
### 9.1 The core challenge
These datasets don't share a common key by default. Here is how they connect:

GeoHub Parcels  ──── PID ─────────► BC Assessment
GeoHub Parcels  ──── PID ─────────► ParcelMap BC
GeoHub Parcels  ── SPATIAL JOIN ──► Zoning Districts (polygon intersect)
GeoHub Parcels  ── SPATIAL JOIN ──► Building Footprints (polygon intersect)
GeoHub Parcels  ── SPATIAL JOIN ──► ALR Boundary (polygon intersect)
GeoHub Parcels  ── SPATIAL JOIN ──► Flood Hazard Areas (polygon intersect)
MLS Listings    ── ADDRESS MATCH ─► Geocode ──► SPATIAL JOIN ──► Parcels
TransLink Stops ── SPATIAL DIST. ─► Parcels (nearest-neighbor distance)
PID is the cleanest join key. It's available in GeoHub Parcels, ParcelMap BC, and BC Assessment.

Address matching between MLS and parcels requires normalization. Addresses in MLS look like "#120 - 8100 No. 3 Road" while in GeoHub they look like "8100 NO 3 RD". Steps:

Parse with libpostal to extract street number, street name, unit number
Normalize (remove punctuation, standardize abbreviations: "Road" → "RD", "Street" → "ST")
Geocode with BC Address Geocoder to get lat/lng
Spatial join: find which parcel polygon contains the geocoded point
### 9.2 Database schema (PostGIS)
```sql
-- Core tables

CREATE TABLE parcels (
    id SERIAL PRIMARY KEY,
    pid VARCHAR(12) UNIQUE,          -- PID: '000-000-000' format
    civic_address TEXT,
    owner_name TEXT,
    lot_area_sqm NUMERIC,
    geom GEOMETRY(MultiPolygon, 4326),
    source VARCHAR(20),              -- 'geohub' or 'parcelmap_bc'
    owner_type VARCHAR(20),          -- 'Municipal', 'Private', 'Crown Provincial', 'Crown Federal'
    last_synced TIMESTAMP
);

CREATE INDEX idx_parcels_geom ON parcels USING GIST (geom);
CREATE INDEX idx_parcels_pid ON parcels (pid);
CREATE INDEX idx_parcels_owner ON parcels (owner_type);

CREATE TABLE zoning_districts (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(20),           -- 'RS1', 'C2', 'RM3', etc.
    zone_description TEXT,
    permits_assembly BOOLEAN,        -- Manually populated from Bylaw 8500 review
    max_far NUMERIC,
    max_height_m NUMERIC,
    geom GEOMETRY(MultiPolygon, 4326),
    last_synced TIMESTAMP
);

CREATE INDEX idx_zones_geom ON zoning_districts USING GIST (geom);

CREATE TABLE building_footprints (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326),
    last_synced TIMESTAMP
);

CREATE INDEX idx_buildings_geom ON building_footprints USING GIST (geom);

CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    mls_number VARCHAR(20) UNIQUE,
    address TEXT,
    normalized_address TEXT,
    list_price NUMERIC,
    property_type VARCHAR(50),
    lot_size_sqm NUMERIC,
    bedrooms INT,
    bathrooms INT,
    days_on_market INT,
    listing_status VARCHAR(20),      -- 'Active', 'Pending', 'Sold'
    listing_agent TEXT,
    listing_brokerage TEXT,
    mls_zoning TEXT,                 -- Zoning as listed in MLS (unreliable)
    lat NUMERIC,
    lng NUMERIC,
    geom GEOMETRY(Point, 4326),
    matched_parcel_pid VARCHAR(12),  -- Populated by address matching / spatial join
    last_synced TIMESTAMP
);

CREATE INDEX idx_listings_geom ON listings USING GIST (geom);
CREATE INDEX idx_listings_parcel ON listings (matched_parcel_pid);

CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    pid VARCHAR(12) UNIQUE,
    roll_number VARCHAR(20),
    owner_name TEXT,
    property_class_code INT,         -- 1=Res, 5=Light Ind, 6=Bus/Comm, etc.
    actual_use_code VARCHAR(10),
    land_value NUMERIC,
    improvement_value NUMERIC,
    total_value NUMERIC,
    is_exempt BOOLEAN,
    exempt_type TEXT,                 -- 'Municipal', 'Religious', 'School', etc.
    assessment_year INT,
    last_synced TIMESTAMP
);

CREATE INDEX idx_assessments_pid ON assessments (pid);

CREATE TABLE alr_boundary (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX idx_alr_geom ON alr_boundary USING GIST (geom);

CREATE TABLE flood_hazard (
    id SERIAL PRIMARY KEY,
    hazard_level VARCHAR(20),
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX idx_flood_geom ON flood_hazard USING GIST (geom);

CREATE TABLE transit_stops (
    id SERIAL PRIMARY KEY,
    stop_name TEXT,
    route_type INT,                  -- 1 = Rail (Canada Line), 3 = Bus
    lat NUMERIC,
    lng NUMERIC,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX idx_transit_geom ON transit_stops USING GIST (geom);

-- Materialized view: enriched parcels (the core queryable entity)

CREATE MATERIALIZED VIEW enriched_parcels AS
SELECT
    p.id,
    p.pid,
    p.civic_address,
    p.owner_name,
    p.lot_area_sqm,
    p.owner_type,
    p.geom,

    -- Zoning (spatial join)
    z.zone_code,
    z.zone_description,
    z.permits_assembly,
    z.max_far,

    -- Assessment (PID join)
    a.property_class_code,
    a.actual_use_code,
    a.land_value,
    a.improvement_value,
    a.total_value,
    a.is_exempt,

    -- Vacancy signals
    CASE WHEN bf.id IS NULL THEN TRUE ELSE FALSE END AS no_building,
    CASE WHEN a.improvement_value IS NOT NULL AND a.improvement_value < (a.land_value * 0.1)
         THEN TRUE ELSE FALSE END AS low_improvement_ratio,
    CASE WHEN a.actual_use_code IN ('060','070','500','501') -- vacant use codes
         THEN TRUE ELSE FALSE END AS bca_vacant,

    -- ALR check
    CASE WHEN alr.id IS NOT NULL THEN TRUE ELSE FALSE END AS in_alr,

    -- Flood hazard
    fh.hazard_level AS flood_hazard_level,

    -- Transit proximity
    (SELECT MIN(ST_Distance(p.geom::geography, ts.geom::geography))
     FROM transit_stops ts WHERE ts.route_type = 1) AS dist_to_canada_line_m,

    (SELECT MIN(ST_Distance(p.geom::geography, ts.geom::geography))
     FROM transit_stops ts) AS dist_to_any_transit_m,

    -- Active listing (if any)
    l.mls_number,
    l.list_price,
    l.days_on_market,
    l.listing_status

FROM parcels p

LEFT JOIN LATERAL (
    SELECT z2.zone_code, z2.zone_description, z2.permits_assembly, z2.max_far
    FROM zoning_districts z2
    WHERE ST_Intersects(ST_Centroid(p.geom), z2.geom)
    LIMIT 1
) z ON TRUE

LEFT JOIN assessments a ON p.pid = a.pid

LEFT JOIN building_footprints bf ON ST_Intersects(p.geom, bf.geom)

LEFT JOIN alr_boundary alr ON ST_Intersects(ST_Centroid(p.geom), alr.geom)

LEFT JOIN flood_hazard fh ON ST_Intersects(ST_Centroid(p.geom), fh.geom)

LEFT JOIN listings l ON l.matched_parcel_pid = p.pid AND l.listing_status = 'Active';

CREATE INDEX idx_enriched_geom ON enriched_parcels USING GIST (geom);
### 9.3 The enriched parcel record
After all joins, each parcel in the system has these attributes:

| Field | Source | Type |
|---|---|---| | PID | GeoHub / PMBC | String |
| Address | GeoHub | String |
| Owner | GeoHub + BCA | String |
| Owner Type | PMBC | Enum |
| Lot Area (m²) | GeoHub | Number |
| Polygon Geometry | GeoHub | Geometry |
| Zone Code | Zoning layer (spatial join) | String |
| Assembly Permitted? | Bylaw 8500 lookup table | Boolean |
| Property Class | BC Assessment | Integer |
| Actual Use Code | BC Assessment | String |
| Land Value | BC Assessment | Number |
| Improvement Value | BC Assessment | Number |
| Has Building? | Building footprints (spatial join) | Boolean |
| In ALR? | ALR boundary (spatial join) | Boolean |
| Flood Hazard Level | Flood layer (spatial join) | String |
| Distance to Canada Line (m) | Transit stops (spatial calc) | Number |
| MLS Number | Listings (address match) | String |
| List Price | Listings | Number |
| Days on Market | Listings | Number |
| Suitability Score | Computed (see Section 16) | 0–100 |

## 10. Technical Roadmap — Phased Implementation
The project is divided into five phases. Each phase produces a working, demonstrable artifact. This allows the synagogue committee to start seeing results early while the full system is being built.

Phase 1: Foundation — Static Data Pipeline
Duration: 2–3 weeks Goal: Ingest all free municipal and provincial data into a PostGIS database and produce the first cross-referenced dataset of city-owned, potentially vacant parcels in central Richmond. Deliverable: A static HTML map (Leaflet) showing city-owned parcels color-coded by vacancy signal, with popup details.

Step-by-step tasks:
### 1.1 Set up development environment

Install PostgreSQL 15+ with PostGIS 3.3+ extension
Install Python 3.11+ with packages: requests, geopandas, sqlalchemy, psycopg2, shapely
Install Node.js 18+ (for the frontend later)
Install QGIS (free desktop GIS tool — useful for visual data inspection)
Set up a Git repository
### 1.2 Create PostGIS database

createdb richmond_land
psql richmond_land -c "CREATE EXTENSION postgis;"
Execute the schema SQL from Section 9.2.

### 1.3 Ingest Richmond GeoHub — Parcels Write a Python script (ingest_parcels.py) that:

Constructs the ArcGIS REST API query URL
Paginates through all Richmond parcels (expect ~40,000–60,000 records)
Requests f=geojson&outSR=4326 for each page
Inserts into the parcels table using geopandas.to_postgis() or raw SQL with ST_GeomFromGeoJSON()
Classifies owner_type based on OWNER field:
OWNER LIKE 'CITY OF RICHMOND%' → 'Municipal'
OWNER LIKE '%PROVINCE%' OR OWNER LIKE '%BC%' → 'Crown Provincial'
Everything else → 'Private'
import requests
import geopandas as gpd
from sqlalchemy import create_engine

BASE_URL = "https://<featureserver_url>/query"
engine = create_engine("postgresql://user:pass@localhost/richmond_land")

offset = 0
batch_size = 1000
all_features = []

while True:
    params = {
        "where": "1=1",
        "outFields": "*",
        "outSR": "4326",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": batch_size
    }
    resp = requests.get(BASE_URL, params=params)
    data = resp.json()
    features = data.get("features", [])
    if not features:
        break
    all_features.extend(features)
    offset += batch_size

gdf = gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
gdf.to_postgis("parcels", engine, if_exists="replace", index=False)
### 1.4 Ingest Richmond GeoHub — Zoning Districts Same pattern as 1.3. Store in zoning_districts table.

### 1.5 Ingest Richmond GeoHub — Building Footprints Same pattern. Store in building_footprints table.

### 1.6 Ingest ALR Boundary Fetch from BC Data Catalogue WFS:

https://openmaps.gov.bc.ca/geo/pub/WHSE_LEGAL_ADMIN_BOUNDARIES.OATS_ALR_POLYS/wfs?
  service=WFS&version=2.0.0&request=GetFeature&
  typeName=WHSE_LEGAL_ADMIN_BOUNDARIES.OATS_ALR_POLYS&
  CQL_FILTER=INTERSECTS(SHAPE, SRID=4326;POLYGON((...richmond bbox...)))&
  outputFormat=application/json
Store in alr_boundary table.

### 1.7 Ingest ParcelMap BC Fetch via WFS filtered by MUNICIPALITY='CITY OF RICHMOND'. Store in a staging table, then merge with GeoHub parcels by PID (GeoHub is more detailed for Richmond-specific data; ParcelMap BC fills in Crown/Federal parcels that GeoHub doesn't have).

### 1.8 Ingest TransLink GTFS Download GTFS feed from TransLink. Parse stops.txt to extract stop locations. Filter to Richmond stops. Insert into transit_stops table.

### 1.9 Build zone-use permission lookup table This is a manual research task. Open Richmond Zoning Bylaw 8500 and for each zone code, determine:

Is "assembly" or "place of worship" or "community/institutional" a permitted use?
Is it a conditional use (requires special approval)?
Is it prohibited?
Store as a lookup table:

CREATE TABLE zone_use_permissions (
    zone_code VARCHAR(20) PRIMARY KEY,
    assembly_permitted BOOLEAN,       -- TRUE if outright permitted
    assembly_conditional BOOLEAN,     -- TRUE if allowed with conditions
    assembly_prohibited BOOLEAN,      -- TRUE if not allowed at all
    notes TEXT
);

-- Examples (YOU MUST VERIFY THESE AGAINST BYLAW 8500):
INSERT INTO zone_use_permissions VALUES
('INS', TRUE, FALSE, FALSE, 'Institutional zone - assembly outright permitted'),
('ASY', TRUE, FALSE, FALSE, 'Assembly zone - explicitly for this use'),
('C1', FALSE, TRUE, FALSE, 'Neighbourhood Commercial - may allow with conditions'),
('C2', FALSE, TRUE, FALSE, 'General Commercial - may allow with conditions'),
('RM1', FALSE, FALSE, TRUE, 'Multi-family residential - no assembly'),
('RS1', FALSE, FALSE, TRUE, 'Single-family - no assembly'),
('AG1', FALSE, FALSE, TRUE, 'Agricultural - no assembly, also ALR'),
('PK', FALSE, FALSE, TRUE, 'Park - no assembly (city park land)');
-- ... continue for all zone codes
Update the zoning_districts table with permits_assembly based on this lookup.

### 1.10 Run spatial joins and create enriched_parcels view Execute the materialized view creation from Section 9.2. This produces the core queryable dataset.

### 1.11 Generate initial candidate list

-- All city-owned parcels in central Richmond with no building and assembly-permitted zoning
SELECT pid, civic_address, lot_area_sqm, zone_code, owner_name,
       dist_to_canada_line_m
FROM enriched_parcels
WHERE owner_type = 'Municipal'
  AND no_building = TRUE
  AND in_alr = FALSE
  AND permits_assembly = TRUE
  AND ST_Within(geom, ST_MakeEnvelope(-123.17, 49.15, -123.10, 49.19, 4326))  -- central Richmond bbox
ORDER BY lot_area_sqm DESC;
### 1.12 Create static Leaflet map Create a simple index.html with Leaflet that:

Loads a Mapbox satellite basemap
Overlays all enriched parcels as GeoJSON polygons
Colors them: green = city-owned vacant, blue = city-owned with building, orange = private for-sale (Phase 3), grey = other
Popup on click shows all attributes
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
    <style>
        #map { height: 100vh; width: 100%; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([49.1666, -123.1336], 13);
        L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token=YOUR_TOKEN', {
            maxZoom: 19,
            attribution: '© Mapbox © OpenStreetMap'
        }).addTo(map);

        fetch('enriched_parcels.geojson')
            .then(r => r.json())
            .then(data => {
                L.geoJSON(data, {
                    style: feature => ({
                        color: feature.properties.owner_type === 'Municipal' && feature.properties.no_building
                            ? '#22c55e' : '#6b7280',
                        weight: 1,
                        fillOpacity: 0.4
                    }),
                    onEachFeature: (feature, layer) => {
                        const p = feature.properties;
                        layer.bindPopup(`
                            <b>${p.civic_address || 'No address'}</b><br>
                            PID: ${p.pid}<br>
                            Owner: ${p.owner_name}<br>
                            Zone: ${p.zone_code}<br>
                            Area: ${p.lot_area_sqm} m²<br>
                            Assembly: ${p.permits_assembly ? '✅ Permitted' : '❌ Not permitted'}<br>
                            Building: ${p.no_building ? '❌ Vacant' : '✅ Has building'}<br>
                            ALR: ${p.in_alr ? '⚠️ In ALR' : '✅ Not ALR'}<br>
                            Canada Line: ${Math.round(p.dist_to_canada_line_m)}m
                        `);
                    }
                }).addTo(map);
            });
    </script>
</body>
</html>
Phase 1 output: A functioning map with all city-owned parcels in Richmond, showing vacancy signals, zoning, ALR status, and transit proximity. The synagogue committee can already start looking at this and identifying interesting sites.

Phase 2: Spatial Engine & Core Dashboard
Duration: 3–4 weeks Goal: Build a proper backend API and interactive frontend with filtering, search, and a detail panel. Deliverable: Deployed web application with server-side API and client-side map interface.

Step-by-step tasks:
### 2.1 Set up backend (Node.js/Express or Python/FastAPI)

Recommended: Python + FastAPI (because you're already using Python for data ingestion, and PostGIS queries are easier to write in Python with asyncpg or psycopg2).

backend/
├── main.py              # FastAPI app
├── routers/
│   ├── parcels.py       # /api/parcels endpoint
│   ├── listings.py      # /api/listings endpoint (Phase 3)
│   ├── zones.py         # /api/zones endpoint
│   └── score.py         # /api/score endpoint (Phase 4)
├── db.py                # Database connection pool
├── models.py            # Pydantic models for API responses
├── sync/
│   ├── sync_parcels.py  # Data ingestion scripts (from Phase 1)
│   ├── sync_zones.py
│   ├── sync_buildings.py
│   ├── sync_listings.py # (Phase 3)
│   └── sync_assessment.py
├── requirements.txt
└── Dockerfile
### 2.2 Implement API endpoints

# backend/routers/parcels.py

from fastapi import APIRouter, Query
from typing import Optional
import json
from db import get_db

router = APIRouter()

@router.get("/api/parcels")
async def get_parcels(
    bbox: Optional[str] = Query(None, description="minLng,minLat,maxLng,maxLat"),
    owner_type: Optional[str] = Query(None, description="Municipal, Private, Crown Provincial"),
    min_area: Optional[float] = Query(None, description="Minimum lot area in m²"),
    max_area: Optional[float] = Query(None, description="Maximum lot area in m²"),
    assembly_permitted: Optional[bool] = Query(None),
    vacant_only: Optional[bool] = Query(None),
    exclude_alr: Optional[bool] = Query(True),
    zone_code: Optional[str] = Query(None, description="Comma-separated zone codes"),
    max_price: Optional[float] = Query(None),
    min_score: Optional[float] = Query(None),
    limit: int = Query(500, le=2000),
    offset: int = Query(0)
):
    conditions = ["1=1"]
    params = {}

    if bbox:
        parts = [float(x) for x in bbox.split(",")]
        conditions.append(
            "ST_Intersects(geom, ST_MakeEnvelope(%(minlng)s, %(minlat)s, %(maxlng)s, %(maxlat)s, 4326))"
        )
        params.update({"minlng": parts[0], "minlat": parts[1], "maxlng": parts[2], "maxlat": parts[3]})

    if owner_type:
        conditions.append("owner_type = %(owner_type)s")
        params["owner_type"] = owner_type

    if min_area:
        conditions.append("lot_area_sqm >= %(min_area)s")
        params["min_area"] = min_area

    if max_area:
        conditions.append("lot_area_sqm <= %(max_area)s")
        params["max_area"] = max_area

    if assembly_permitted:
        conditions.append("permits_assembly = TRUE")

    if vacant_only:
        conditions.append("(no_building = TRUE OR bca_vacant = TRUE OR low_improvement_ratio = TRUE)")

    if exclude_alr:
        conditions.append("in_alr = FALSE")

    if zone_code:
        codes = [c.strip() for c in zone_code.split(",")]
        conditions.append("zone_code = ANY(%(zone_codes)s)")
        params["zone_codes"] = codes

    if max_price:
        conditions.append("(list_price IS NULL OR list_price <= %(max_price)s)")
        params["max_price"] = max_price

    where = " AND ".join(conditions)

    query = f"""
        SELECT pid, civic_address, owner_name, owner_type, lot_area_sqm,
               zone_code, zone_description, permits_assembly,
               property_class_code, actual_use_code,
               land_value, improvement_value, total_value,
               no_building, low_improvement_ratio, bca_vacant,
               in_alr, flood_hazard_level,
               dist_to_canada_line_m, dist_to_any_transit_m,
               mls_number, list_price, days_on_market,
               ST_AsGeoJSON(geom) as geometry
        FROM enriched_parcels
        WHERE {where}
        ORDER BY lot_area_sqm DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    params.update({"limit": limit, "offset": offset})

    db = await get_db()
    rows = await db.fetch(query, params)

    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": json.loads(row["geometry"]),
            "properties": {k: v for k, v in dict(row).items() if k != "geometry"}
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
### 2.3 Build frontend application

Technology: React + Mapbox GL JS (or Leaflet — see Section 17 for comparison).

frontend/
├── src/
│   ├── App.jsx
│   ├── components/
│   │   ├── Map.jsx           # Mapbox GL JS map component
│   │   ├── FilterPanel.jsx   # Left sidebar with all filters
│   │   ├── DetailPanel.jsx   # Right panel showing selected parcel details
│   │   ├── ParcelPopup.jsx   # Map popup on hover/click
│   │   ├── Legend.jsx         # Color legend
│   │   └── ScoreGauge.jsx    # Visual suitability score display
│   ├── hooks/
│   │   ├── useParcels.js     # React Query hook for API calls
│   │   └── useFilters.js     # Filter state management
│   ├── utils/
│   │   ├── colors.js         # Color scales for parcel rendering
│   │   └── scoring.js        # Client-side score display logic
│   └── index.js
├── public/
│   └── index.html
├── package.json
└── vite.config.js
### 2.4 Filter panel implementation

The filter panel should include:

| Filter | Input Type | Default |
|---|---|---| | Ownership | Checkbox group: Municipal, Private, Crown Provincial, Crown Federal | All checked |
| Zoning | Multi-select dropdown of all zone codes | All |
| Assembly Permitted | Toggle: Yes / Any | Any |
| Minimum Lot Area | Slider or number input (m²) | 0 |
| Maximum List Price | Slider or number input ($) | No limit |
| Vacant Only | Toggle | Off |
| Exclude ALR | Toggle | On |
| Max Distance to Canada Line | Slider (meters) | No limit |
| Central Richmond Only | Toggle (applies predefined bounding box) | On |
| Synagogue Mode | Toggle — activates the suitability scoring overlay (Phase 4) | Off |

### 2.5 Detail panel implementation

When a user clicks a parcel on the map, the right panel shows:

Parcel overview: Address, PID, lot area, owner, zone code
Zoning analysis: Zone description, assembly permission status, max FAR, max height
Valuation: Assessed land value, improvement value, total value, assessment year
Vacancy signals: Building footprint check, improvement ratio, BCA classification
Location: Distance to Canada Line, distance to nearest bus stop, neighborhood name
Listing info (if applicable): MLS#, list price, days on market, agent, link to full listing
Suitability score (Phase 4): Score breakdown by criterion
External links: "View on BC Assessment" link, "View on RIM" link, "View on Google Maps" link, "View Street View" link
Satellite thumbnail: Embedded aerial image of the parcel (Google Maps Static API or Mapbox)
### 2.6 Map rendering

// Simplified Mapbox GL JS rendering
map.addSource('parcels', {
    type: 'geojson',
    data: geojsonData
});

map.addLayer({
    id: 'parcels-fill',
    type: 'fill',
    source: 'parcels',
    paint: {
        'fill-color': [
            'case',
            ['all',
                ['==', ['get', 'owner_type'], 'Municipal'],
                ['==', ['get', 'no_building'], true]
            ], '#22c55e',  // Green: city-owned vacant
            ['!=', ['get', 'mls_number'], null], '#f97316',  // Orange: for sale
            ['==', ['get', 'owner_type'], 'Municipal'], '#3b82f6',  // Blue: city-owned with building
            '#d1d5db'  // Grey: other
        ],
        'fill-opacity': 0.5
    }
});

map.addLayer({
    id: 'parcels-outline',
    type: 'line',
    source: 'parcels',
    paint: {
        'line-color': '#1f2937',
        'line-width': 0.5
    }
});
### 2.7 Deploy

Backend: Docker container → any cloud provider (Railway, Render, DigitalOcean App Platform, AWS ECS)
Database: Managed PostgreSQL with PostGIS (Supabase free tier, or Neon, or DigitalOcean managed DB)
Frontend: Static build → Vercel or Netlify (free tier)
Domain: Something like richmondland.ca or richmond-property.tools
Phase 2 output: A fully interactive web dashboard where users can filter and explore all Richmond parcels by zoning, ownership, vacancy, and location. No listing data yet.

Phase 3: Live Market Data Integration
Duration: 2–6 weeks (depending on MLS API access timeline) Goal: Add active real estate listings to the dashboard, matched to parcels and zones. Deliverable: Orange dots/polygons on the map for every active listing, with listing details in the detail panel.

Step-by-step tasks:
### 3.1 Secure MLS API access

This is the critical path item and should be started in Phase 1, because it takes the longest and is outside your direct control.

Option A (recommended): Partner with a REALTOR®

Identify a licensed real estate agent in Richmond who is interested in this tool. They benefit directly — it's a prospecting tool for them.
The agent registers for Repliers API access (repliers.com) and sponsors your developer access
Alternative: The agent registers for CREA DDF access (ddf.realtor.ca)
Timeline: 2–8 weeks for compliance review
Option B: Build without live MLS data initially

Use publicly available listing data from realtor.ca (view-only, no API — you'd manually compile a CSV of relevant listings)
Or: Scrape rew.ca or realtor.ca (violates TOS — not recommended for production, acceptable for a one-time proof of concept)
Use this as a placeholder until Option A is secured
### 3.2 Build listing sync worker

# sync/sync_listings.py

import requests
from db import get_db

REPLIERS_API_KEY = "your_key"
REPLIERS_BASE = "https://api.repliers.io"

async def sync_listings():
    """Fetch all active Richmond listings and store in database."""
    db = await get_db()

    # Repliers API query for Richmond active listings
    params = {
        "city": "Richmond",
        "province": "BC",
        "status": "Active",
        "type": "Land,Commercial,Residential",  # all types
        "limit": 100,
        "offset": 0
    }
    headers = {"Authorization": f"Bearer {REPLIERS_API_KEY}"}

    all_listings = []
    while True:
        resp = requests.get(f"{REPLIERS_BASE}/listings", params=params, headers=headers)
        data = resp.json()
        listings = data.get("listings", [])
        if not listings:
            break
        all_listings.extend(listings)
        params["offset"] += params["limit"]

    for listing in all_listings:
        # Geocode address to lat/lng if not provided
        lat = listing.get("latitude")
        lng = listing.get("longitude")
        if not lat or not lng:
            lat, lng = geocode_address(listing["address"])

        # Match to parcel via spatial join
        matched_pid = await db.fetchval("""
            SELECT pid FROM parcels
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint($1, $2), 4326))
            LIMIT 1
        """, lng, lat)

        await db.execute("""
            INSERT INTO listings (mls_number, address, list_price, property_type,
                                  lot_size_sqm, lat, lng, geom, matched_parcel_pid,
                                  days_on_market, listing_status, last_synced)
            VALUES ($1, $2, $3, $4, $5, $6, $7,
                    ST_SetSRID(ST_MakePoint($7, $6), 4326), $8, $9, $10, NOW())
            ON CONFLICT (mls_number) DO UPDATE SET
                list_price = EXCLUDED.list_price,
                days_on_market = EXCLUDED.days_on_market,
                listing_status = EXCLUDED.listing_status,
                last_synced = NOW()
        """, listing["mls_number"], listing["address"], listing.get("price"),
             listing.get("type"), listing.get("lot_size"),
             lat, lng, matched_pid,
             listing.get("days_on_market"), "Active")
### 3.3 Schedule sync Run listing sync daily (or more frequently) via cron job or a task scheduler like APScheduler (Python) or node-cron (Node.js).

### 3.4 Refresh enriched_parcels materialized view After each listing sync:

REFRESH MATERIALIZED VIEW CONCURRENTLY enriched_parcels;
### 3.5 Update frontend

Add orange fill color for parcels with active listings
Show listing details in the detail panel
Add price filter to the filter panel
Ensure IDX compliance: display listing broker attribution, don't modify listing text, include required disclaimers
### 3.6 Address matching quality assurance MLS addresses won't always match parcels cleanly. Implement a multi-step matching strategy:

Spatial match (best): If listing has lat/lng, find the containing parcel polygon.
Geocode + spatial: If no lat/lng, geocode the address, then spatial match.
Normalized address match: Normalize both listing address and parcel address using libpostal, then exact match.
Fuzzy match (fallback): Use Levenshtein distance or similar fuzzy matching on normalized addresses.
Manual review queue: For unmatched listings, flag for manual matching via the admin interface.
Phase 3 output: The dashboard now shows both public land opportunities and private market listings, all cross-referenced with zoning data.

Phase 4: Synagogue Site Suitability Scoring
Duration: 2 weeks Goal: Implement a weighted scoring algorithm specific to the synagogue site search, and display scores visually on the map. Deliverable: A "Synagogue Mode" toggle that color-codes parcels by suitability score and displays a ranked list of top candidates.

Step-by-step tasks:
### 4.1 Define scoring criteria

See Section 16 for the full deep dive. Summary of criteria and weights:

| Criterion | Weight | Scoring Logic |
|---|---|---| | Zoning: Assembly Permitted | 25 points | Outright permitted = 25, Conditional = 15, Prohibited but rezonable = 5, Prohibited in ALR = 0 |
| Lot Size | 20 points | ≥2000m² = 20, 1500–2000 = 15, 1000–1500 = 10, 800–1000 = 5, <800 = 0 |
| Walkability (distance to residential core) | 20 points | Within 800m of defined residential centroid = 20, 800–1500m = 15, 1500–2500m = 8, >2500m = 0 |
| Availability | 15 points | City-owned vacant = 15, For sale on MLS = 12, City-owned with building = 8, Private not for sale = 0 |
| Cost Feasibility | 10 points | Assessed value < $2M = 10, $2–5M = 7, $5–10M = 4, >$10M = 1 |
| Transit Proximity | 5 points | <500m to Canada Line = 5, 500–1000m = 3, >1000m = 1 |
| Flood Risk | 5 points | No flood hazard = 5, Low = 3, Moderate/High = 1 |

Total: 100 points

### 4.2 Implement scoring in PostGIS

CREATE OR REPLACE FUNCTION synagogue_score(
    p_permits_assembly BOOLEAN,
    p_assembly_conditional BOOLEAN,
    p_in_alr BOOLEAN,
    p_lot_area_sqm NUMERIC,
    p_dist_to_residential_core_m NUMERIC,
    p_owner_type TEXT,
    p_no_building BOOLEAN,
    p_mls_number TEXT,
    p_total_value NUMERIC,
    p_dist_to_canada_line_m NUMERIC,
    p_flood_hazard_level TEXT
) RETURNS JSONB AS $$
DECLARE
    score_zoning INT;
    score_lot INT;
    score_walk INT;
    score_avail INT;
    score_cost INT;
    score_transit INT;
    score_flood INT;
    total INT;
BEGIN
    -- Zoning (25 points)
    IF p_in_alr THEN score_zoning := 0;
    ELSIF p_permits_assembly THEN score_zoning := 25;
    ELSIF p_assembly_conditional THEN score_zoning := 15;
    ELSE score_zoning := 5; -- would need rezoning
    END IF;

    -- Lot size (20 points)
    IF p_lot_area_sqm >= 2000 THEN score_lot := 20;
    ELSIF p_lot_area_sqm >= 1500 THEN score_lot := 15;
    ELSIF p_lot_area_sqm >= 1000 THEN score_lot := 10;
    ELSIF p_lot_area_sqm >= 800 THEN score_lot := 5;
    ELSE score_lot := 0;
    END IF;

    -- Walkability (20 points)
    IF p_dist_to_residential_core_m <= 800 THEN score_walk := 20;
    ELSIF p_dist_to_residential_core_m <= 1500 THEN score_walk := 15;
    ELSIF p_dist_to_residential_core_m <= 2500 THEN score_walk := 8;
    ELSE score_walk := 0;
    END IF;

    -- Availability (15 points)
    IF p_owner_type = 'Municipal' AND p_no_building THEN score_avail := 15;
    ELSIF p_mls_number IS NOT NULL THEN score_avail := 12;
    ELSIF p_owner_type = 'Municipal' THEN score_avail := 8;
    ELSE score_avail := 0;
    END IF;

    -- Cost (10 points)
    IF p_total_value IS NULL THEN score_cost := 5; -- unknown
    ELSIF p_total_value < 2000000 THEN score_cost := 10;
    ELSIF p_total_value < 5000000 THEN score_cost := 7;
    ELSIF p_total_value < 10000000 THEN score_cost := 4;
    ELSE score_cost := 1;
    END IF;

    -- Transit (5 points)
    IF p_dist_to_canada_line_m < 500 THEN score_transit := 5;
    ELSIF p_dist_to_canada_line_m < 1000 THEN score_transit := 3;
    ELSE score_transit := 1;
    END IF;

    -- Flood risk (5 points)
    IF p_flood_hazard_level IS NULL OR p_flood_hazard_level = '' THEN score_flood := 5;
    ELSIF p_flood_hazard_level = 'Low' THEN score_flood := 3;
    ELSE score_flood := 1;
    END IF;

    total := score_zoning + score_lot + score_walk + score_avail + score_cost + score_transit + score_flood;

    RETURN jsonb_build_object(
        'total', total,
        'zoning', score_zoning,
        'lot_size', score_lot,
        'walkability', score_walk,
        'availability', score_avail,
        'cost', score_cost,
        'transit', score_transit,
        'flood_risk', score_flood
    );
END;
$$ LANGUAGE plpgsql;
### 4.3 Add score to enriched_parcels view

Add a suitability_score column to the materialized view that calls this function for each parcel.

### 4.4 Frontend: Synagogue Mode

When the user toggles "Synagogue Mode":

Map re-colors parcels on a green-yellow-red gradient based on suitability score
A ranked list appears in a side panel showing the top 20 parcels sorted by score
The detail panel shows a score breakdown radar chart or bar chart
Parcels scoring 0 (ALR, too small, too far) are dimmed or hidden
A "walkshed" polygon is drawn on the map showing the 2km walking radius from a configurable center point (default: center of the Brighouse / City Centre neighborhood)
### 4.5 Configurable center point

The "residential core" for the walkability calculation should be configurable. The default is the approximate center of where Jewish families in Richmond are likely to live (e.g., Brighouse area, near No. 3 Road and Westminster Highway). The committee should be able to:

Drag a pin on the map to set the center
Enter an address
The scores re-calculate in real-time based on walking distance from the new center
Phase 4 output: The dashboard has a "Synagogue Mode" that instantly surfaces and ranks the best candidate sites.

Phase 5: Polish, Auth, and Deployment
Duration: 2–3 weeks Goal: Production-ready deployment with authentication, data refresh monitoring, and user-facing documentation. Deliverable: Publicly accessible dashboard at a custom domain.

Step-by-step tasks:
### 5.1 Authentication (optional for v1)

If the tool is for the synagogue committee only:

Simple password-protected access (basic auth or a shared link with a token)
No user accounts needed
If the tool is for broader public use:

User accounts with email/password (Auth0, Clerk, or Supabase Auth)
Free tier shows municipal data only
Paid tier ($10–50/month) adds MLS listing data (to cover API costs)
### 5.2 MLS IDX compliance

If displaying MLS listings publicly, you must comply with GVR's IDX rules:

Display the listing broker's name and contact information
Include the GVR/MLS disclaimer text
Do not modify listing descriptions or photos
Include a "Data provided by [Board Name]" attribution
Refresh data at least daily (stale data violates IDX rules)
Some boards require a click-through registration before showing listing details
Have the sponsoring REALTOR® review the display for compliance before launch.

### 5.3 Data freshness monitoring

Build a simple admin dashboard or health check endpoint that shows:

Last successful sync for each data source
Number of records in each table
Number of unmatched listings
Alerts if any sync fails or data is older than expected
### 5.4 Export functionality

Users should be able to:

Export the current filtered view as CSV (for spreadsheet analysis)
Export as GeoJSON (for use in QGIS or other GIS tools)
Print the map view as a PDF report (for committee meetings)
### 5.5 Mobile responsiveness

The map and filter panel should work on tablets (committee members may use iPads at meetings). Full mobile phone support is lower priority but the layout should not break.

### 5.6 Documentation

User guide: How to use each filter, what the colors mean, how to interpret suitability scores
Data dictionary: What each field means and where it comes from
Methodology doc: How vacancy is determined, how scores are calculated, what the limitations are (important for transparency)
Phase 5 output: A production-deployed, documented, IDX-compliant dashboard ready for use by the synagogue committee and potentially the broader Richmond community.

## 16. Synagogue Suitability Criteria — Deep Dive
This section explains every criterion in the suitability scoring algorithm, why it matters for a synagogue specifically, and how the thresholds were chosen.

### 16.1 Zoning Compatibility (Weight: 25/100)
Why it matters: A synagogue is classified as an "assembly" or "institutional" use under Richmond's Zoning Bylaw 8500. If the current zoning doesn't permit this use, the community must apply for rezoning — a process that costs $50,000–200,000+, takes 1–3 years, and may be rejected.

How to determine which zones allow assembly:

You must read Bylaw 8500 (available at richmond.ca) and for each zone, check Section 14 (Institutional and Assembly Districts) and the individual zone section's "Permitted Uses" table.

Likely zone codes that permit assembly/worship:

| Zone Code | Description | Assembly Status (VERIFY) |
|---|---|---| | ASY | Assembly | Outright permitted — this is specifically for this use |
| INS | Institutional | Outright permitted |
| C1 | Local Commercial | Conditional — may allow with development permit |
| C2 | General Commercial | Conditional — may allow as secondary use |
| C3 | Community Commercial | Conditional |
| CDT1/CDT2 | City Centre commercial | Conditional — depends on specific provisions |
| RM zones | Multi-family residential | Generally not permitted — would need rezoning |
| RS zones | Single-family residential | Not permitted |
| AG zones | Agricultural | Not permitted — also in ALR, essentially impossible |
| PK | Park | Not permitted (but city-owned, so could theoretically be re-designated) |
| IL/IB/IG | Industrial | Not permitted |

⚠️ CRITICAL: These are educated guesses. You must read the actual bylaw text for each zone before populating the lookup table. The city's planning department can also provide guidance.

Scoring:

25 points: Assembly is an outright permitted use in the parcel's current zone
15 points: Assembly is a conditional use (possible with a development permit)
5 points: Assembly is not permitted but the zone and context suggest rezoning is plausible (e.g., a commercial zone adjacent to an existing institutional use)
0 points: In ALR or in a zone where rezoning to assembly is extremely unlikely
### 16.2 Lot Size (Weight: 20/100)
Why it matters: A synagogue needs:

Sanctuary: 200–400m² (seating for 100–300 people)
Social hall/kitchen: 100–200m²
Classrooms (Hebrew school): 100–200m²
Office/administration: 50–100m²
Lobby/corridors/washrooms: 100m²
Total building footprint: ~600–1000m²
Parking: Richmond's Zoning Bylaw requires parking for assembly uses. Typically 1 space per 4–10 seats. For 200 seats: 20–50 spaces. At ~25m² per space (including aisles): 500–1250m²
Setbacks and landscaping: Variable by zone, typically 3–6m on each side
Minimum viable lot size: ~1000m² (very tight, likely multi-story) Comfortable lot size: ~1500–2000m² (allows single-story with surface parking) Ideal lot size: 2000m²+ (room for future expansion, outdoor space)

Scoring:

20 points: ≥2000m²
15 points: 1500–1999m²
10 points: 1000–1499m²
5 points: 800–999m²
0 points: <800m²
### 16.3 Walkability to Residential Core (Weight: 20/100)
Why it matters: This is the uniquely Jewish requirement that distinguishes this use case from a generic community center search. Observant Jews do not drive on Shabbat. They must walk to synagogue. This means:

The synagogue must be within reasonable walking distance of where congregants live
"Reasonable" for a healthy adult is typically 1–2 km (15–25 minute walk)
For elderly or families with small children: <1 km is strongly preferred
The walk should be on safe, lit, sidewalked streets (Richmond's central area generally meets this)
How to measure: We define a "residential centroid" — the approximate center of where Jewish families in Richmond live. This is configurable in the dashboard (see Phase 4). The default should be set based on input from the synagogue committee.

A good starting point is the Brighouse / City Centre area (near No. 3 Road and Westminster Highway), which is Richmond's densest residential neighborhood and where many families in the community likely reside.

Distance is calculated as walking distance, not straight-line distance. For the MVP, use straight-line distance × 1.3 (a standard urban walking distance adjustment factor). For a more accurate version, use the Mapbox or Google Maps Directions API to calculate actual walking routes.

Scoring:

20 points: ≤800m from residential centroid (10-minute walk)
15 points: 800–1500m (15-20 minute walk)
8 points: 1500–2500m (25-35 minute walk — feasible but inconvenient)
0 points: >2500m (too far to walk regularly)
### 16.4 Availability (Weight: 15/100)
Why it matters: A perfect site is useless if you can't acquire it.

Scoring:

15 points: City-owned vacant land (strongest signal — the city may lease or sell at below-market rates for community use)
12 points: Currently listed for sale on MLS (available on the open market)
8 points: City-owned with a building (might be available but requires negotiation and possibly demolition)
0 points: Privately owned, not for sale (no indication of availability — would require cold-calling the owner)
### 16.5 Cost Feasibility (Weight: 10/100)
Why it matters: A synagogue community is typically funded by congregant donations, community fundraising, and possibly grants. Budget is limited. A $20M parcel in the commercial core is not realistic for most congregations.

Using assessed value as a proxy: BC Assessment values are not market values, but they're correlated. In Richmond, market values for commercial/institutional land are typically 1.5–3x assessed value. Use assessed value as a relative ranking.

Scoring:

10 points: Total assessed value < $2M
7 points: $2M–$5M
4 points: $5M–$10M
1 point: >$10M
For parcels with an MLS listing, use list price instead of assessed value.

### 16.6 Transit Proximity (Weight: 5/100)
Why it matters: While congregants walk on Shabbat, the synagogue is used throughout the week for classes, meetings, and events. Easy transit access makes it more accessible to the broader community, including those traveling from Vancouver or other parts of Metro Vancouver. It also affects property value and development potential.

Scoring:

5 points: <500m from a Canada Line station
3 points: 500–1000m from a Canada Line station
1 point: >1000m
### 16.7 Flood Risk (Weight: 5/100)
Why it matters: Richmond is a flood-prone area. Higher flood risk means higher construction costs (elevated foundation), higher insurance premiums, and operational risk. All else being equal, prefer lower-risk sites.

Scoring:

5 points: No designated flood hazard
3 points: Low flood hazard
1 point: Moderate or High flood hazard
### 16.8 Additional criteria (not scored, but displayed)
These factors should be shown in the detail panel but are not part of the automated score because they require subjective judgment or information that's hard to quantify:

| Factor | Display | Notes |
|---|---|---| | Nearby amenities | List: schools, parks, grocery stores within 500m | Important for community center function |
| Street frontage / visibility | Photo from Google Street View | A visible, accessible location is preferred |
| Adjacent land uses | List neighboring parcel zone codes | Avoid placing next to heavy industrial |
| Soil/geotechnical conditions | Note if available from city data | Affects construction cost (Richmond has variable soil due to river delta) |
| Heritage or environmental designation | Flag if parcel has heritage overlay or ESA | These add regulatory complexity |
| Shape of lot | Display length/width ratio | Irregular lots are harder to develop efficiently |
| Existing community facilities nearby | Map overlay of other places of worship, community centers | Useful context for the committee |

## 17. Infrastructure & Tooling Choices
### 17.1 Why PostGIS (not MongoDB, not a flat file)
Spatial joins are the core operation in this project. PostGIS handles them natively:

ST_Intersects, ST_Contains, ST_Within — polygon intersection queries
ST_Distance — distance calculations (using ::geography cast for meters)
ST_MakeEnvelope — bounding box filters
Spatial indexes (GiST) make these queries fast even on 50,000+ parcels
MongoDB has some geospatial support but it's limited. Flat files (GeoJSON on disk) would require loading everything into memory and using Turf.js for every query — fine for a prototype, but slow and memory-hungry at scale.

### 17.2 Why FastAPI (not Express, not Django)
Python is already needed for data ingestion (geopandas, requests)
FastAPI is the fastest Python web framework (async, built on Starlette)
Auto-generates API documentation (OpenAPI/Swagger)
Easy to learn for junior engineers
Django would work too but is heavier than needed — we don't need an ORM, template engine, or admin panel
If the team is more comfortable with JavaScript/TypeScript, Express.js with pg (postgres client) and node-cron is perfectly fine.

### 17.3 Why Mapbox GL JS (not Leaflet, not Google Maps)
| Feature | Leaflet | Mapbox GL JS | Google Maps |
|---|---|---|---| | Cost | Free | Free tier: 200k loads/month | Paid after trial |
| Vector tiles | No (raster only) | Yes | No |
| Performance with 50k polygons | Struggles | Handles well | Moderate |
| Satellite imagery | Via plugin | Built-in | Built-in |
| 3D buildings | No | Yes | Yes |
| Style customization | Limited | Extensive | Limited |
| Open source | Yes | Source available | No |
| Learning curve | Low | Medium | Low |

Recommendation: Start with Leaflet for the Phase 1 prototype (fastest to implement). Migrate to Mapbox GL JS in Phase 2 for better performance with dense polygon data.

### 17.4 Why React (not Vue, not vanilla JS)
Any modern frontend framework works. React is recommended because:

Largest ecosystem and community
Most junior developers know it
React Query (TanStack Query) makes API data fetching and caching easy
Mapbox GL JS has good React wrappers (react-map-gl)
If the team prefers Vue or Svelte, use those instead. The choice doesn't materially affect the project.

### 17.5 Hosting recommendations
| Component | Recommended | Cost | Alternative |
|---|---|---|---| | Database | Supabase (free tier: 500MB, includes PostGIS) | Free–$25/month | Neon (free tier), DigitalOcean Managed DB ($15/month) |
| Backend | Railway or Render | Free tier available; ~$7/month for always-on | DigitalOcean App Platform, Fly.io |
| Frontend | Vercel | Free for hobby projects | Netlify (free), Cloudflare Pages (free) |
| Domain | Namecheap or Cloudflare Registrar | ~$12/year for .ca |
|

Total hosting cost for MVP: $0–25/month

## 18. Cost Estimates
### 18.1 Data costs
| Source | Cost |
|---|---| | Richmond GeoHub (parcels, zoning, buildings) | Free |
| ParcelMap BC | Free |
| ALR boundary | Free |
| TransLink GTFS | Free |
| BC Address Geocoder | Free |
| BC Assessment (single lookups via web) | Free (limited) |
| BC Assessment (bulk data product) | $1,000–5,000/year (optional — can defer) |
| Repliers MLS API | ~$100–300/month |
| Mapbox GL JS | Free (under 200k map loads/month) |
| Google Maps Static API (thumbnails) | ~$2–10/month at low volume |

### 18.2 Infrastructure costs
| Item | Monthly Cost |
|---|---| | Database (Supabase or Neon free tier) | $0–25 |
| Backend hosting (Railway/Render) | $0–7 |
| Frontend hosting (Vercel) | $0 |
| Domain name | ~$1 (annualized) |
| Total infrastructure | $1–33/month |

### 18.3 Development time
| Phase | Effort (one developer) |
|---|---| | Phase 1: Data pipeline + static map | 2–3 weeks |
| Phase 2: Backend API + interactive frontend | 3–4 weeks |
| Phase 3: MLS integration | 2–6 weeks (mostly waiting for API access) |
| Phase 4: Suitability scoring | 1–2 weeks |
| Phase 5: Polish + deployment | 2–3 weeks |
| Total | 10–18 weeks |

If a junior developer is working full-time, expect ~4 months from start to production deployment. Phases 1–2 can be done in parallel with waiting for MLS API access (Phase 3).

### 18.4 Total project budget estimate
| Category | One-time | Monthly |
|---|---|---| | Development (if hiring) | $15,000–40,000 | — |
| MLS API | — | $100–300 |
| Hosting | — | $1–33 |
| BC Assessment bulk data (optional) | $1,000–5,000 | — |
| Domain | $12 | — |
| Total (building in-house) | $1,012–5,012 | $101–333 |

## 19. Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---| | MLS API access denied or delayed | Medium | High — no listing data | Start the application process immediately. Build Phases 1–2 without listing data. Have a REALTOR® partner lined up before starting Phase 3. Worst case: use manual listing data entry. |
| BC Assessment bulk data too expensive | Medium | Medium — lose best vacancy signal | Use building footprint + permit activity as vacancy proxies (free). Manually look up top candidates on bcassessment.ca. |
| GeoHub API schema changes | Low | Medium — ingestion scripts break | Version your ingestion scripts. Log raw API responses. Test sync weekly. |
| Zoning bylaw interpretation errors | Medium | High — incorrect suitability scores | Have a planner or the city's planning department review the zone-use permission table. Add a disclaimer: "Verify zoning with the City of Richmond before making any decisions." |
| No suitable sites found | Low–Medium | Very High — project doesn't achieve its goal | Expand the geographic search area. Lower minimum lot size. Consider parcels that would need rezoning. Consider multi-parcel assembly (buying two adjacent lots). Consider existing buildings that could be converted. |
| CORS issues with provincial WFS endpoints | High | Low — annoying but solvable | Always use a backend proxy for WFS requests. Never call provincial services directly from the browser. |
| Address matching failures (MLS to parcels) | High | Medium — some listings won't link to parcels | Use multi-step matching (spatial → geocode → fuzzy). Accept that ~10% may need manual matching. Display unmatched listings as dots on the map without parcel enrichment. |
| Data freshness concerns | Low | Low | Display "last updated" timestamps on the UI. Explain to users that assessed values are from prior year, zoning may lag recent bylaws, etc. |
| Parcel polygon misalignment with zoning polygons | High (known issue) | Medium — some parcels get wrong zone | Use parcel centroid for spatial join (not full polygon intersection). This works for 95%+ of parcels. For edge cases near zone boundaries, display both possible zones and flag for manual verification. |


## 20. Timeline
Week  1-2:  [Phase 1] Environment setup, data ingestion (parcels, zones, buildings, ALR, transit)
             START MLS API application process (parallel)
Week  3:    [Phase 1] Spatial joins, enriched view, zone-use lookup table, static Leaflet map
             ★ DELIVERABLE: Static map of city-owned vacant parcels
Week  4-5:  [Phase 2] Backend API (FastAPI), database queries, filter endpoints
Week  6-7:  [Phase 2] Frontend (React + Mapbox GL), filter panel, detail panel
             ★ DELIVERABLE: Interactive dashboard (no listings yet)
Week  8:    [Phase 3] MLS API integration (if access secured), listing sync, address matching
             If MLS not ready: continue polish on Phase 2, add export, improve scoring
Week  9:    [Phase 3] Listing display on map, IDX compliance, price filters
             ★ DELIVERABLE: Dashboard with live listings
Week 10-11: [Phase 4] Suitability scoring engine, Synagogue Mode, ranked list, configurable center
             ★ DELIVERABLE: Synagogue Mode with scored parcels
Week 12-13: [Phase 5] Auth, deployment, documentation, mobile responsiveness, monitoring
             ★ DELIVERABLE: Production deployment
Week 14:    [Phase 5] User testing with synagogue committee, feedback, iteration
             ★ DELIVERABLE: Refined dashboard based on feedback

## 21. Appendices

## Appendix A: How to Find GeoHub FeatureServer URLs
Go to https://richmond-geo-hub-cor.hub.arcgis.com/
Search for the dataset (e.g., "Parcels")
Click the dataset
Click "I want to use this" (or similar button)
Click "View API resources" or "APIs"
Copy the FeatureServer URL (not MapServer)
Test it by appending ?f=json in your browser — you should see the service metadata
To query features: <url>/query?where=1=1&outFields=*&outSR=4326&f=geojson&resultRecordCount=10
## Appendix B: How to Discover Hidden RIM Layers
Go to https://maps.richmond.ca/rim
Open Chrome DevTools (F12) → Network tab
Check "Preserve log" and filter by "XHR"
In RIM, enable a layer (e.g., "Building Permits")
Watch for network requests to URLs containing arcgis or MapServer or FeatureServer
Copy these URLs — they are functional ArcGIS REST endpoints
Test by appending /query?where=1=1&outFields=*&f=json&resultRecordCount=5
## Appendix C: Richmond Zoning Bylaw 8500 — Quick Reference
The full bylaw is at richmond.ca/cityhall/bylaws/zoningbylaw8500. Key sections for this project:

Part 7: Residential zones (RS, RT, RM) — generally do NOT permit assembly
Part 8: Commercial zones (C1, C2, C3, CA) — may permit assembly as conditional use
Part 9: Industrial zones (IL, IB, IG) — do NOT permit assembly
Part 10: Agricultural zones (AG1, AG2) — do NOT permit assembly (also ALR)
Part 14 (or similar): Institutional and Assembly zones (INS, ASY) — permit assembly outright
Part 15 (or similar): Special districts (CDT, CDA) — check each individually
⚠️ These part numbers are approximate. Read the actual bylaw to confirm.

## Appendix D: Existing Synagogues and Jewish Institutions in Metro Vancouver
Understanding where existing institutions are located helps contextualize the Richmond search:

| Institution | Location | Distance from Richmond Centre |
|---|---|---| | Beth Israel Synagogue | Vancouver (Oak & 28th) | ~15 km |
| Schara Tzedeck Synagogue | Vancouver (Oak & 19th) | ~14 km |
| Or Shalom Synagogue | Vancouver (Fraser & 10th) | ~13 km |
| Richmond Jewish Day School (if exists) | Richmond | Verify |
| Chabad of Richmond (if exists) | Richmond | Verify — may currently operate from a house or rented space |

If a Chabad or other Jewish organization already operates in Richmond, their current location may inform the "residential centroid" for the walkability calculation (since congregants likely live near it).

## Appendix E: Alternative Acquisition Strategies
The dashboard identifies candidate sites. Here are the acquisition strategies the committee should consider for each type:

| Parcel Type | Acquisition Strategy |
|---|---| | City-owned vacant land | Contact City of Richmond Real Estate Division. Request to lease or purchase. The city sometimes disposes of surplus land through public process. For community use, the city may offer below-market terms. Council approval is typically required. |
| City-owned land with building | Same as above, but may require demolition or renovation. The city may not want to dispose of land with an active use (e.g., community garden, temporary parking). |
| Crown Provincial land | Contact BC Housing or the Ministry responsible for the specific parcel. Provincial land is sometimes made available for community or affordable housing purposes. |
| Private land for sale (MLS) | Standard purchase through a real estate agent. Make an offer. Due diligence includes zoning verification, environmental assessment, geotechnical report. |
| Private land not for sale | Cold-call the owner (identified through BC Assessment or land title search). Some owners are willing to sell if approached with a serious offer. |
| Land requiring rezoning | Purchase conditionally (subject to rezoning). Apply for rezoning. Budget $50,000–200,000 for the application process. Timeline: 1–3 years. Not guaranteed. |
| Land assembly | Acquire two or more adjacent small parcels and consolidate. Requires negotiating with multiple owners. More complex but can yield a larger site. |

## Appendix F: Useful SQL Queries for the Synagogue Committee
-- Top 10 synagogue candidate sites, all types
SELECT pid, civic_address, owner_type, zone_code, permits_assembly,
       lot_area_sqm, total_value, list_price, no_building,
       ROUND(dist_to_canada_line_m) AS dist_transit_m,
       synagogue_score(...) AS score
FROM enriched_parcels
WHERE in_alr = FALSE
  AND lot_area_sqm >= 800
  AND ST_Within(geom, ST_MakeEnvelope(-123.17, 49.15, -123.10, 49.19, 4326))
ORDER BY (synagogue_score(...)->>'total')::int DESC
LIMIT 10;

-- All city-owned vacant land in central Richmond
SELECT pid, civic_address, lot_area_sqm, zone_code
FROM enriched_parcels
WHERE owner_type = 'Municipal'
  AND no_building = TRUE
  AND in_alr = FALSE
  AND ST_Within(geom, ST_MakeEnvelope(-123.17, 49.15, -123.10, 49.19, 4326))
ORDER BY lot_area_sqm DESC;

-- All active listings with assembly-permitted zoning
SELECT pid, civic_address, list_price, lot_area_sqm, zone_code, mls_number
FROM enriched_parcels
WHERE mls_number IS NOT NULL
  AND permits_assembly = TRUE
  AND ST_Within(geom, ST_MakeEnvelope(-123.17, 49.15, -123.10, 49.19, 4326))
ORDER BY list_price ASC;

-- Parcels within 1km walk of a specific point (e.g., community center at -123.1366, 49.1666)
SELECT pid, civic_address, lot_area_sqm, zone_code, owner_type,
       ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(-123.1366, 49.1666), 4326)::geography) AS dist_m
FROM enriched_parcels
WHERE in_alr = FALSE
  AND lot_area_sqm >= 800
  AND ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(-123.1366, 49.1666), 4326)::geography, 1000)
ORDER BY dist_m ASC;
## Appendix G: Checklist for Go-Live
- [ ] All GeoHub layers ingested and verified (parcels, zoning, buildings, permits)
- [ ] ParcelMap BC ingested for Crown/Federal parcels
- [ ] ALR boundary ingested
- [ ] TransLink stops ingested
- [ ] Zone-use permission table populated and reviewed against Bylaw 8500
- [ ] Enriched parcels materialized view created and verified
- [ ] Backend API endpoints tested with Swagger/OpenAPI docs
- [ ] Frontend map renders all parcels with correct colors
- [ ] Filter panel works (all filters applied to API query)
- [ ] Detail panel shows full enriched parcel data
- [ ] MLS listings synced and displayed (or: documented plan for when access is secured)
- [ ] Synagogue Mode scoring implemented and verified with test cases
- [ ] Ranked list in Synagogue Mode shows plausible candidates
- [ ] Walk distance center point is configurable
- [ ] Export to CSV works
- [ ] IDX compliance reviewed by sponsoring REALTOR® (if showing MLS data)
- [ ] Data freshness timestamps displayed
- [ ] Deployed to production environment
- [ ] Domain configured with HTTPS
- [ ] User guide written
- [ ] Methodology/limitations document written
- [ ] Synagogue committee has access and has been briefed on how to use it
This document is intended to be a living plan. As the project progresses, update it with actual FeatureServer URLs discovered, actual zone-use permissions confirmed from Bylaw 8500, actual costs encountered, and feedback from the synagogue committee. The plan is designed to be executed by a single junior-to-intermediate developer with access to standard web development tools and no prior GIS experience.

|