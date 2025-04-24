export function orderStatusSMSTemplate(phoneNumber: string, orderId: string, status: string) {
  const safeOrderId = orderId || 'N/A';
  const safeStatus = status || 'processing';
  return {
    to: phoneNumber,
    message: `📦 Your order #${safeOrderId} has been updated to: ${safeStatus}. Thanks for shopping with us!`,
  };
}
