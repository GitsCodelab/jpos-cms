import React from 'react'
import {
  UserOutlined,
  TeamOutlined,
  FileTextOutlined,
  CreditCardOutlined,
  ApartmentOutlined,
  BankOutlined,
  IdcardOutlined,
  SendOutlined,
  ToolOutlined,
  ExceptionOutlined,
  FormOutlined,
  ContainerOutlined,
  SettingOutlined,
  DollarOutlined,
  StopOutlined,
  SafetyOutlined,
  FileProtectOutlined,
  ShopOutlined,
  DesktopOutlined,
  FolderOutlined,
  TagsOutlined,
  AppstoreOutlined,
  MonitorOutlined,
  BellOutlined,
  ScheduleOutlined,
  FileSearchOutlined,
  AuditOutlined,
  BarChartOutlined,
  PieChartOutlined,
  ClusterOutlined,
  GlobalOutlined,
  ApiOutlined,
  DatabaseOutlined,
  CalendarOutlined,
  RetweetOutlined,
  SyncOutlined,
  RiseOutlined,
  TagOutlined,
  CustomerServiceOutlined,
  DashboardOutlined,
  FileOutlined,
  BookOutlined,
  OrderedListOutlined,
  TransactionOutlined,
  ReconciliationOutlined,
  BranchesOutlined,
  ThunderboltOutlined,
  QuestionCircleOutlined,
  NotificationOutlined,
  InboxOutlined,
  BugOutlined,
  CrownOutlined,
  LockOutlined,
  PhoneOutlined,
  AppstoreAddOutlined,
  ProfileOutlined,
  CheckSquareOutlined,
  FundOutlined,
  SlidersOutlined,
  UnorderedListOutlined,
  BlockOutlined,
} from '@ant-design/icons'

/**
 * Enterprise sidebar navigation configuration.
 *
 * Each item:
 *   key        – unique string; leaf items must start with '/' (used as route path)
 *   label      – display name
 *   icon       – React element (Ant Design icon)
 *   permission – permission key for future RBAC
 *   children   – optional nested items array
 */
const menuConfig = [


  // ── Issuing ────────────────────────────────────────────────────
  {
    key: 'issuing',
    label: 'Issuing',
    icon: <CreditCardOutlined />,
    permission: 'issuing',
    children: [
      { key: '/customers', label: 'Customers', icon: <TeamOutlined />, permission: 'customers.list' },
      { key: '/issuing/hierarchy',             label: 'Hierarchy',             icon: <ApartmentOutlined />,  permission: 'issuing.hierarchy' },
      { key: '/issuing/accounts',              label: 'Accounts',              icon: <BankOutlined />,       permission: 'issuing.accounts' },
      { key: '/issuing/cards',                 label: 'Cards',                 icon: <CreditCardOutlined />, permission: 'issuing.cards' },
      { key: '/issuing/cardholders',           label: 'Cardholders',           icon: <IdcardOutlined />,     permission: 'issuing.cardholders' },
      { key: '/issuing/delivery',              label: 'Delivery',              icon: <SendOutlined />,       permission: 'issuing.delivery' },
      { key: '/issuing/operations',            label: 'Operations',            icon: <ToolOutlined />,       permission: 'issuing.operations' },
      { key: '/issuing/operational-requests',  label: 'Operational requests',  icon: <FormOutlined />,       permission: 'issuing.operational_requests' },
      { key: '/issuing/dispute-operations',    label: 'Dispute operations',    icon: <ExceptionOutlined />,  permission: 'issuing.dispute_operations' },
      { key: '/issuing/applications',          label: 'Applications',          icon: <ContainerOutlined />,  permission: 'issuing.applications' },
      {
        key: 'issuing-credit',
        label: 'Credit',
        icon: <DollarOutlined />,
        permission: 'issuing.credit',
        children: [
          { key: '/issuing/credit/blacklist', label: 'Black list', icon: <StopOutlined />, permission: 'issuing.credit.blacklist' },
        ],
      },
      {
        key: 'issuing-disputes',
        label: 'Disputes',
        icon: <ExceptionOutlined />,
        permission: 'issuing.disputes',
        children: [
          { key: '/issuing/disputes', label: 'Disputes', icon: <ExceptionOutlined />, permission: 'issuing.disputes.list' },
        ],
      },
      {
        key: 'issuing-loyalty',
        label: 'Loyalty',
        icon: <TagOutlined />,
        permission: 'issuing.loyalty',
        children: [
          { key: '/issuing/loyalty', label: 'Loyalty', icon: <TagOutlined />, permission: 'issuing.loyalty.list' },
        ],
      },
      {
        key: 'issuing-emv',
        label: 'EMV',
        icon: <SafetyOutlined />,
        permission: 'issuing.emv',
        children: [
          { key: '/issuing/emv/documents', label: 'Documents', icon: <FileProtectOutlined />, permission: 'issuing.emv.documents' },
        ],
      },
    ],
  },

  // ── Acquiring ──────────────────────────────────────────────────
  {
    key: 'acquiring',
    label: 'Acquiring',
    icon: <ShopOutlined />,
    permission: 'acquiring',
    children: [
      { key: '/acquiring/hierarchy',          label: 'Hierarchy',          icon: <ApartmentOutlined />, permission: 'acquiring.hierarchy' },
      { key: '/acquiring/accounts',           label: 'Accounts',           icon: <BankOutlined />,      permission: 'acquiring.accounts' },
      { key: '/acquiring/merchants',          label: 'Merchants',          icon: <ShopOutlined />,      permission: 'acquiring.merchants' },
      { key: '/acquiring/terminals',          label: 'Terminals',          icon: <DesktopOutlined />,   permission: 'acquiring.terminals' },
      { key: '/acquiring/operations',         label: 'Operations',         icon: <ToolOutlined />,      permission: 'acquiring.operations' },
      { key: '/acquiring/dispute-operations', label: 'Dispute operations', icon: <ExceptionOutlined />, permission: 'acquiring.dispute_operations' },
      { key: '/acquiring/applications',       label: 'Applications',       icon: <ContainerOutlined />, permission: 'acquiring.applications' },
      {
        key: 'acquiring-configuration',
        label: 'Configuration',
        icon: <SettingOutlined />,
        permission: 'acquiring.configuration',
        children: [
          { key: '/acquiring/configuration', label: 'Configuration', icon: <SettingOutlined />, permission: 'acquiring.configuration.list' },
        ],
      },
      {
        key: 'acquiring-disputes',
        label: 'Disputes',
        icon: <ExceptionOutlined />,
        permission: 'acquiring.disputes',
        children: [
          { key: '/acquiring/disputes/vouchers',    label: 'Vouchers batches',        icon: <FolderOutlined />,   permission: 'acquiring.disputes.vouchers' },
          { key: '/acquiring/disputes/invoices',    label: 'Invoices',                icon: <FileTextOutlined />, permission: 'acquiring.disputes.invoices' },
          { key: '/acquiring/disputes/mcc-groups',  label: 'MCC redefinition groups', icon: <TagsOutlined />,     permission: 'acquiring.disputes.mcc_groups' },
          { key: '/acquiring/disputes/companies',   label: 'Companies',               icon: <BankOutlined />,     permission: 'acquiring.disputes.companies' },
        ],
      },
    ],
  },

  // ── Operational Rules ──────────────────────────────────────────
  {
    key: 'operational-rules',
    label: 'Operational Rules',
    icon: <BookOutlined />,
    permission: 'operational_rules',
    children: [
      { key: '/operational-rules/accounting',   label: 'Accounting',   icon: <DollarOutlined />,    permission: 'operational_rules.accounting' },
      { key: '/operational-rules/processing',   label: 'Processing',   icon: <SyncOutlined />,      permission: 'operational_rules.processing' },
      { key: '/operational-rules/authorization',label: 'Authorization', icon: <SafetyOutlined />,   permission: 'operational_rules.authorization' },
      { key: '/operational-rules/naming',       label: 'Naming',       icon: <TagsOutlined />,      permission: 'operational_rules.naming' },
      { key: '/operational-rules/events',       label: 'Events',       icon: <BellOutlined />,      permission: 'operational_rules.events' },
      { key: '/operational-rules/matching',     label: 'Matching',     icon: <CheckSquareOutlined />, permission: 'operational_rules.matching' },
      { key: '/operational-rules/modifiers',    label: 'Modifiers',    icon: <SlidersOutlined />,   permission: 'operational_rules.modifiers' },
      { key: '/operational-rules/checks',       label: 'Checks',       icon: <FileProtectOutlined />, permission: 'operational_rules.checks' },
      { key: '/operational-rules/disputes',     label: 'Disputes',     icon: <ExceptionOutlined />, permission: 'operational_rules.disputes' },
    ],
  },

  // ── Payment Orders ─────────────────────────────────────────────
  {
    key: 'payment-orders',
    label: 'Payment Orders',
    icon: <OrderedListOutlined />,
    permission: 'payment_orders',
    children: [
      { key: '/payment-orders/services',          label: 'Services',          icon: <ApiOutlined />,        permission: 'payment_orders.services' },
      { key: '/payment-orders/service-providers', label: 'Service providers', icon: <CustomerServiceOutlined />, permission: 'payment_orders.service_providers' },
      { key: '/payment-orders/parameters',        label: 'Parameters',        icon: <SlidersOutlined />,    permission: 'payment_orders.parameters' },
      { key: '/payment-orders/applications',      label: 'Applications',      icon: <ContainerOutlined />,  permission: 'payment_orders.applications' },
      { key: '/payment-orders/orders',            label: 'Orders',            icon: <OrderedListOutlined />, permission: 'payment_orders.orders' },
    ],
  },

  // ── Payment System ─────────────────────────────────────────────
  {
    key: 'payment-system',
    label: 'Payment System',
    icon: <TransactionOutlined />,
    permission: 'payment_system',
    children: [
      { key: '/payment-system/mastercard',    label: 'MasterCard',       icon: <CreditCardOutlined />, permission: 'payment_system.mastercard' },
      { key: '/payment-system/visa',          label: 'VISA',             icon: <CreditCardOutlined />, permission: 'payment_system.visa' },
      { key: '/payment-system/cup',           label: 'China Union Pay',  icon: <CreditCardOutlined />, permission: 'payment_system.cup' },
      { key: '/payment-system/amex',          label: 'American Express', icon: <CreditCardOutlined />, permission: 'payment_system.amex' },
      { key: '/payment-system/jcb',           label: 'Japan Credit Bureau', icon: <CreditCardOutlined />, permission: 'payment_system.jcb' },
      { key: '/payment-system/mir',           label: 'MIR',              icon: <CreditCardOutlined />, permission: 'payment_system.mir' },
      { key: '/payment-system/nbc',           label: 'NBC',              icon: <BankOutlined />,       permission: 'payment_system.nbc' },
      { key: '/payment-system/meeza',         label: 'Meeza',            icon: <CreditCardOutlined />, permission: 'payment_system.meeza' },
      { key: '/payment-system/reconciliation',label: 'Reconciliation',   icon: <ReconciliationOutlined />, permission: 'payment_system.reconciliation' },
      { key: '/payment-system/swift',         label: 'SWIFT',            icon: <GlobalOutlined />,     permission: 'payment_system.swift' },
      { key: '/payment-system/diners',        label: 'Diners Club',      icon: <CreditCardOutlined />, permission: 'payment_system.diners' },
      { key: '/payment-system/gim',           label: 'GIM',              icon: <BankOutlined />,       permission: 'payment_system.gim' },
    ],
  },



  // ── Monitoring ─────────────────────────────────────────────────
  {
    key: 'monitoring',
    label: 'Monitoring',
    icon: <MonitorOutlined />,
    permission: 'monitoring',
    children: [
      { key: '/monitoring/notifications',    label: 'Notifications',    icon: <BellOutlined />,       permission: 'monitoring.notifications' },
      { key: '/monitoring/process-files',    label: 'Process files',    icon: <FileOutlined />,       permission: 'monitoring.process_files' },
      { key: '/monitoring/process-schedule', label: 'Process Schedule', icon: <ScheduleOutlined />,   permission: 'monitoring.process_schedule' },
      { key: '/monitoring/configuration',    label: 'Configuration',    icon: <SettingOutlined />,    permission: 'monitoring.configuration' },
      { key: '/monitoring/process-logs',     label: 'Process logs',     icon: <FileSearchOutlined />, permission: 'monitoring.process_logs' },
      { key: '/monitoring/audit-logs',       label: 'Audit logs',       icon: <AuditOutlined />,      permission: 'monitoring.audit_logs' },
      { key: '/monitoring/report-runs',      label: 'Report runs',      icon: <BarChartOutlined />,   permission: 'monitoring.report_runs' },
      { key: '/monitoring/user-sessions',    label: 'User sessions',    icon: <TeamOutlined />,       permission: 'monitoring.user_sessions' },
      { key: '/monitoring/atm-monitoring',   label: 'ATM monitoring',   icon: <DesktopOutlined />,    permission: 'monitoring.atm_monitoring' },
      {
        key: 'monitoring-mis',
        label: 'MIS',
        icon: <PieChartOutlined />,
        permission: 'monitoring.mis',
        children: [
          { key: '/monitoring/mis', label: 'MIS', icon: <PieChartOutlined />, permission: 'monitoring.mis.list' },
        ],
      },
    ],
  },

  // ── Reconciliation ─────────────────────────────────────────────
  {
    key: 'reconciliation',
    label: 'Reconciliation',
    icon: <ReconciliationOutlined />,
    permission: 'reconciliation',
    children: [
      { key: '/reconciliation/cbs',              label: 'CBS',              icon: <DatabaseOutlined />,      permission: 'reconciliation.cbs' },
      { key: '/reconciliation/atm',              label: 'ATM',              icon: <DesktopOutlined />,       permission: 'reconciliation.atm' },
      { key: '/reconciliation/host',             label: 'Host',             icon: <ClusterOutlined />,       permission: 'reconciliation.host' },
      { key: '/reconciliation/service-provider', label: 'Service provider', icon: <CustomerServiceOutlined />, permission: 'reconciliation.service_provider' },
    ],
  },

  // ── Routing ────────────────────────────────────────────────────
  {
    key: 'routing',
    label: 'Routing',
    icon: <BranchesOutlined />,
    permission: 'routing',
    children: [
      { key: '/routing/operations', label: 'Operations', icon: <ToolOutlined />, permission: 'routing.operations' },
    ],
  },



  // ── Campaigns ──────────────────────────────────────────────────
  {
    key: 'campaigns',
    label: 'Campaigns',
    icon: <NotificationOutlined />,
    permission: 'campaigns',
    children: [
      { key: '/campaigns/campaigns',       label: 'Campaigns',       icon: <NotificationOutlined />, permission: 'campaigns.list' },
      { key: '/campaigns/promo-campaigns', label: 'Promo campaigns', icon: <TagOutlined />,          permission: 'campaigns.promo' },
      { key: '/campaigns/applications',    label: 'Applications',    icon: <ContainerOutlined />,    permission: 'campaigns.applications' },
    ],
  },


  // ── Fraud Prevention ───────────────────────────────────────────
  {
    key: 'fraud-prevention',
    label: 'Fraud Prevention',
    icon: <BugOutlined />,
    permission: 'fraud_prevention',
    children: [
      { key: '/fraud-prevention/suites',               label: 'Suites',               icon: <AppstoreAddOutlined />, permission: 'fraud_prevention.suites' },
      { key: '/fraud-prevention/cases',                label: 'Cases',                icon: <FolderOutlined />,      permission: 'fraud_prevention.cases' },
      { key: '/fraud-prevention/matrices',             label: 'Matrices',             icon: <BlockOutlined />,       permission: 'fraud_prevention.matrices' },
      { key: '/fraud-prevention/alerts',               label: 'Fraud alerts',         icon: <BellOutlined />,        permission: 'fraud_prevention.alerts' },
      { key: '/fraud-prevention/alert-monitoring',     label: 'Fraud alert monitoring', icon: <MonitorOutlined />,   permission: 'fraud_prevention.alert_monitoring' },
    ],
  },

  // ── Structure ──────────────────────────────────────────────────
  {
    key: 'structure',
    label: 'Structure',
    icon: <ClusterOutlined />,
    permission: 'structure',
    children: [
      { key: '/structure/bank-organization', label: 'Bank organization', icon: <BankOutlined />,   permission: 'structure.bank_organization' },
      { key: '/structure/networks',          label: 'Networks',          icon: <GlobalOutlined />, permission: 'structure.networks' },
    ],
  },

 
  // ── Administration ─────────────────────────────────────────────
  {
    key: 'administration',
    label: 'Administration',
    icon: <CrownOutlined />,
    permission: 'administration',
    children: [
      { key: '/administration/processes',    label: 'Processes',    icon: <SyncOutlined />,          permission: 'administration.processes' },
      { key: '/administration/permissions',  label: 'Permissions',  icon: <LockOutlined />,          permission: 'administration.permissions' },
      { key: '/administration/communication',label: 'Communication',icon: <PhoneOutlined />,         permission: 'administration.communication' },
      { key: '/administration/security',     label: 'Security',     icon: <SafetyOutlined />,        permission: 'administration.security' },
      { key: '/administration/interface',    label: 'Interface',    icon: <DesktopOutlined />,       permission: 'administration.interface' },
      { key: '/administration/settings',     label: 'Settings',     icon: <SettingOutlined />,       permission: 'administration.settings' },
    ],
  },

  // ── Configuration ──────────────────────────────────────────────
  {
    key: 'configuration',
    label: 'Configuration',
    icon: <SettingOutlined />,
    permission: 'configuration',
    children: [
      { key: '/configuration/calendar',      label: 'Calendar',      icon: <CalendarOutlined />,       permission: 'configuration.calendar' },
      { key: '/configuration/fees',          label: 'Fees',          icon: <DollarOutlined />,         permission: 'configuration.fees' },
      { key: '/configuration/limits',        label: 'Limits',        icon: <DashboardOutlined />,      permission: 'configuration.limits' },
      { key: '/configuration/converters',    label: 'Converters',    icon: <RetweetOutlined />,        permission: 'configuration.converters' },
      { key: '/configuration/cycles',        label: 'Cycles',        icon: <SyncOutlined />,           permission: 'configuration.cycles' },
      { key: '/configuration/rates',         label: 'Rates',         icon: <RiseOutlined />,           permission: 'configuration.rates' },
      { key: '/configuration/card-types',    label: 'Card types',    icon: <CreditCardOutlined />,     permission: 'configuration.card_types' },
      { key: '/configuration/notification',  label: 'Notification',  icon: <BellOutlined />,           permission: 'configuration.notification' },
      { key: '/configuration/reporting',     label: 'Reporting',     icon: <BarChartOutlined />,       permission: 'configuration.reporting' },
      { key: '/configuration/scoring',       label: 'Scoring',       icon: <FundOutlined />,           permission: 'configuration.scoring' },
      { key: '/configuration/database-connections', label: 'Database Connections', icon: <DatabaseOutlined />, permission: 'configuration.database_connections' },
      {
        key: 'configuration-directory',
        label: 'Directory',
        icon: <FolderOutlined />,
        permission: 'configuration.directory',
        children: [
          { key: '/configuration/directory/flexible-fields', label: 'Flexible fields', icon: <FormOutlined />, permission: 'configuration.directory.flexible_fields' },
        ],
      },
      {
        key: 'configuration-applications',
        label: 'Applications',
        icon: <ContainerOutlined />,
        permission: 'configuration.applications',
        children: [
          { key: '/configuration/applications/validation', label: 'Configuration validation', icon: <CheckSquareOutlined />, permission: 'configuration.applications.validation' },
        ],
      },
    ],
  },
]

export default menuConfig

/**
 * Recursively flattens the menu tree to a list of leaf items (items with route paths).
 * Used by Search and Bookmarks tabs.
 */
export const flattenMenuItems = (items = menuConfig, result = []) => {
  items.forEach((item) => {
    if (item.children && item.children.length > 0) {
      flattenMenuItems(item.children, result)
    } else if (item.key.startsWith('/')) {
      result.push(item)
    }
  })
  return result
}

/**
 * Finds all ancestor keys for a given route key (used to auto-open parent menus).
 */
export const findAncestorKeys = (items, targetKey, ancestors = []) => {
  for (const item of items) {
    if (item.key === targetKey) return ancestors
    if (item.children) {
      const found = findAncestorKeys(item.children, targetKey, [...ancestors, item.key])
      if (found) return found
    }
  }
  return null
}
