/**
 * Anonymous Prototype Patient Session Identifier Utility for PCIF Day 10.
 *
 * Provides an anonymous, opaque prototype session identifier stored exclusively in sessionStorage.
 * Reused across Nutrition AI and Mental Wellness AI pages within the active browser session.
 *
 * IMPORTANT DISCLAIMER:
 * This session identifier is not authentication and does not establish verified patient identity.
 * It will later be replaced by an authenticated application-level patient ID.
 */

const SESSION_KEY = 'pcif_patient_session_id';

/**
 * Retrieves the existing patient session ID from sessionStorage, or generates a new opaque UUID
 * if one does not exist for the current browser session.
 *
 * @returns {string} Opaque patient session ID (e.g. "pcif_demo_7b5a8c1d-...")
 */
export function getOrCreatePatientSessionId() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    // Non-browser or SSR fallback
    return 'pcif_demo_fallback_session';
  }

  try {
    let sessionId = window.sessionStorage.getItem(SESSION_KEY);
    if (!sessionId || typeof sessionId !== 'string' || !sessionId.trim()) {
      const rawUuid = typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : 'fallback-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);
      
      sessionId = `pcif_demo_${rawUuid}`;
      window.sessionStorage.setItem(SESSION_KEY, sessionId);
    }
    return sessionId;
  } catch (err) {
    console.warn('[PCIF Session] Unable to access sessionStorage:', err);
    return 'pcif_demo_transient_session';
  }
}
