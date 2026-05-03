# Phase 06 - Tasks - Customer Management Enhencement

# in progress task


# closed tasks
* [x] customer search page
  * [x] customer search page show 100 customers — `PAGE_SIZE = 100` in frontend, `Query(100)` default in router
  * [x] remove quick view — removed `EyeOutlined` drawer button; drawer removed from `Customers.jsx`
  * [x] make "open full page" open as modal windows — row click and `ExpandOutlined` button open `CustomerDetail` in a maximized `Modal` (98% width, maximize/restore toggle); `isModal` prop hides breadcrumb/Back button
  * [x] show pan button: make it as icon beside the pan — eye icon rendered inline in each card row cell; `card_number_clear` fetched upfront with `include_pan=true`; icon only shown when backend returns clear PAN (admin/operator role); per-row toggle (red `EyeInvisibleOutlined` when revealed)
