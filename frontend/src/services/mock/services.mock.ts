import {
  loansDb,
  exceptionsDb,
  aiRecommendationsDb,
  importJobsDb,
  auditLogsDb,
  reviewsDb,
  updateLoanInDb,
  updateExceptionInDb,
  addAuditLogToDb,
  addReviewToDb,
  addImportJobToDb
} from './db.mock';
import { Loan, Exception, AIRecommendation, ImportJob, AuditLog, DashboardSummary } from './types';

// Mock API Call delay simulation
const delay = (ms: number = 300) => new Promise((resolve) => setTimeout(resolve, ms));

export const getLoans = async (filters?: {
  status?: string;
  search?: string;
}): Promise<Loan[]> => {
  await delay();
  let result = [...loansDb];

  if (filters?.status) {
    result = result.filter((l) => l.verificationStatus === filters.status);
  }

  if (filters?.search) {
    const s = filters.search.toLowerCase();
    result = result.filter(
      (l) =>
        l.loanId.toLowerCase().includes(s) ||
        l.borrowerName.toLowerCase().includes(s) ||
        l.borrowerId.toLowerCase().includes(s)
    );
  }

  return result;
};

export const getLoanById = async (id: string): Promise<Loan | null> => {
  await delay();
  const loan = loansDb.find((l) => l.loanId === id);
  return loan || null;
};

export const getExceptions = async (filters?: {
  severity?: string;
  status?: string;
  search?: string;
}): Promise<Exception[]> => {
  await delay();
  let result = [...exceptionsDb];

  if (filters?.severity && filters.severity !== 'all') {
    const sev = filters.severity.toLowerCase();
    result = result.filter((e) => e.severity === sev);
  }

  if (filters?.status && filters.status !== 'all') {
    const stat = filters.status.toLowerCase();
    result = result.filter((e) => e.status === stat);
  }

  if (filters?.search) {
    const s = filters.search.toLowerCase();
    result = result.filter(
      (e) => e.loanId.toLowerCase().includes(s) || e.ruleName.toLowerCase().includes(s)
    );
  }

  return result;
};

export const getExceptionById = async (id: string): Promise<Exception | null> => {
  await delay();
  const exc = exceptionsDb.find((e) => e.id === id);
  return exc || null;
};

export const getAIRecommendationForException = async (
  exceptionId: string
): Promise<AIRecommendation | null> => {
  await delay();
  const rec = aiRecommendationsDb.find((r) => r.exceptionId === exceptionId);
  return rec || null;
};

export const getImportJobs = async (): Promise<ImportJob[]> => {
  await delay();
  return [...importJobsDb];
};

export const getAuditTrail = async (loanId: string): Promise<AuditLog[]> => {
  await delay();
  return auditLogsDb
    .filter((a) => a.loanId === loanId)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
};

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  await delay();
  const openExceptionsCount = exceptionsDb.filter((e) => e.status === 'open').length;
  const criticalExceptionsCount = exceptionsDb.filter(
    (e) => e.severity === 'critical' && e.status === 'open'
  ).length;

  return {
    totalRecords: 2000,
    validRecords: 1742,
    exceptionsCount: 258,
    criticalExceptionsCount: 43 + criticalExceptionsCount,
    qualityScore: 87.1,
    verificationRate: 68.5,
    pendingExceptions: openExceptionsCount,
    recordsReviewedToday: reviewsDb.length,
    approvedCount: reviewsDb.filter((r) => r.action === 'approve_verification').length,
    rejectedCount: reviewsDb.filter((r) => r.action === 'request_correction').length,
    correctionRequestsCount: reviewsDb.filter((r) => r.action === 'request_correction').length
  };
};

// User operations
export const performReviewAction = async (params: {
  loanId: string;
  exceptionId: string;
  action: 'approve_verification' | 'waive_exception' | 'request_correction' | 'edit_record';
  notes: string;
  reviewerName: string;
  updatedFields?: Record<string, any>;
}): Promise<void> => {
  await delay();

  const { loanId, exceptionId, action, notes, reviewerName, updatedFields } = params;

  // Add review entry
  addReviewToDb({
    loanId,
    reviewerId: '2',
    reviewerName,
    action,
    exceptionId,
    notes
  });

  // Calculate audit logs and perform updates
  if (action === 'edit_record' && updatedFields) {
    const loan = loansDb.find((l) => l.loanId === loanId);
    if (loan) {
      Object.keys(updatedFields).forEach((key) => {
        const prevValue = (loan as any)[key];
        const newValue = updatedFields[key];

        // Update Loan
        updateLoanInDb(loanId, { [key]: newValue });

        // Add Audit Log
        addAuditLogToDb({
          loanId,
          actor: reviewerName,
          action: 'FIELD_EDITED',
          entityType: 'Loan',
          changeSummary: `Reviewer edited field "${key}".`,
          diff: { field: key, before: prevValue, after: newValue }
        });
      });
    }
  } else if (action === 'waive_exception') {
    // Resolve Exception
    updateExceptionInDb(exceptionId, {
      status: 'waived',
      resolutionNote: notes,
      resolvedBy: reviewerName,
      resolvedAt: new Date().toISOString()
    });

    addAuditLogToDb({
      loanId,
      actor: reviewerName,
      action: 'EXCEPTION_WAIVED',
      entityType: 'Exception',
      changeSummary: `Exception resolved via waiver note: "${notes}".`
    });

    // Check if other open exceptions exist. If not, auto-transition loan status
    const remainingOpen = exceptionsDb.filter((e) => e.loanId === loanId && e.status === 'open' && e.id !== exceptionId);
    if (remainingOpen.length === 0) {
      updateLoanInDb(loanId, { verificationStatus: 'verified' });
      addAuditLogToDb({
        loanId,
        actor: reviewerName,
        action: 'LOAN_VERIFIED',
        entityType: 'VerifiedLoan',
        changeSummary: 'All exceptions resolved/waived. Loan verification approved.'
      });
    }
  } else if (action === 'approve_verification') {
    // Directly approve loan
    updateLoanInDb(loanId, { verificationStatus: 'verified' });
    updateExceptionInDb(exceptionId, {
      status: 'resolved',
      resolutionNote: notes,
      resolvedBy: reviewerName,
      resolvedAt: new Date().toISOString()
    });

    addAuditLogToDb({
      loanId,
      actor: reviewerName,
      action: 'LOAN_VERIFIED',
      entityType: 'VerifiedLoan',
      changeSummary: `Loan manually signed off and verified. Resolution: "${notes}".`
    });
  } else if (action === 'request_correction') {
    updateExceptionInDb(exceptionId, {
      status: 'investigating',
      resolutionNote: `Correction requested: ${notes}`
    });

    updateLoanInDb(loanId, { verificationStatus: 'exception' });

    addAuditLogToDb({
      loanId,
      actor: reviewerName,
      action: 'CORRECTION_REQUESTED',
      entityType: 'Exception',
      changeSummary: `Sent back to operator for correction. Instructions: "${notes}".`
    });
  }
};

// Ingest simulation
export const simulateUploadFile = async (
  fileName: string,
  fileType: 'loan_tape' | 'servicer_update' | 'document_manifest',
  uploadedBy: string,
  onProgress: (phase: string, percent: number) => void
): Promise<ImportJob> => {
  // Simulate standard parsing steps
  const steps = [
    { label: 'Parsing records from CSV...', pct: 20 },
    { label: 'Normalizing schema structures...', pct: 50 },
    { label: 'Running validation rule assertions...', pct: 80 },
    { label: 'Writing exception queue entries...', pct: 100 }
  ];

  for (const step of steps) {
    onProgress(step.label, step.pct);
    await delay(600);
  }

  // Create import statistics reflecting synthetic data
  const total = fileType === 'loan_tape' ? 2000 : fileType === 'servicer_update' ? 700 : 120;
  const failed = fileType === 'loan_tape' ? 18 : fileType === 'servicer_update' ? 2 : 0;
  const processed = total - failed;

  const newJob: Omit<ImportJob, 'id' | 'createdAt'> = {
    fileName,
    fileType,
    status: 'completed',
    totalRecords: total,
    processedRecords: processed,
    failedRecords: failed,
    uploadedBy
  };

  addImportJobToDb(newJob);

  // If it is a new loan tape, let's reset exceptions or add a new mock loan
  if (fileType === 'loan_tape') {
    // Add mock ingestion log in audit trail
    const demoId = `LN-200${Math.floor(10 + Math.random() * 90)}`;
    loansDb.push({
      loanId: demoId,
      borrowerName: 'Alice Smith',
      borrowerId: 'BR-47291',
      loanType: 'Residential Mortgage',
      originationDate: '2025-02-14',
      maturityDate: '2055-02-14',
      originalPrincipal: 250000,
      currentBalance: 248000,
      interestRate: 6.15,
      paymentStatus: 'CURRENT',
      dpd: 0,
      propertyState: 'FL',
      loanPurpose: 'Purchase',
      creditGrade: 'A',
      verificationStatus: 'unverified',
      servicerName: 'Apex Servicing Corp',
      lastUpdated: new Date().toISOString(),
      documents: []
    });

    addAuditLogToDb({
      loanId: demoId,
      actor: uploadedBy,
      action: 'RECORD_IMPORTED',
      entityType: 'Loan',
      changeSummary: `Loan uploaded via manual ingestion sheet: "${fileName}".`
    });
  }

  // Return the newly created job
  return importJobsDb[0];
};
