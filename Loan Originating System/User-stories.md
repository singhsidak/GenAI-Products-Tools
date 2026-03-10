### Epic 1: Frictionless Borrower Intake

**Objective:** Capture borrower data and financial history with zero redundant manual entry.

*   **Story 1.1: Conversational Application Flow**
    
    *   **As a** Borrower,
        
    *   **I want to** apply for a loan using a dynamic, chat-like interface
        
    *   **So that** I only have to answer questions relevant to my specific business type and avoid a 50-field static form.
        
    *   _Acceptance Criteria:_
        
        *   UI presents questions one at a time or in small logical chunks.
            
        *   Logic tree: If "Sole Proprietor" is selected, the system bypasses "Corporate Board" questions.
            
        *   Session automatically saves progress so the user can resume later without data loss.
            
*   **Story 1.2: Identity Verification (KYC/KYB)**
    
    *   **As a** Risk Officer,
        
    *   **I want** the borrower to upload their ID and take a live selfie
        
    *   **So that** the system can instantly verify their identity and ensure they are a real person.
        
    *   _Acceptance Criteria:_
        
        *   Integrate mobile camera/webcam UI for live capture.
            
        *   AI performs liveness detection (anti-spoofing).
            
        *   System extracts Name, DOB, and Address via OCR and matches the selfie to the ID photo with >98% confidence.
            
*   **Story 1.3: Open Banking / Financial Sync**
    
    *   **As a** Borrower,
        
    *   **I want to** securely connect my business bank account via a third-party provider (e.g., Plaid)
        
    *   **So that** my financial history is securely shared without me needing to manually type out my revenue and expenses.
        
    *   _Acceptance Criteria:_
        
        *   Embedded Plaid/Account Aggregator widget in the UI.
            
        *   System securely fetches 12 months of transaction history upon successful login.
            
        *   A "Magic" loading screen displays progress ("Analyzing cash flow...") while data is pulled.
            

### Epic 2: Intelligent Document Processing (IDP) & Fraud Check

**Objective:** Automate the ingestion, extraction, and validation of unstructured documents.

*   **Story 2.1: Dynamic Document Uploads**
    
    *   **As a** Borrower,
        
    *   **I want the** system to only ask me for documents that couldn't be fetched via my bank connection
        
    *   **So that** my manual upload burden is minimized.
        
    *   _Acceptance Criteria:_
        
        *   System checks missing data fields after API sync.
            
        *   Drag-and-drop UI prompts the user _only_ for missing files (e.g., "Please upload your 2024 Tax Return").
            
*   **Story 2.2: Multi-Modal Data Extraction**
    
    *   **As an** Underwriter,
        
    *   **I want** the AI to automatically read uploaded PDFs and JPEGs
        
    *   **So that** key financial data (Net Income, EIN) is automatically populated into the LOS database without manual typing.
        
    *   _Acceptance Criteria:_
        
        *   Vision-Language Model (VLM) extracts key-value pairs from Tax Returns and Bank Statements.
            
        *   Achieves >95% extraction accuracy.
            
        *   Unreadable or highly blurry documents are flagged for user re-upload or manual underwriter review.
            
*   **Story 2.3: Document Tampering & Fraud Detection**
    
    *   **As a** Risk Officer,
        
    *   **I want** the AI to analyze the metadata and visual layers of uploaded documents
        
    *   **So that** forged or photoshopped bank statements are caught before underwriting begins.
        
    *   _Acceptance Criteria:_
        
        *   AI evaluates documents for digital manipulation (e.g., irregular pixel compression, altered metadata).
            
        *   Assigns a "Tamper Probability Score."
            
        *   If score > 15%, the loan is hard-stopped and routed to the Fraud Queue.
            

### Epic 3: AI Decision Engine & Alternative Underwriting

**Objective:** Provide instant, Straight-Through Processing (STP) decisions using cash-flow AI.

*   **Story 3.1: Cash-Flow Risk Scoring Model**
    
    *   **As a** Lender,
        
    *   **I want** the ML engine to evaluate daily bank balances, NSF fees, and revenue trends
        
    *   **So that** the system can accurately assess the creditworthiness of "thin-file" borrowers who lack traditional credit scores.
        
    *   _Acceptance Criteria:_
        
        *   Engine ingests Plaid transaction data and traditional bureau data.
            
        *   Outputs a proprietary "LoanMatrix Health Score" (0-1000).
            
        *   Model executes and returns a score in < 5 seconds.
            
*   **Story 3.2: Automated Decision Routing (STP)**
    
    *   **As a** Borrower,
        
    *   **I want** to receive an instant decision on my application
        
    *   **So that** I know immediately if I am approved, declined, or need manual review.
        
    *   _Acceptance Criteria:_
        
        *   Rules engine routes based on the LoanMatrix Health Score: Auto-Approve, Auto-Decline, or Refer.
            
        *   If Auto-Approved, UI immediately presents confetti animation and risk-based pricing offers.
            
*   **Story 3.3: Risk-Based Offer Selection & E-Sign**
    
    *   **As a** Borrower ,
        
    *   **I want to** view multiple loan options (e.g., Term Loan vs. Line of Credit) and e-sign my contract
        
    *   **So that** I can choose the terms that fit my business and finalize the loan.
        
    *   _Acceptance Criteria:_
        
        *   System displays up to 3 dynamic offers based on the approved risk tier.
            
        *   User selects an offer, which triggers an embedded DocuSign/HelloSign contract.
            
        *   Upon signature, system queues the loan for API funding disbursement.
            

### Epic 4: Underwriter Copilot (For "Referred" Loans)

**Objective:** Supercharge the human underwriter with AI synthesis and traceable insights.

*   **Story 4.1: Prioritized Underwriter Dashboard**
    
    *   **As an** Underwriter,
        
    *   **I want to** see a prioritized list of "Referred" applications
        
    *   **So that** I know which files require my attention based on SLA wait times.
        
    *   _Acceptance Criteria:_
        
        *   Kanban or list view UI showing Applicant Name, Requested Amount, and Time in Queue.
            
        *   Ability to click into a profile to view the split-screen workspace.
            
*   **Story 4.2: Auto-Generated AI Credit Memo with Traceability**
    
    *   **As an** Underwriter,
        
    *   **I want** the AI to draft a narrative Credit Memo based on the borrower's data
        
    *   **So that** I don't have to spend 2 hours writing a summary from scratch.
        
    *   _Acceptance Criteria:_
        
        *   LLM generates a 3-5 page rich-text summary (Business Overview, Financial Health, Risks).
            
        *   **Traceability (Crucial):** Hovering over any AI-generated financial number reveals a tool-tip displaying a visual snippet of the exact source document the number was pulled from.
            
        *   Text is fully editable by the underwriter.
            
*   **Story 4.3: AI Risk Highlighting & Alerts**
    
    *   **As an** Underwriter,
        
    *   **I want** the system to explicitly flag financial anomalies or risks
        
    *   **So that** I don't miss critical issues buried in the transaction data.
        
    *   _Acceptance Criteria:_
        
        *   UI displays an "Alerts" panel.
            
        *   Flags specific ML findings (e.g., ⚠️ _Red Flag: Top 2 clients account for 85% of revenue_).
            
*   **Story 4.4: Final Decision Modal**
    
    *   **As an** Underwriter,
        
    *   **I want** a dedicated modal to log my final decision
        
    *   **So that** I can finalize the loan terms or officially document my decline reasons.
        
    *   _Acceptance Criteria:_
        
        *   Modal includes buttons: \[Approve\],\[Decline\], \[Request More Info\].
            
        *   If Approved: Underwriter inputs final rate and amount.
            
        *   If Declined: Underwriter must select standard decline reason codes from a dropdown.
            

### Epic 5: Compliance & Explainable AI (XAI)

**Objective:** Ensure the AI is legally compliant, transparent, and unbiased.

*   **Story 5.1: Explainable AI (SHAP) Audit Logging**
    
    *   **As a** Compliance Officer,
        
    *   **I want** the system to log the mathematical reasons for every AI-generated decision
        
    *   **So that** the ML model is not a "black box" during regulatory audits.
        
    *   _Acceptance Criteria:_
        
        *   System stores SHAP (SHapley Additive exPlanations) values for every decision.
            
        *   UI displays a bar chart showing the top positive and negative variables impacting the specific LoanMatrix Health Score.
            
*   **Story 5.2: Automated Adverse Action Generation**
    
    *   **As a** Compliance Officer,
        
    *   **I want** the system to automatically map AI decline reasons to legally compliant ECOA letters
        
    *   **So that** declined borrowers legally understand why they were rejected without manual ops intervention.
        
    *   _Acceptance Criteria:_
        
        *   System maps top 3 negative SHAP values to standard FCRA/ECOA reason codes.
            
        *   Auto-generates a PDF Adverse Action Notice and emails it to the borrower.
            
*   **Story 5.3: Disparate Impact & Bias Dashboard**
    
    *   **As a** Compliance Officer ,
        
    *   **I want** to view real-time portfolio approval rates sliced by demographic proxies
        
    *   **So that** I can ensure the AI is not unintentionally discriminating against protected classes.
        
    *   _Acceptance Criteria:_
        
        *   Dashboard visualizing approval/decline ratios.
            
        *   Ability to filter by geographic region, estimated gender, or business type.
            
*   **Story 5.4: Dynamic Rules & Threshold Management**
    
    *   **As a** Risk Admin,
        
    *   **I want** to easily adjust the AI's auto-approval/decline thresholds via a UI
        
    *   **So that** I can tighten or loosen our lending criteria instantly based on macroeconomic conditions.
        
    *   _Acceptance Criteria:_
        
        *   Admin UI with slider bars for "Minimum Score for Auto-Approval."
            
        *   Changes require dual-approval (Maker-Checker workflow) before pushing to production.