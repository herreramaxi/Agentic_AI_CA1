---
name: payment-options-inquiry
description: When a user asks to check available payment options, ask for their country/region to provide accurate methods.
---
# Payment Options Inquiry Skill

## Purpose
Handle user requests to view the payment methods we support. Payment options vary by country or region, so the assistant must gather the user's location before providing details.

## Procedure
1. **Acknowledge the request positively**
   - Use a friendly tone (e.g., "Positively! I'm here to help you check the available payment options.")
2. **Ask for the user's country or region**
   - Phrase the request clearly: "Could you please let me know which country or region you are in?"
   - Explain why: "This will help me give you accurate and relevant details about the payment methods we offer in your area."
3. **Wait for the user’s response**
   - Do not provide any payment options until the location is known.
4. **After receiving the location**
   - Provide a concise list of the payment methods available for that specific country/region.
   - If you do not have the exact list memorized, respond with: "Based on the information I have, the following payment options are available in [Country/Region]: …"
   - Offer to give more details about any method the user is interested in.
5. **If the user cannot specify a location**
   - Offer a generic fallback: "Our most common global payment methods include credit/debit cards, PayPal, and bank transfers. Let me know if you’d like details for a specific country when you have that information."
6. **Close politely**
   - Thank the user and ask if they need anything else.

## Key Points to Preserve
- Payment options are location‑dependent.
- Always ask for the country/region before listing options.
- Maintain a helpful, courteous tone throughout.
- Do not assume any payment method without confirming the region.

---
*This skill should be invoked for any query that mentions checking or viewing payment options, methods, or ways to pay.*