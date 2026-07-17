# MHES User Manual

---

## Cover Page

**System Name:** MHES — Man-Hour Estimation System

**Company Name:** (To Be Confirmed)

**Version:** 1.0

**Date:** 2026-07-17

**Document Number:** (To Be Confirmed)

---

## Revision History

| Version | Date | Description | Author |
|---|---|---|---|
| 1.0 | 2026-07-17 | Initial release of the User Manual | (To Be Confirmed) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [System Requirements](#3-system-requirements)
4. [Screen Descriptions](#4-screen-descriptions)
   - 4.1 [AI Chatbot](#41-ai-chatbot)
   - 4.2 [Upload Files](#42-upload-files)
   - 4.3 [Preview](#43-preview)
   - 4.4 [Temporary Data List](#44-temporary-data-list)
   - 4.5 [Temporary Data Detail](#45-temporary-data-detail)
   - 4.6 [Exported Files](#46-exported-files)
   - 4.7 [Export Detail](#47-export-detail)
5. [Business Operations](#5-business-operations)
6. [Error Messages](#6-error-messages)
7. [Frequently Asked Questions (FAQ)](#7-frequently-asked-questions-faq)
8. [Limitations](#8-limitations)
9. [Appendix](#9-appendix)

---

## 1. Introduction

### Purpose

This manual explains how to use MHES (Man-Hour Estimation System), a web application that helps Infrastructure Engineers create man-hour estimates for infrastructure projects. It describes every screen, the actions available on each screen, and the step-by-step procedures for common tasks such as uploading knowledge files, searching for estimation data, assembling an estimate, and exporting it to Excel.

### Intended Audience

This manual is written for end users of MHES, including:

- Infrastructure Engineers who search for tasks and assemble estimates
- Project Managers who review estimates and export reports
- System Administrators who upload knowledge base files and monitor the system
- Technical Leads who validate estimates against historical data

No programming or database knowledge is required to use this manual.

### Scope

This manual covers all end-user–facing screens and workflows of MHES: the AI Chatbot search screen, the Upload Files screen, the Preview (estimate assembly) screen, the Temporary Data screens, and the Exported Files screens.

It does not cover source code, internal architecture, or database/file-storage design. Developers and system architects should refer to the project's technical documentation instead.

### Definitions

| Term | Definition |
|---|---|
| Knowledge Base (KB) | The collection of uploaded Excel files that MHES searches to find man-hour estimation data |
| Category | The top level of the estimation hierarchy (e.g., a project or system type) |
| Task | A unit of work within a Category |
| Activity / Activity Detail | A specific action within a Task, with its own estimated hours |
| Buffer | Additional hours added to a Task to account for contingency |
| Preview | The screen where a user assembles and edits an estimate before exporting it |
| Stash / Temporary Data | An automatic server-side backup of in-progress Preview data |
| Embedding | The AI-generated representation of text used to power semantic search (internal process; not user-configured) |

---

## 2. System Overview

### System Overview

MHES is an internal, AI-assisted tool that converts historical man-hour estimation spreadsheets into searchable, editable, and exportable project estimates. Engineers upload historical Excel estimation sheets, and the system automatically indexes them so users can search using natural language, assemble the matching results into a new estimate, edit it, and export it as a formatted Excel file.

### Main Features

- **Knowledge Base Management** — Upload one or more Excel (`.xlsx`) files containing historical man-hour data. Duplicate files can be renamed or overwritten. Files can be deleted or re-indexed at any time.
- **AI Semantic Search (Chatbot)** — A chat-style interface for describing what estimate data is needed in plain language.
- **Interactive Preview** — Search results are assembled into an editable Category → Task → Activity estimate, with live-recalculated totals.
- **Excel Export** — Generates a professionally formatted `.xlsx` estimate file for download.
- **Temporary Data (Preview Stashing)** — In-progress Preview data is automatically backed up on the server and can be restored later.

### System Workflow

1. **Upload** — Knowledge files are uploaded and stored in the Knowledge Base.
2. **Embed** — Each file is automatically indexed for AI search.
3. **Search** — The user asks the Chatbot for the estimate data needed.
4. **Preview** — Matched results are assembled and edited on the Preview screen.
5. **Export** — The finished estimate is exported to a formatted Excel workbook.
6. **Temporary Data** — Unsaved Preview work is automatically saved and can be restored later.

---

## 3. System Requirements

### Supported Browsers

MHES has no officially tested browser-support list, but its front-end dependencies require a modern, evergreen browser:

- Google Chrome (current version)
- Microsoft Edge (current version)
- Mozilla Firefox (current version)
- Safari (current version)

This is because MHES is built on Bootstrap 5.3.3 and the Quill 2.0.3 rich-text editor, both of which require modern browsers and do not support Internet Explorer. The page also has no `X-UA-Compatible` meta tag or legacy-browser fallback.

### Operating Systems

(To Be Confirmed)

### Screen Resolution

(To Be Confirmed)

### Hardware/Software Requirements

**Server-side (confirmed from the project's installation prerequisites and dependencies):**

| Requirement | Details |
|---|---|
| Python | Version 3.11 or later |
| Web framework | Flask 3.1.1 (served via Waitress 3.0.2 in production) |
| Data processing | pandas 2.2.3, openpyxl 3.1.5 |
| AI / search | sentence-transformers 3.4.1, FAISS (CPU-only build — no GPU required) |
| Scheduling | APScheduler 3.11.3 (in-process background jobs) |
| Cloud storage | google-cloud-storage 3.13.0 (for storing exported Excel files) |
| Ollama (optional) | `qwen2.5:3b` model — installable but not yet connected to the chatbot; not required for current functionality |
| GPU | Not required — the AI search feature uses the CPU-only FAISS build |

**Client-side:** A supported web browser (see above). No software installation is required on the user's device.

**Hardware (not documented in the project):** There is no stated minimum CPU, RAM, or disk specification. As a general guide: disk usage grows with the size of the Knowledge Base (each uploaded Excel file also stores a corresponding AI search index), and since no GPU is required, standard commodity server hardware is sufficient to run the application. Specific minimums should be confirmed with your system administrator based on expected Knowledge Base size and user load.

> **Note:** MHES is a browser-based web application accessed via a URL provided by your system administrator. No client-side installation is required.

---

## 4. Screen Descriptions

All screens share a common navigation sidebar with links to: **AI Chatbot**, **Preview**, **Temporary Data List** (shows a live count badge of stashed items), **Exported File List**, and **Upload Files** (shows a badge indicating how many knowledge files are missing embeddings). The sidebar can be collapsed or expanded, and this preference is remembered on the device. System messages (confirmations, warnings, and errors) appear as dismissible colored banners at the top of the page content.

### 4.1 AI Chatbot

**Screen Purpose**

The main landing page. Lets a user describe, in plain language, what estimate data they are looking for, and returns matching results from the Knowledge Base.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |               Main Area                  |
|      |  [ Chat message history ]                |
|      |  [ Results table with checkboxes ]        |
|      |  [ Text input ..................] [Send] |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | Text input field | Where the user types their search query |
| 2 | Send button (paper-plane icon) | Submits the query; pressing Enter has the same effect |
| 3 | Results table | Displays Category, Task List, Activity Details, Activity Details Estimate (Hours), Estimate (Hours), Buffer (Hours), Task Estimate (Hours), and Resource (source file), with a totals row |
| 4 | Selection checkboxes | One per result row, used to choose which items to send to Preview |
| 5 | "None of the above" checkbox | Included in the selection bar |
| 6 | "Go to Preview (N selected)" button | Sends the selected items to the Preview screen |

**Validation Rules**

- The search query cannot be empty. Submitting an empty query returns the message "Please enter a search query."

**Navigation**

Reached by opening the application (this is the default landing page `/`), or via the **AI Chatbot** link in the sidebar from any other screen.

**Available Operations**

- Type a question describing the estimation data needed and press **Send** or **Enter**.
- Review the grouped Category → Task → Activity results.
- Select one or more result rows using the checkboxes.
- Click **Go to Preview** to carry the selected items into the Preview screen.

**Related Screens**

- **Preview** — selected search results are sent here for assembly and editing.
- **Upload Files** — if a search returns no results, files may need to be uploaded first.

**User Permissions**

No access restrictions — all users can use this screen.

**Notes**

- If no matching results are found, the message displayed is: "Sorry, I couldn't find any matching results for your query. Try different keywords or check if knowledge files have been uploaded."
- If the server cannot be reached, the message displayed is: "Failed to connect to the server. Please try again."
- The conversation history is only kept when returning to this screen via the Preview screen's **Add More / Back to Chatbot** link. Arriving at this screen any other way starts a fresh conversation, and any unsaved Preview data is automatically stashed to Temporary Data first.

---

### 4.2 Upload Files

**Screen Purpose**

Lets a user upload Excel knowledge files into the Knowledge Base and manage existing files (view embedding status, re-embed, or delete).

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  [Download Template] [Browse Files...]  |
|      |  [Selected file list]                   |
|      |  [Upload & Generate Embeddings]          |
|      |  [Knowledge Base file table]             |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | "Download Template" button | Downloads a sample `.xlsx` file showing the expected column layout |
| 2 | "Browse Files..." button | Opens the file picker (multiple `.xlsx` files can be selected) |
| 3 | Selected file list with "×" remove buttons | Shows files chosen but not yet uploaded |
| 4 | "Upload & Generate Embeddings" button | Uploads the selected file(s); disabled until at least one valid file is selected |
| 5 | Knowledge Base table | Lists all uploaded files |
| 6 | "↻" re-embed button (per row) | Shown only for files missing embeddings; regenerates the AI index for that file |
| 7 | Delete (trash) button (per row) | Removes a file from the Knowledge Base after confirmation |
| 8 | Duplicate-file modal | Appears when an uploaded file name already exists, with "Auto-Rename", "Overwrite", and "Cancel" options |

**Input Field / Validation Rules**

| Field | Rule |
|---|---|
| File selection | Only `.xlsx` files are accepted; other file types are rejected client-side with the message "Skipped invalid file(s) (only .xlsx is supported): ..." |
| File size | Maximum 10 MB per file |
| Duplicate file name | User must choose "Auto-Rename" or "Overwrite" via the modal, or "Cancel" the upload |

**Navigation**

Reached via the **Upload Files** link in the sidebar (which also shows a badge if any file is missing embeddings).

**Available Operations**

1. Click **Download Template** to obtain the correct file layout (optional).
2. Click **Browse Files...** and select one or more `.xlsx` files.
3. Remove any unwanted file from the selection using its "×" button.
4. Click **Upload & Generate Embeddings**.
5. Resolve any duplicate-name conflicts using the modal that appears.
6. Review the Knowledge Base table to confirm the file was uploaded and embedded ("Ready" badge).
7. Use the "↻" button to re-embed a file if the "Missing" badge is shown, or the delete button to remove a file entirely.

**Related Screens**

- **AI Chatbot** — searches the files uploaded here.

**User Permissions**

No access restrictions — all users can upload, re-embed, and delete Knowledge Base files.

**Notes**

- The Knowledge Base table columns are: File Name, File Size (KB), Upload Date, Categories, Embeddings status ("Ready"/"Missing"), and Actions.
- Empty state message: "No files imported yet. Upload Excel files to get started."
- A warning banner listing affected file names is shown at the top of the page whenever one or more Knowledge Base files are missing embeddings.
- Deleting a file asks for confirmation: "Delete {filename}? This cannot be undone."

---

### 4.3 Preview

**Screen Purpose**

Lets a user assemble, review, and edit the Category → Task → Activity estimate before exporting it to Excel.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  [Project Name] [Created By]             |
|      |  [Remark editor]                         |
|      |  [Category/Task/Activity table]          |
|      |  [Add More/Back to Chatbot] [Clear All]  |
|      |  [Export Excel]                          |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | "Project Name" field | Required text field for the estimate's project name |
| 2 | "Created By" field | Required text field for the preparer's name |
| 3 | "Remark" rich-text editor | Formatting toolbar: Bold, Italic, Underline, Color, Bullet list, Numbered list, Undo, Redo |
| 4 | Category/Task/Activity table | Editable hierarchy with inline-editable fields (category name, task name, task remarks, buffer hours, activity name, activity hours) |
| 5 | "Add Category" button | Adds a new blank category |
| 6 | Per-task "Add Activity" button | Adds a new activity row under a task |
| 7 | Per-row "×" delete buttons | Removes a category, task, or activity |
| 8 | Collapse/expand toggle | Per task, to show or hide its activities |
| 9 | "Add More / Back to Chatbot" link | Returns to the AI Chatbot, keeping the current conversation |
| 10 | "Clear All" button | Clears all Preview data (client-side only, no server call) |
| 11 | "Export Excel" button | Submits the estimate for export; shows a spinner and is disabled while exporting |

**Validation Rules**

| Field | Rule |
|---|---|
| Project Name | Required to export; shows inline red validation text if left empty |
| Created By | Required to export; shows inline red validation text if left empty |
| Categories | At least one category with data is required to export |

**Navigation**

Reached via the sidebar **Preview** link, by clicking **Go to Preview** on the AI Chatbot screen, or by clicking **Restore to Preview** on the Temporary Data Detail screen.

**Available Operations**

1. Enter the **Project Name** and **Created By** values.
2. Optionally add a **Remark** using the rich-text editor.
3. Review, add, edit, or delete categories, tasks, and activities as needed.
4. Click **Export Excel** to generate and download the estimate file.
5. Alternatively, click **Add More / Back to Chatbot** to search for more items, or **Clear All** to start over.

**Related Screens**

- **AI Chatbot** — source of search results assembled here.
- **Temporary Data List/Detail** — unsaved Preview data may be automatically stashed here.
- **Exported Files** — the destination of a completed export.

**User Permissions**

No access restrictions — all users can assemble, edit, and export estimates.

**Notes**

- If the browser tab is closed, refreshed, or navigated away from (outside the application) while there is unsaved Preview data, it is automatically saved to Temporary Data.
- Attempting to export without a Project Name, Created By value, or any category data returns one of: "Project name is required.", "Created By is required.", or "No data to export."

---

### 4.4 Temporary Data List

**Screen Purpose**

Lists all in-progress Preview snapshots ("stashes") that were automatically saved to the server, so unsaved work can be found and restored.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  [From Date] [To Date] [Project Name]    |
|      |  [Search] [Reset]                        |
|      |  [Stash table]                           |
|      |  [Pagination]                            |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | "From Date" / "To Date" pickers | Filter stashes by the date they were created |
| 2 | "Project Name" field | Filter stashes by project name |
| 3 | "Search" button | Applies the selected filters |
| 4 | "Reset" button | Clears all filters |
| 5 | Stash table | Columns: Project Name, Created By, Created Date, Total Man Hour, Status, Action |
| 6 | "View" button (per row) | Opens the Temporary Data Detail screen for that stash |
| 7 | Pagination controls | 10 stashes per page, with page number links and previous/next |

**Validation Rules**

None (filter fields are optional).

**Navigation**

Reached via the **Temporary Data List** link in the sidebar, which shows a live badge with the current number of stashes.

**Available Operations**

1. Optionally set a date range and/or project name filter, then click **Search**.
2. Click **Reset** to clear filters.
3. Click **View** on a row to see the full stash detail.

**Related Screens**

- **Temporary Data Detail** — the destination when clicking "View".
- **Preview** — the source of stashed data, and the destination when a stash is restored.

**User Permissions**

No access restrictions. Note: because MHES has no login system, all stashes are shared across every user of the application, not scoped to an individual account.

**Notes**

- Status is always shown as "Pending".
- Empty state (no stashes exist): "No temporary data stashed. This fills up when you have Preview data and start a new session from the AI Chatbot nav link."
- Empty state (filters return nothing): "No stashes match the selected filters. Try adjusting the date range or project name, or reset the filters."
- Stashes older than a configured retention period are automatically deleted by a scheduled background job (see Section 8, Limitations, for the retention period).

---

### 4.5 Temporary Data Detail

**Screen Purpose**

Shows the full Category → Task → Activity breakdown of a single stashed Preview snapshot, and lets the user restore or discard it.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  Temporary Data > Detail (breadcrumb)    |
|      |  [Category/Task/Activity breakdown]      |
|      |  [Discard] [Restore to Preview]           |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | Breadcrumb | Temporary Data → Detail |
| 2 | Category/Task/Activity breakdown | Read-only display of the stashed estimate |
| 3 | "Discard" button | Permanently deletes the stash, after confirmation |
| 4 | "Restore to Preview" button | Merges the stash back into the active Preview screen and deletes the stash |

**Validation Rules**

None (read-only screen).

**Navigation**

Reached by clicking **View** on a row in the Temporary Data List screen.

**Available Operations**

1. Review the stashed estimate details.
2. Click **Restore to Preview** to bring the data back into the Preview screen for further editing, or
3. Click **Discard** to permanently delete the stash (confirmation: "Discard this stash? This cannot be undone.").

**Related Screens**

- **Temporary Data List** — where this screen is reached from and returned to.
- **Preview** — destination after restoring.

**User Permissions**

No access restrictions.

**Notes**

- If the stash no longer exists (e.g., already restored or discarded by another user in another tab), the message shown is: "This stash is no longer available. It may have already been restored or discarded." — and the user is redirected to the Temporary Data List with the flash message: "Temporary data not found. It may have already been restored or discarded."

---

### 4.6 Exported Files

**Screen Purpose**

Lists all previously exported estimate files (export history), with options to view or download each one.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  [From Date] [To Date] [Project Name]    |
|      |  [Search] [Reset]                        |
|      |  [Export history table]                  |
|      |  [Pagination]                             |
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | "From Date" / "To Date" pickers | Filter by export date |
| 2 | "Project Name" field | Filter by project name |
| 3 | "Search" / "Reset" buttons | Apply or clear filters |
| 4 | Export history table | Columns: Project Name, File Name, Created By, Export Date, Size (KB), Total Tasks, Total Hours, Actions |
| 5 | "View" button (eye icon, per row) | Opens the Export Detail screen |
| 6 | "Download" button (per row) | Downloads the exported `.xlsx` file |

**Validation Rules**

None (filter fields are optional).

**Navigation**

Reached via the **Exported File List** link in the sidebar.

**Available Operations**

1. Optionally set a date range and/or project name filter, then click **Search**.
2. Click **Reset** to clear filters.
3. Click **View** to review a file's contents on-screen, or **Download** to save it locally.

**Related Screens**

- **Export Detail** — the destination when clicking "View".
- **Preview** — the source of every exported file.

**User Permissions**

No access restrictions. Note: because MHES has no login system, export history is shared across every user of the application.

**Notes**

- If a file's underlying export is no longer available, a "Missing" badge is shown next to the File Name, and the View/Download actions are replaced with the text "Unavailable".
- Empty state (no exports exist): "No exported files yet. Generate your first report from the estimation summary."
- Empty state (filters return nothing): "No exports match the selected filters. Try adjusting the date range or project name, or reset the filters."

---

### 4.7 Export Detail

**Screen Purpose**

Shows a read-only, print-friendly view of a previously exported estimate.

**Screenshot Placeholder**

```
[Screen Image]
(Insert Screenshot Here)
```

**Screen Layout Diagram**

```
+------------------------------------------------+
| Header                                          |
+------------------------------------------------+
| Menu |  Project Information                    |
|      |  [Category/Task/Estimate/Remarks table] |
|      |  Remark section                          |
|      |  [Download Excel]
+------------------------------------------------+
| Footer                                          |
+------------------------------------------------+
```

**UI Components**

| No. | Component | Description |
|---|---|---|
| 1 | Project Information section | Project Name, Created By, Created Date |
| 2 | Selected Data table | Columns: Category, Task List, Estimate Hours, Working Day, Remarks, with a Total row |
| 3 | Remark section | Displays the rich-text remark saved with the export, including any hyperlinks |
| 4 | "Download Excel" button | Downloads the file |
| 5 | "Back to Export History" button | Returns to the Exported Files screen |

**Validation Rules**

None (read-only screen).

**Navigation**

Reached by clicking **View** on a row in the Exported Files screen.

**Available Operations**

1. Review the exported estimate details.
2. Click **Download Excel** to save the file.

**Related Screens**

- **Exported Files** — where this screen is reached from and returned to.

**User Permissions**

No access restrictions.

**Notes**

- This screen uses print-optimized formatting (A4 page size, navigation and buttons hidden when printed).
- If the file name is invalid or the underlying file cannot be read, the message shown is "File not found: {filename}" or "Could not open '{filename}' for viewing: {error}", and the user is redirected to the Exported Files list.

---

## 5. Business Operations

### 5.1 Uploading a Knowledge File

**Purpose:** Add historical man-hour estimation data to the system so it can be searched.

**Preconditions:** The user has an `.xlsx` file (10 MB or smaller) containing Category, Task, Activity/Detail, and Estimate columns.

**Procedure:**

1. Go to the **Upload Files** screen.
2. Click **Browse Files...** and select one or more `.xlsx` files.
3. Click **Upload & Generate Embeddings**.
4. If a file name already exists, choose **Auto-Rename** or **Overwrite** in the dialog that appears.
5. Wait for the confirmation message and check that the file's Embeddings badge shows "Ready".

**Expected Result:** The file appears in the Knowledge Base table with an embedding-ready status, and its data becomes searchable from the AI Chatbot.

**Error Cases:** See Section 6, Error Messages, for messages related to invalid file type, oversized files, or embedding failures.

**Notes:** Uploading does not overwrite the Knowledge Base unless "Overwrite" is chosen; the original file is otherwise never modified once stored.

---

### 5.2 Searching for Estimate Data

**Purpose:** Find historical man-hour data matching a described need.

**Preconditions:** At least one Knowledge Base file has been uploaded and embedded.

**Procedure:**

1. Go to the **AI Chatbot** screen.
2. Type a description of the work needed (e.g., a project, task, or activity name).
3. Click **Send** or press Enter.
4. Review the returned Category → Task → Activity results.

**Expected Result:** A results table appears, grouped by Category, Task, and Activity, with computed totals.

**Error Cases:** See Section 6, Error Messages.

**Notes:** Searching first checks for exact or partial name matches in the Knowledge Base, then falls back to AI semantic search if no direct match is found.

---

### 5.3 Assembling and Editing an Estimate

**Purpose:** Build a project estimate from search results, with the ability to make manual adjustments.

**Preconditions:** The user has performed a search on the AI Chatbot screen, or intends to build an estimate manually.

**Procedure:**

1. On the AI Chatbot screen, select the desired result rows using the checkboxes.
2. Click **Go to Preview (N selected)**.
3. On the Preview screen, enter the **Project Name** and **Created By** fields.
4. Optionally enter a **Remark**.
5. Edit any category, task, or activity field directly in the table, or use **Add Category** / **Add Activity** to add new rows.
6. Use the "×" buttons to remove any category, task, or activity no longer needed.

**Expected Result:** The Preview table reflects the assembled estimate, with totals recalculated automatically after each change.

**Error Cases:** See Section 6, Error Messages.

**Notes:** Clicking **Add More / Back to Chatbot** preserves the current Preview data and returns to the chat conversation to search for more items.

---

### 5.4 Exporting an Estimate to Excel

**Purpose:** Produce a formatted Excel file of the finished estimate for delivery or record-keeping.

**Preconditions:** The Preview screen has at least one category with data, and both Project Name and Created By are filled in.

**Procedure:**

1. On the Preview screen, click **Export Excel**.
2. Wait for the export to complete (a spinner is shown on the button).
3. The formatted Excel file downloads to the browser automatically.
4. Verify the completion message and check the **Exported Files** screen to confirm the new entry appears.

**Expected Result:** A `.xlsx` file is downloaded, and a corresponding entry appears in the Exported Files list.

**Error Cases:** See Section 6, Error Messages.

**Notes:** If the exported estimate contains any Category, Task, or Activity Detail not already present in the Knowledge Base, that data is automatically added to the Knowledge Base and indexed, so it becomes searchable in future queries.

---

### 5.5 Restoring or Discarding Temporary Data

**Purpose:** Recover Preview work that was automatically saved before it was lost (e.g., after closing the browser), or clean up unwanted backups.

**Preconditions:** At least one stash exists in the Temporary Data List.

**Procedure:**

1. Go to the **Temporary Data List** screen.
2. Optionally filter by date range or project name, then click **Search**.
3. Click **View** on the desired stash.
4. On the Temporary Data Detail screen, click **Restore to Preview** to bring the data back into an active estimate, or click **Discard** to permanently delete it.

**Expected Result:** If restored, the Preview screen opens with the stashed data merged in. If discarded, the stash is permanently removed from the list.

**Error Cases:** See Section 6, Error Messages.

**Notes:** Stashes are also removed automatically once they exceed the configured retention period (see Section 8, Limitations).

---

## 6. Error Messages

| Message | Cause | Solution |
|---|---|---|
| "Please enter a search query." | The Chatbot search box was submitted empty | Enter a search term before clicking Send |
| "Sorry, I couldn't find any matching results for your query. Try different keywords or check if knowledge files have been uploaded." | No Knowledge Base entry matched the search | Try different keywords, or upload relevant files on the Upload Files screen |
| "Failed to connect to the server. Please try again." | A network or server issue occurred during search | Check your connection and retry; contact an administrator if it persists |
| "Skipped invalid file(s) (only .xlsx is supported): ..." | A selected file was not an `.xlsx` file | Select only `.xlsx` files for upload |
| "No files selected." | The upload form was submitted with no file chosen | Select at least one file before uploading |
| "Skipped '{name}': invalid file type." | An invalid file type reached the server-side check | Re-select and upload a valid `.xlsx` file |
| "Failed to upload '{name}': {err}" | An error occurred while saving the uploaded file | Retry the upload; contact an administrator if it persists |
| "Uploaded '{name}' but embedding failed: {err}" | The file was saved, but the AI indexing step failed | Use the "↻" re-embed button on the Upload Files screen to retry indexing |
| "Delete {filename}? This cannot be undone." | Confirmation prompt shown before deleting a Knowledge Base file | Confirm only if certain; this action cannot be reversed |
| "Project name is required." | Export was attempted with no Project Name entered | Enter a Project Name on the Preview screen and try again |
| "Created By is required." | Export was attempted with no Created By value entered | Enter a Created By value on the Preview screen and try again |
| "No data to export." | Export was attempted with no category/task/activity data present | Add at least one category with data before exporting |
| "Discard this stash? This cannot be undone." | Confirmation prompt shown before discarding a Temporary Data stash | Confirm only if certain; this action cannot be reversed |
| "This stash is no longer available. It may have already been restored or discarded." | The stash was removed (restored, discarded, or expired) before this page loaded | Return to the Temporary Data List and select another entry |
| "Temporary data not found. It may have already been restored or discarded." | The requested stash no longer exists on the server | Return to the Temporary Data List; the stash may have already been handled |
| "File not found: {filename}" | The requested export file name was invalid or does not exist | Return to the Exported Files list and select a valid entry |
| "Could not open '{filename}' for viewing: {error}" | The exported file could not be read (e.g., storage issue) | Retry later, or contact an administrator if it persists |

---

## 7. Frequently Asked Questions (FAQ)

**Q: Do I need a username and password to use MHES?**
A: No. MHES currently has no login system. Anyone with access to the application URL can use all features.

**Q: What file format does MHES accept for the Knowledge Base?**
A: Only `.xlsx` (Excel) files, up to 10 MB each.

**Q: Why can't I find any results when I search?**
A: Either no Knowledge Base files have been uploaded and embedded yet, or the wording of your query doesn't match any Category, Task, or Activity name closely enough. Try different keywords, or check the Upload Files screen to confirm files are marked "Ready".

**Q: What happens to my Preview data if I accidentally close the browser tab?**
A: MHES automatically saves a backup ("stash") of your in-progress Preview data to the server. You can find and restore it from the Temporary Data List screen.

**Q: How long are Temporary Data stashes kept?**
A: They are automatically deleted after a configured retention period (see Section 8, Limitations, for the current value) via a scheduled cleanup job.

**Q: Can other people see my Preview stashes or exported files?**
A: Yes. Because MHES has no login system, Temporary Data stashes and export history are shared by everyone using the application, not private to an individual user.

**Q: Does exporting an estimate change the Knowledge Base?**
A: If the export contains any Category, Task, or Activity Detail not already in the Knowledge Base, that data is automatically added and indexed, so it can be found in future searches.

**Q: Can I edit an estimate after exporting it?**
A: Not directly. The Export Detail screen is read-only. To make changes, go back to Preview (or restore a related Temporary Data stash), edit as needed, and export again.

---

## 8. Limitations

### Known Limitations

- There is no login or user account system; all data (Knowledge Base, Temporary Data stashes, export history) is shared across all users of the application.
- The underlying AI language model (Ollama) integration is not yet active; the AI Chatbot currently uses structured semantic search only.
- Temporary Data stashes older than the configured retention period are automatically and permanently deleted; there is no way to recover a stash once it has been purged.
- Category names are not guaranteed to be unique across different Knowledge Base files.

### Unsupported Operations

- There is no in-browser editor for modifying Knowledge Base Excel data directly; files must be re-uploaded to make changes.
- There is no undo/redo history for edits made on the Preview screen.
- There is no drag-and-drop reordering of tasks or activities on the Preview screen.

### Browser Restrictions

(To Be Confirmed)

---

## 9. Appendix

### Glossary

See Section 1, Definitions.

### Abbreviations

| Abbreviation | Meaning |
|---|---|
| MHES | Man-Hour Estimation System |
| KB | Knowledge Base |
| AI | Artificial Intelligence |

### References

(To Be Confirmed)
