export const meta = {
  name: '002-travel-plan-detail-implement',
  description: 'Execute 002-travel-plan-detail 72-task implementation with 4 subagents: backend, frontend, testing, code-review',
  phases: [
    { title: 'Phase1-Setup', detail: 'Install dependencies, update config, create ignore files' },
    { title: 'Phase2-Foundational', detail: '001 LangChain migration, models, services, deps' },
    { title: 'Phase3-US1', detail: 'MVP: Travel plan overview page (budget, map, daily list)' },
    { title: 'Phase4-US2', detail: 'Day detail view (attractions, weather, accommodation, dining, transport)' },
    { title: 'Phase5-US3', detail: 'Edit itinerary (drag-drop reorder, delete attractions)' },
    { title: 'Phase6-US4', detail: 'Export travel plan (image/PDF)' },
    { title: 'Phase7-US5', detail: 'Replan travel plan (LangGraph StateGraph)' },
    { title: 'Phase8-Polish', detail: 'Observability, error handling, loading states, docs' },
    { title: 'Review', detail: 'Code review across all implemented changes' },
  ],
}

// ============================================================
// Shared context: task definitions for each agent per phase
// ============================================================

const TASKS_MD_PATH = 'specs/002-travel-plan-detail/tasks.md'
const PLAN_MD_PATH = 'specs/002-travel-plan-detail/plan.md'
const DATA_MODEL_PATH = 'specs/002-travel-plan-detail/data-model.md'
const API_CONTRACT_PATH = 'specs/002-travel-plan-detail/contracts/api-contract.md'

const BACKEND_PROMPT_BASE = `You are the BACKEND implementation agent for the 002-travel-plan-detail feature.

CONTEXT:
- Project: travel-helper (FastAPI backend + Vue 3 frontend)
- Task list: ${TASKS_MD_PATH}
- Plan: ${PLAN_MD_PATH}
- Data model: ${DATA_MODEL_PATH}
- API contract: ${API_CONTRACT_PATH}

RULES:
1. Read tasks.md to find tasks assigned to you (backend tasks)
2. Read plan.md and data-model.md for architecture context
3. Implement each task completely: write code, save files, mark task as [X] in tasks.md
4. Follow existing code patterns and conventions
5. Use Python type annotations everywhere
6. All comments and docstrings in CHINESE (中文)
7. After each task, update tasks.md to mark it as - [X]
8. Backend code goes in backend/app/ following existing layered structure (api → services → models → agents)
9. Do NOT run tests — that's handled by the testing agent
10. Do NOT review code — that's handled by the review agent

CURRENT PHASE: {phase}`

const FRONTEND_PROMPT_BASE = `You are the FRONTEND implementation agent for the 002-travel-plan-detail feature.

CONTEXT:
- Project: travel-helper (Vue 3 + TypeScript + Element Plus frontend)
- Task list: ${TASKS_MD_PATH}
- Plan: ${PLAN_MD_PATH}
- Data model: ${DATA_MODEL_PATH}

RULES:
1. Read tasks.md to find tasks assigned to you (frontend tasks: components, views, router, services, types)
2. Read plan.md for architecture context
3. Implement each task completely: write code, save files, mark task as [X] in tasks.md
4. Follow existing code patterns (Vue 3 Composition API, <script setup>, TypeScript)
5. Use Element Plus 2.x components consistently
6. All comments in CHINESE (中文)
7. After each task, update tasks.md to mark it as - [X]
8. Frontend code goes in frontend/src/ following existing structure
9. Do NOT run tests — that's handled by the testing agent
10. Do NOT review code — that's handled by the review agent

CURRENT PHASE: {phase}`

const TEST_PROMPT_BASE = `You are the TESTING agent for the 002-travel-plan-detail feature.

CONTEXT:
- Project: travel-helper
- Task list: ${TASKS_MD_PATH}
- API contract: ${API_CONTRACT_PATH}

RULES:
1. Read tasks.md to find test-related tasks
2. Write pytest tests for backend API contracts and unit tests
3. Write Vitest tests for frontend components (if applicable)
4. Mark test tasks as [X] in tasks.md when done
5. All test comments in CHINESE (中文)
6. Tests go in backend/tests/ following existing patterns

CURRENT PHASE: {phase}`

const REVIEW_PROMPT_BASE = `You are the CODE REVIEW agent for the 002-travel-plan-detail feature.

CONTEXT:
- Project: travel-helper
- Task list: ${TASKS_MD_PATH}
- Constitution: .specify/memory/constitution.md

RULES:
1. Read tasks.md to see what was implemented
2. Review backend code for: correctness, type safety, error handling, security, performance
3. Review frontend code for: TypeScript types, Element Plus usage, component structure, reactivity correctness
4. Report findings as a structured list with file:line references
5. Check constitution compliance
6. Do NOT modify files — only report issues
7. All review comments in CHINESE (中文)

CURRENT PHASE: {phase}`

// ============================================================
// Phase definitions
// ============================================================

phase('Phase1-Setup')

const setupResults = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 1: Setup — T001, T003, T004 (backend tasks)') +
    `\n\nTASKS TO EXECUTE:\n- T001: Add LangChain/LangGraph/LangSmith deps to backend/requirements.txt (check if already present)\n- T003: Add LangSmith config to backend/app/config.py (check if already present)\n- T004: Add LANGSMITH_API_KEY to backend/.env.example (check if already present)\n\nNOTE: These may already be done — verify before making changes.`,
    { label: 'backend-setup', phase: 'Phase1-Setup' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 1: Setup — T002 (frontend deps)') +
    `\n\nTASKS TO EXECUTE:\n- T002: Verify frontend package.json has html2canvas, jspdf, vuedraggable, @amap/amap-jsapi-loader (check if already installed)\n\nNOTE: These may already be in package.json — verify before making changes.`,
    { label: 'frontend-setup', phase: 'Phase1-Setup' }
  ),
])

// Create frontend .gitignore if missing
const gitignoreCheck = await agent(
  'Check if frontend/.gitignore exists. If not, create it with: node_modules/\ndist/\n*.local\n.env\n.DS_Store\nThumbs.db',
  { label: 'gitignore-check', phase: 'Phase1-Setup' }
)

log(`Phase 1 Setup complete: ${setupResults.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase2-Foundational')

const foundationalResults = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 2: Foundational — 001 LangChain migration + models + services') +
    `\n\nTASKS TO EXECUTE (in this order, respecting dependencies):

**Templates (T005-T007):**
- T005: Create backend/app/templates/__init__.py (if not exists)
- T006: Create backend/app/templates/_common.py with ROLE_DEFINITION, OUTPUT_FORMAT_CONSTRAINTS, PLANNING_PRINCIPLES (if not exists)
- T007: Create backend/app/templates/travel_planner/__init__.py and create.py with CREATE_SYSTEM_PROMPT and build_create_user_prompt (if not exists)

**Models (T008, T011):**
- T008: backend/app/models/travel_plan_output.py already exists with TravelPlanOutput, DailyItineraryOutput, etc. Verify it's complete per data-model.md.
- T011: Expand backend/app/models/travel_plan.py with new models per data-model.md: TravelPlanResponse (new version with id, destination as DestinationCity, dateRange, budget, dailyItineraries as DailyItineraryFull), DailyItinerary, AttractionDetail, AccommodationPlan, DiningPlan, TransportationPlan, WeatherInfo, BudgetBreakdown, etc. Keep existing TravelPlanCreateRequest and old TravelPlanResponse for backward compat or migrate.

**Services (T009, T013, T014, T015):**
- T009: Replace backend/app/services/llm_service.py with LangChain version using ChatOpenAI + with_structured_output + built-in retry/timeout
- T013: Create backend/app/services/amap_service.py — wrap Gaode AMap POI search (/v3/place/text), weather (/v3/weather/weatherInfo), route planning (/v3/direction/driving), geocoding (/v3/geocode/geo), reverse geocoding (/v3/geocode/regeo). Use httpx, JSON return.
- T014: Create backend/app/services/weather_service.py — weather data cache layer based on destination city and date
- T015: Create backend/app/services/unsplash_service.py — attraction image fetching using UNSPLASH_ACCESS_KEY

**Agents (T010):**
- T010: Rewrite backend/app/agents/travel_planner_agent.py to use ChatPromptTemplate + bind Pydantic output model via LangChain

**Deps (T016):**
- T016: Create backend/app/api/deps.py — dependency injection for AMap MCP client, LLM client, LangGraph StateGraph instance

CRITICAL NOTES:
- templates/__init__.py, _common.py, and travel_planner/create.py already exist — READ them first before modifying
- travel_plan_output.py already exists — READ it first
- llm_service.py currently uses OpenAI SDK — migrate to LangChain ChatOpenAI
- travel_planner_agent.py currently uses old prompt building — migrate to LangChain ChatPromptTemplate
- Keep backward compatibility where possible`,
    { label: 'backend-foundational', phase: 'Phase2-Foundational', isolation: 'worktree' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 2: Foundational — TypeScript types') +
    `\n\nTASKS TO EXECUTE:
- T012: frontend/src/types/travelPlan.ts already exists with 002 module types (DestinationCity, DateRange, TravelPreferences, BudgetBreakdown, AttractionDetail, etc.) — VERIFY all types are present and correct per data-model.md. Add any missing types.

READ the current file first. The types section for 002 module already exists — do NOT duplicate or overwrite working types. Only add missing ones.`,
    { label: 'frontend-types', phase: 'Phase2-Foundational' }
  ),
])

log(`Phase 2 Foundational complete: ${foundationalResults.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase3-US1')

const us1Results = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 3: User Story 1 — Travel plan overview (MVP)') +
    `\n\nTASKS TO EXECUTE (in order):

- T017: Backend API contract test — backend/tests/contract/test_travel_plan_api.py — test GET /api/v1/travel-plans/{id} returns full TravelPlanResponse
- T018: Backend unit test — backend/tests/unit/test_travel_plan_model.py — Pydantic model field validation, budget total calculation
- T020: Expand backend/app/api/routes/travel_plan.py — add GET /api/v1/travel-plans/{id} endpoint (returns full travel plan data with budget, map coords, daily summaries). Use path param {id} which is a UUID string.
- T021: In backend/app/services/travel_plan_service.py — implement get_travel_plan method (query from 001 module generated data, supplement with map coords and weather). Use localStorage-equivalent data or in-memory storage keyed by plan ID.
- T025: Note — this is frontend, skip it
- T026: Note — this is frontend, skip it
- T027: Note — this is frontend, skip it
- T028: Note — this is frontend, skip it
- T029: Note — this is integration, skip it

IMPORTANT: Since this is a single-user app with localStorage, the backend needs a simple in-memory store (dict) keyed by plan ID to serve GET requests. The 001 module's create endpoint should store the generated plan in this dict.

FOCUS: T017 (test), T018 (test), T020 (API endpoint), T021 (service method)

For the in-memory store, create a simple dict in travel_plan_service.py:
  _plans: dict[str, TravelPlanFull] = {}

And ensure the POST /travel-plans/generate endpoint stores the result in this dict with a generated UUID.`,
    { label: 'backend-us1', phase: 'Phase3-US1' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 3: User Story 1 — Travel plan overview (MVP)') +
    `\n\nTASKS TO EXECUTE (in order):

- T019: Frontend component test — frontend/tests/unit/BudgetCard.spec.ts — test budget card renders category amounts and total
- T022: Create frontend/src/components/BudgetCard.vue — budget detail card, Element Plus el-card + category amount display. Shows attractionTickets, hotelAccommodation, diningTransport, diningFood, total. Use Element Plus el-descriptions or el-statistic for amounts.
- T023: Create frontend/src/components/MapView.vue — AMap map embed, onMounted init AMap via @amap/amap-jsapi-loader, render attraction and accommodation markers. Use el-card container with fixed height div. Handle loading/error states with placeholders.
- T024: Create frontend/src/components/DailyScheduleList.vue — daily schedule overview list, Element Plus el-timeline or el-table, click to jump to detail page (/travel-plans/:id/day/:dayIndex).
- T025: Create frontend/src/views/TravelPlanOverview.vue — overview page main component, assembles BudgetCard + MapView + DailyScheduleList, Axios calls GET API. Add toolbar area with buttons for export and replan (placeholders for now).
- T026: Update frontend/src/router/index.ts — register overview route /travel-plans/:id/overview
- T027: Create frontend/src/services/travelPlanService.ts — Axios wrapper, calls backend travel plan API (getTravelPlan, getDayDetail, updateDay, replan)
- T028: Create frontend/src/services/storageService.ts — localStorage read/write wrapper, stores/gets travel plan ID
- T029: Integration — connect 001 module's create success callback to jump to overview page (pass plan ID). Modify frontend/src/views/TravelPlanCreate.vue to use router.push after successful plan generation, storing plan ID in localStorage.

IMPORTANT:
- Use the types from frontend/src/types/travelPlan.ts (TravelPlanFull, DailyItineraryFull, BudgetBreakdown, etc.)
- All components use <script setup lang="ts">
- Use Element Plus components consistently
- MapView needs VITE_AMAP_KEY from env — add to frontend/.env.example
- TravelPlanOverview should handle loading states with el-skeleton or v-loading`,
    { label: 'frontend-us1', phase: 'Phase3-US1' }
  ),
])

log(`Phase 3 US1 (MVP) complete: ${us1Results.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase4-US2')

const us2Results = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 4: User Story 2 — Day detail view') +
    `\n\nTASKS TO EXECUTE (in order):

- T030: Backend API contract test — backend/tests/contract/test_day_detail_api.py — test GET /api/v1/travel-plans/{id}/day/{dayIndex} returns full day data
- T031: Note — frontend test, skip
- T032: Add GET /api/v1/travel-plans/{id}/day/{dayIndex} endpoint in backend/app/api/routes/travel_plan.py
- T033: Implement get_day_detail method in backend/app/services/travel_plan_service.py — filter by dayIndex, supplement with weather, attraction images (via unsplash_service)

FOCUS:
- T030 (test), T032 (API endpoint), T033 (service method)
- The endpoint returns a single day's full itinerary data
- Use weather_service to get weather data for the day's date
- Use unsplash_service to get images for attractions that lack images`,
    { label: 'backend-us2', phase: 'Phase4-US2' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 4: User Story 2 — Day detail view') +
    `\n\nTASKS TO EXECUTE (in order):

- T031: Frontend component test — frontend/tests/unit/AttractionCard.spec.ts — test attraction card renders image, name, play duration, features, description
- T034: Create frontend/src/components/AttractionCard.vue — attraction detail card, Element Plus el-card + image lazy loading + feature tags. Shows imageUrl, name, playDuration, description, features, tips.
- T035: Create frontend/src/components/ScheduleTimeline.vue — schedule timeline showing time periods and activities. Use Element Plus el-timeline with el-timeline-item for each TimeSlot.
- T036: Create frontend/src/components/AccommodationInfo.vue — accommodation info display, Element Plus el-descriptions for hotelName, roomType, address, checkIn, checkOut, amenities.
- T037: Create frontend/src/components/DiningInfo.vue — dining info display, breakfast/lunch/dinner recommendations. Use el-descriptions or el-card sections.
- T038: Create frontend/src/components/TransportationInfo.vue — transportation info display, type + description for each plan. Use el-table or el-descriptions list.
- T039: Create frontend/src/components/WeatherInfo.vue — weather info display, condition + temp range + wind speed. Use Element Plus el-tag for weather condition, show temp as "low°C ~ high°C".
- T040: Create frontend/src/views/TravelPlanDayDetail.vue — day detail page, assembles all sub-components (AttractionCard list, ScheduleTimeline, AccommodationInfo, DiningInfo, TransportationInfo, WeatherInfo). Has "Edit Itinerary" button placeholder.
- T041: Update frontend/src/router/index.ts — register detail route /travel-plans/:id/day/:dayIndex
- T042: Integration — DailyScheduleList click navigation to detail page, passing planId and dayIndex. Update DailyScheduleList.vue to use router.push.

IMPORTANT:
- All components use <script setup lang="ts">
- Use props for data input
- Handle loading states
- Use the types from types/travelPlan.ts`,
    { label: 'frontend-us2', phase: 'Phase4-US2' }
  ),
])

log(`Phase 4 US2 (Day Detail) complete: ${us2Results.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase5-US3')

const us3Results = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 5: User Story 3 — Edit itinerary') +
    `\n\nTASKS TO EXECUTE (in order):

- T043: Backend API contract test — backend/tests/contract/test_edit_day_api.py — test PUT /api/v1/travel-plans/{id}/day/{dayIndex} updates day itinerary
- T044: Backend unit test — backend/tests/unit/test_edit_day_validation.py — validation rule: at least 1 attraction must remain
- T045: Add PUT /api/v1/travel-plans/{id}/day/{dayIndex} endpoint in backend/app/api/routes/travel_plan.py
- T046: Implement update_day_itinerary in backend/app/services/travel_plan_service.py — validate at least 1 attraction, update dailyItineraries for that day, update updatedAt
- T047: Create backend/app/templates/travel_planner/edit_day.py — EDIT_DAY_PROMPT template for AI-assisted edit scenario (optional but recommended)

FOCUS:
- T043 (test), T044 (test), T045 (API endpoint), T046 (service), T047 (template)
- Validation: attractions list must have at least 1 item
- Request body matches EditDayRequest type from api-contract.md
- Response: { message, dayIndex, updatedAt }`,
    { label: 'backend-us3', phase: 'Phase5-US3' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 5: User Story 3 — Edit itinerary') +
    `\n\nTASKS TO EXECUTE (in order):

- T048: Create frontend/src/components/EditDayDrawer.vue — edit itinerary drawer, Element Plus el-drawer + vuedraggable drag-sort + delete buttons. Shows attraction cards with drag handles. Each card has a delete button (el-button type="danger" size="small"). Drawer has Save and Cancel buttons.
- T049: Integrate "Edit Itinerary" button and EditDayDrawer into frontend/src/views/TravelPlanDayDetail.vue (modify the existing file)
- T050: Integration — after drag sort completes, call PUT API via Axios to save update, then refresh detail page data. Wire up the save button in EditDayDrawer to call travelPlanService.updateDay() then reload data.

IMPORTANT:
- Use vuedraggable with <draggable v-model="localAttractions" item-key="id" tag="div">
- Import from 'vuedraggable' (Vue 3 version)
- The drawer emits events: 'save', 'cancel', and updates the parent via v-model for visible state
- Delete button should show confirmation (ElMessageBox.confirm) before removing
- Must validate at least 1 attraction remains before allowing save`,
    { label: 'frontend-us3', phase: 'Phase5-US3' }
  ),
])

log(`Phase 5 US3 (Edit) complete: ${us3Results.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase6-US4')

const us4Results = await parallel([
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 6: User Story 4 — Export travel plan') +
    `\n\nTASKS TO EXECUTE (in order):

- T051: Create frontend/src/components/ExportDropdown.vue — export dropdown, Element Plus el-dropdown, offers Image/PDF options. Emits 'export-image' and 'export-pdf' events.
- T052: Create frontend/src/services/exportService.ts — wraps html2canvas + jsPDF export logic:
  - Image export: html2canvas captures target DOM → canvas.toDataURL() → trigger <a download>
  - PDF export: html2canvas captures sections → jsPDF adds images page by page → jsPDF.save()
  - Export content: overview + all day summaries (skip map and complex DOM)
  - Handle loading state during generation
- T053: Integrate ExportDropdown into frontend/src/views/TravelPlanOverview.vue toolbar area (modify existing file)
- T054: Integration — auto-capture overview and all day summaries, generate file and trigger download. Wire up ExportDropdown events in TravelPlanOverview.

IMPORTANT:
- html2canvas and jsPDF are already in package.json
- export image: use html2canvas(element, { scale: 2, useCORS: true })
- export PDF: create jsPDF('p', 'mm', 'a4'), addImage per page, handle page breaks
- Skip map element (complex DOM that doesn't render well in canvas)
- Show loading indicator during export`,
    { label: 'frontend-us4', phase: 'Phase6-US4' }
  ),
])

log(`Phase 6 US4 (Export) complete: ${us4Results.filter(Boolean).length}/1 agents succeeded`)

// ============================================================

phase('Phase7-US5')

const us5Results = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 7: User Story 5 — Replan travel plan') +
    `\n\nTASKS TO EXECUTE (in order):

- T055: Create backend/app/templates/travel_planner/replan.py — REPLAN_PROMPT, injects current itinerary + user edit traces + new constraints
- T056: Implement LangGraph StateGraph in backend/app/agents/itinerary_agent.py — replanning flow node state management: collect context → call LLM → return new itinerary
- T057: Add POST /api/v1/travel-plans/{id}/replan endpoint in backend/app/api/routes/travel_plan.py — calls LangGraph StateGraph, returns new itinerary data

FOCUS:
- T055 (template), T056 (LangGraph agent), T057 (API endpoint)
- The StateGraph should have nodes: collect_context, call_llm, return_result
- Use LangGraph's StateGraph with proper state definition
- Integrate with LangSmith tracing if configured
- Endpoint returns { message, estimatedTime } immediately (async) or waits for completion (sync)
- Handle conflict: if replanning already in progress, return 409`,
    { label: 'backend-us5', phase: 'Phase7-US5' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 7: User Story 5 — Replan travel plan') +
    `\n\nTASKS TO EXECUTE (in order):

- T058: Create frontend/src/components/ReplanConfirmModal.vue — replan confirmation modal, Element Plus el-dialog, warning "Replanning will overwrite current itinerary and lose your edits". Has Confirm and Cancel buttons.
- T059: Integrate "Replan" button and ReplanConfirmModal into frontend/src/views/TravelPlanOverview.vue toolbar area (modify existing file)
- T060: Integration — on modal confirm, call POST replan API, wait for response, refresh overview data. Show loading state during replanning (it may take 30s).

IMPORTANT:
- ReplanConfirmModal emits 'confirm' event
- Show loading spinner during API call
- After successful replan, refresh all overview data
- Handle error: if 409 (already in progress), show message to user`,
    { label: 'frontend-us5', phase: 'Phase7-US5' }
  ),
])

log(`Phase 7 US5 (Replan) complete: ${us5Results.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Phase8-Polish')

const polishResults = await parallel([
  () => agent(
    BACKEND_PROMPT_BASE.replace('{phase}', 'Phase 8: Polish & Cross-Cutting') +
    `\n\nTASKS TO EXECUTE (in order):

- T061: Observability — Configure LangSmith tracing integration (backend/app/config.py set LANGSMITH_TRACING=true, auto-trace in LangGraph calls)
- T062: Observability — Add structured logging in API routes (request ID, timestamp, response status, duration)
- T063: Error handling — Unified error response format (all API errors return {"detail": "error message"} format)
- T067: Integration test — End-to-end flow test (create → overview → detail → edit → export), covering full user journey
- T068: Docs — Update specs/002-travel-plan-detail/quickstart.md with LangSmith config and LangGraph usage notes
- T069: Verification — Run quickstart.md steps, ensure end-to-end flow works

FOCUS:
- T061 (LangSmith config), T062 (logging), T063 (error format), T067 (e2e test), T068 (docs), T069 (verify)
- These are polish tasks — ensure they don't break existing functionality`,
    { label: 'backend-polish', phase: 'Phase8-Polish' }
  ),
  () => agent(
    FRONTEND_PROMPT_BASE.replace('{phase}', 'Phase 8: Polish & Cross-Cutting') +
    `\n\nTASKS TO EXECUTE (in order):

- T064: Loading states — Integrate loading skeleton/loading animation in all view components (FR-020). Use el-skeleton for loading states in TravelPlanOverview and TravelPlanDayDetail.
- T065: Placeholder handling — Show placeholder image when attraction image is missing, show placeholder map with retry button when map fails to load.
- T066: Create common style components in frontend/src/components/ — loading animation, empty state, error prompt components/patterns.

FOCUS:
- T064 (loading skeleton), T065 (placeholders), T066 (common states)
- Use Element Plus el-skeleton, el-empty, el-alert components
- Consistent styling across all components`,
    { label: 'frontend-polish', phase: 'Phase8-Polish' }
  ),
])

log(`Phase 8 Polish complete: ${polishResults.filter(Boolean).length}/2 agents succeeded`)

// ============================================================

phase('Review')

const reviewResult = await agent(
  REVIEW_PROMPT_BASE.replace('{phase}', 'Final Code Review') +
  `\n\nSCOPE:
1. Read tasks.md and check ALL tasks are marked as [X] (completed)
2. List any tasks that are still unchecked and report them
3. Review the overall implementation:
   - Backend: API routes, services, models, agents — correctness, type safety, error handling
   - Frontend: Views, components, services, router — TypeScript correctness, Element Plus usage, reactivity
   - Consistency between backend models and frontend types
   - Constitution compliance (read .specify/memory/constitution.md)
4. Report a structured summary:
   - ✅ Completed tasks count
   - ⚠️ Incomplete/unchecked tasks (list task IDs)
   - 🔴 Critical issues found (if any)
   - 🟡 Suggestions for improvement (if any)
   - 📊 Constitution compliance status`,
  { label: 'final-review', phase: 'Review' }
)

log(`Final review complete`)

// ============================================================
// Final summary
// ============================================================

const allResults = [
  ...setupResults.filter(Boolean),
  ...foundationalResults.filter(Boolean),
  ...us1Results.filter(Boolean),
  ...us2Results.filter(Boolean),
  ...us3Results.filter(Boolean),
  ...us4Results.filter(Boolean),
  ...us5Results.filter(Boolean),
  ...polishResults.filter(Boolean),
  reviewResult ? 'review-done' : null,
].filter(Boolean)

return {
  totalPhases: 9,
  agentsSucceeded: allResults.length,
  status: allResults.length > 0 ? 'completed' : 'failed',
  phases: [
    'Phase1-Setup',
    'Phase2-Foundational',
    'Phase3-US1 (MVP)',
    'Phase4-US2 (Day Detail)',
    'Phase5-US3 (Edit)',
    'Phase6-US4 (Export)',
    'Phase7-US5 (Replan)',
    'Phase8-Polish',
    'Review',
  ],
}
