# Payment Setup Guide

## Flutterwave Integration Setup

### 1. Update .env File

Add these Flutterwave configuration variables to your `.env` file:

```env
# Flutterwave Configuration
FLUTTERWAVE_PUBLIC_KEY=your_flutterwave_public_key_here
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret_key_here
FLUTTERWAVE_ENCRYPTION_KEY=your_flutterwave_encryption_key_here

# Frontend URL (for payment redirects)
FRONTEND_URL=https://algaddaftechhub.vercel.app
```

### 2. Get Flutterwave API Keys

1. Go to [Flutterwave Dashboard](https://dashboard.flutterwave.com/)
2. Sign up/Login to your account
3. Go to Settings > API Keys
4. Copy your:
   - **Public Key** (for frontend)
   - **Secret Key** (for backend)
   - **Encryption Key** (for security)

### 3. Test Mode vs Live Mode

- **Test Mode**: Use test API keys for development
- **Live Mode**: Use live API keys for production

### 4. Payment Flow

1. **Student clicks "Buy Now"** → Frontend calls `initiatePayment()`
2. **Backend creates payment record** → Returns Flutterwave payment URL
3. **Student redirected to Flutterwave** → Completes payment
4. **Flutterwave redirects back** → Frontend calls `verifyPayment()`
5. **Backend verifies payment** → Enrolls student in course

### 5. Course Pricing

- **Free Courses**: `is_free = True`, `price = 0`
- **Paid Courses**: `is_free = False`, `price = amount_in_naira`

### 6. Testing

1. Set up test courses with different prices
2. Use Flutterwave test cards for payment testing
3. Verify enrollment after successful payment

### 7. Production Deployment

1. Update `.env` with live Flutterwave keys
2. Set `DEBUG=False` for production
3. Update `FRONTEND_URL` to your live domain
4. Test with real payments (small amounts)

## API Endpoints

- `POST /api/courses/payments/initiate/` - Start payment
- `POST /api/courses/payments/verify/` - Verify payment
- `GET /api/courses/payments/history/` - Payment history
- `GET /api/courses/payments/{id}/status/` - Payment status

## Frontend Components

- Course cards show price and buy buttons
- Payment callback page handles return from Flutterwave
- Free courses show "Enroll Now" button
- Paid courses show "Buy Now" and "Preview" buttons




