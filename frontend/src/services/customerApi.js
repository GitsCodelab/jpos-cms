import api from './api'

const customerAPI = {
  /**
   * Search customers with optional filters.
   * At least one of q or nationalId is required.
   */
  search: (params) =>
    api.get('/customers', { params }),

  /**
   * Get full customer detail by ID.
   */
  getById: (customerId) =>
    api.get(`/customers/${customerId}`),

  /**
   * Get contracts for a customer.
   */
  getContracts: (customerId) =>
    api.get(`/customers/${customerId}/contracts`),

  /**
   * Get cards for a customer.
   * Pass { includePan: true } to request clear PAN (admin/operator only).
   */
  getCards: (customerId, options = {}) =>
    api.get(`/customers/${customerId}/cards`, {
      params: options.includePan ? { include_pan: true } : undefined,
    }),

  /**
   * Get accounts for a customer.
   * Balance field is null for viewer role (enforced by backend).
   */
  getAccounts: (customerId) =>
    api.get(`/customers/${customerId}/accounts`),

  /**
   * Get KYC documents for a customer.
   */
  getDocuments: (customerId) =>
    api.get(`/customers/${customerId}/documents`),

  /**
   * Get contacts for a customer.
   */
  getContacts: (customerId) =>
    api.get(`/customers/${customerId}/contacts`),
}

export default customerAPI
