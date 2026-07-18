---
name: customer-support
description: Answer order questions and prepare customer-support actions when a user asks for help with an order.
asxp-version: 0.1
version: 1.0.0
id: asxp://example.org/customer-support
publisher: example.org
license: Apache-2.0
permissions: orders.read
privacy: local
ae-tools-json: '[{"name":"lookup_order","description":"Look up an order by its public order identifier.","kind":"function","inputSchema":{"type":"object","properties":{"order_id":{"type":"string"}},"required":["order_id"],"additionalProperties":false},"permissions":["orders.read"]}]'
---

# Customer support

Ask for the order identifier when it is missing. Use `lookup_order` only after the user provides it. Summarize status plainly and do not invent delivery dates.
