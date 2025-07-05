
import React from 'react';
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';

const CheckoutForm: React.FC = () => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      // Stripe.js has not yet loaded. Make sure to disable form submission until Stripe.js has loaded.
      return;
    }

    // In a real application, you would create a PaymentMethod or confirm a PaymentIntent here.
    // This is a simplified example.
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    });

    if (error) {
      console.log('[error]', error);
    } else {
      console.log('[PaymentMethod]', paymentMethod);
      alert('Payment method created! Check console for details.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded-md">
      <h3 className="text-lg font-semibold mb-4">Make a Payment</h3>
      <div className="mb-4">
        <CardElement className="p-2 border rounded-md" />
      </div>
      <Button type="submit" disabled={!stripe}>Pay</Button>
    </form>
  );
};

export default CheckoutForm;
