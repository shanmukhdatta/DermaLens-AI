# Recruiter showcase deployment — Vercel + optional Python API

This guide prepares an **informational research engineering showcase**, not a clinically approved classifier. Medical analysis remains disabled in production. Do not claim performance metrics without real independent evidence.

## A. Deploy Next.js only (safe first release)

1. In Vercel, import `shanmukhdatta/DermaLens-AI`.
2. Set framework **Next.js**, **Root Directory = `apps/web`**, and Node.js 22+.
3. Leave `DERMALENS_WEB_API_BASE_URL` unset initially. The homepage, pipeline, privacy and browser-local research report pages still work. Image-check and docs lookup return **503/unavailable**, rather than fake results.
4. Deploy a **preview** first and check each page in desktop/mobile browsers: `/`, `/check`, `/assistant`, `/research`, `/history`, `/how-it-works`, `/privacy`.
5. Confirm links, reduced motion, keyboard focus, no console errors and clear “model unavailable” status.

**Deployment does not provide image classification.**

## B. Optional independent FastAPI deployment

Use `render.yaml` as the Docker API blueprint, or another container host with the same settings. The Docker API listens on port 8000 and uses health endpoint `/api/v1/health`. The **readiness endpoint intentionally responds 503** without verified model readiness: do not use it as a liveness probe.

At minimum, set on your API host:

| Environment key | Meaning |
| --- | --- |
| `DERMALENS_ENV=production` | Keeps experimental model-analysis route disabled |
| `DERMALENS_PUBLIC_WEB_ORIGIN=https://your-vercel-domain` | Exact HTTPS origin, no trailing slash/path |
| `DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS=true` | Enable *nonmedical* photo format/face suitability checks |
| `DERMALENS_ENABLE_RESEARCH_ANALYSES=false` | Required safe public default |
| `DERMALENS_ENABLE_IMAGE_STORAGE=false` | No raw-photo retention |
| `DERMALENS_ENABLE_RESEARCH_IMAGE_OPT_IN=false` | No research raw-photo retention |
| `DERMALENS_ENABLE_RAG_ASSISTANT=false` | Public docs lookup still works without Grok |
| `PORT=8000` | Align container port with host expectations if required |

For public quality and docs endpoints, the production API does **not** require PostgreSQL or OIDC. Privileged account/history/feedback paths remain unavailable unless you separately configure real database, issuer, audience, keys and privacy procedures. Do not place those credentials into Git.

Then in Vercel set (server-side, production and preview as appropriate):

```text
DERMALENS_WEB_API_BASE_URL=https://your-running-api-host
```

Redeploy Next.js after changing the environment variable. The frontend sends nonclinical photos through bounded same-origin `/api/public/quality` to the FastAPI quality endpoint. The proxy does not persist photos, send them to Grok, or classify diseases. The docs lookup uses `/api/public/docs`.

## C. Verify before sharing with recruiters

- `GET /api/v1/health` is 200 on the API host.
- `GET /api/v1/readiness` is 503 until model release review. This is intentional.
- Upload one **authorized** JPEG/PNG/WebP face image on `/check`; test wrong type, oversized file, no face and multiple faces; do not retain the photo or log request contents.
- Check `/assistant` with documentation questions; if API is absent, it should explain unavailability.
- Check six research class labels are **not shown as predictions**.
- Do not post sample health data, fake scores, model weights or secret tokens.
- Test `/research` with a non-identifying aggregate JSON result only.
- Run CI, responsive layout and keyboard navigation checks; confirm page title, citations and links.
- Validate HTTPS, traffic caps, error monitoring, incident response, model release blocks and relevant data/privacy requirements before any broader public use.

**Deployment evidence:** record actual Vercel URL, API host, commit SHA, browser screenshots and exact test outcomes. This repository has no published verified URL yet.

## D. Model and MLOps promotion later

Use the private model artifact runbook. Bring the real approved checkpoint and label map **outside public Git**, verify SHA256 and model/source parity, evaluate held-out real data, calibrate uncertainties, validate Grad-CAM and abstention and review with experts. Production medical-analysis flags remain off; specialist and regulatory clearance would be separate work.

The original research source is isolated under `research/legacy/`. Its heavy training requirements must not be installed by Vercel and must not be bundled into the public image-check API.

## E. Rollback

Use GitHub revert or Vercel rollback to the last reviewed deployment. If API traffic fails or a privacy issue is discovered, disconnect `DERMALENS_WEB_API_BASE_URL`, redeploy the web client and disable the backend endpoint until fixed. Never turn on a fake inference fallback to mask an outage.
