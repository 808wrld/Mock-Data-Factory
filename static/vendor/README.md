# Vendored front-end libraries

Served from `static/vendor/` instead of a CDN so the app keeps working when
jsDelivr is slow or unreachable (e.g. from mainland China), and so the exact
bytes are pinned in the repository. Files are copied unmodified from the
upstream release tags.

| Library         | Version | Source                                                        | Files                                         |
| --------------- | ------- | ------------------------------------------------------------- | --------------------------------------------- |
| Bootstrap       | 5.3.0   | https://github.com/twbs/bootstrap/tree/v5.3.0/dist            | `bootstrap.min.css`, `bootstrap.bundle.min.js` |
| Bootstrap Icons | 1.11.3  | https://github.com/twbs/icons/tree/v1.11.3/font               | `bootstrap-icons.min.css`, `fonts/*`          |
| SortableJS      | 1.15.2  | https://github.com/SortableJS/Sortable/tree/1.15.2            | `Sortable.min.js`                             |

All three are MIT licensed; each directory keeps the upstream `LICENSE`.

To upgrade, replace the files from the new release tag and update this table.
