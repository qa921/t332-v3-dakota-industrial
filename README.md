# Dakota property workflow baseline

Original prerequisite code created on 2026-09-14, not a prior customer implementation. The opportunity scanner, nearby page, controls, filtering, aggregate analysis and corrected tests are deliberately absent and are contributor outputs.

The source sample contains 20 actual public parcel records from the Minnesota Geospatial Commons service. Only the allowlisted non-owner fields were fetched; source URL is preserved. These rows are a bounded input sample, not the full dataset. Query current records during task execution. Never infer roof age from year_built.

Backend starts with python backend/server.py after installing backend/requirements.txt. DATABASE_URL stays in Render secure environment configuration. DATABASE_SCHEMA identifies only this variation's database schema. /health confirms this baseline is reachable; /api/territory intentionally returns unavailable.

No customer authentication credentials or personal account records exist in this prerequisite yet. Do not call this family ready until the full original authorization contract and deployment destinations are prepared and verified.

Follow-up inputs: V2 exclusion must be an observed source record, without claiming it was handled historically. V3 must reserve two separately fetched source records. These follow-ups remain pending preparation.
