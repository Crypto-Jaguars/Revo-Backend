import { HttpException, HttpStatus, Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import Stripe from 'stripe';
import { PaymentDto } from '../dtos/payment.dto';
import { Payment } from '../entities/payment.entity';
import * as crypto from 'crypto';

@Injectable()
export class PaymentService {
  private stripe: Stripe;
  private readonly logger = new Logger(PaymentService.name);

  constructor(
    @InjectRepository(Payment)
    private paymentRepository: Repository<Payment>,
    private configService: ConfigService,
  ) {
    this.stripe = new Stripe(this.configService.get<string>('STRIPE_SECRET_KEY'), {
      apiVersion: '2025-02-24.acacia',
    });
  }

  async processPayment(paymentDto: PaymentDto) {
    if (!paymentDto.amount || paymentDto.amount <= 0) {
      throw new HttpException('Invalid payment amount', HttpStatus.BAD_REQUEST);
    }

    const maxRetries = 3;
    let attempt = 0;
    let paymentIntent: Stripe.PaymentIntent | null = null;
    let delay = 500;

    while (attempt < maxRetries) {
      try {
        paymentIntent = await this.stripe.paymentIntents.create({
          amount: paymentDto.amount * 100,
          currency: paymentDto.currency,
          metadata: { userId: paymentDto.userId, orderId: paymentDto.orderId },
        }, { idempotencyKey: crypto.randomUUID() });
        break;
      } catch (error) {
        attempt++;
        this.logger.warn(`Payment attempt ${attempt} failed: ${error.message}`);
        if (attempt >= maxRetries) {
          this.logger.error('Payment processing failed after multiple attempts', error);
          throw new HttpException('Payment processing failed', HttpStatus.BAD_REQUEST);
        }
        await new Promise(res => setTimeout(res, delay));
        delay *= 2;
      }
    }

    const trackingId = generateUniqueCode(6);

    const payment = this.paymentRepository.create({
      userId: paymentDto.userId,
      orderId: paymentDto.orderId,
      amount: paymentDto.amount,
      currency: paymentDto.currency,
      transactionId: paymentIntent.id,
      trackingId: trackingId,
      status: 'pending',
    });
    return await this.paymentRepository.save(payment);
  }

  async refundPayment(transactionId: string) {
    try {
      const refund = await this.stripe.refunds.create({
        payment_intent: transactionId,
      });
      await this.paymentRepository.update({ transactionId }, { status: 'refunded' });
      return refund;
    } catch (error) {
      this.logger.error('Refund processing failed', error);
      throw new HttpException('Refund processing failed', HttpStatus.BAD_REQUEST);
    }
  }

  async getPaymentStatus(transactionId: string) {
    const payment = await this.paymentRepository.findOne({ where: { transactionId } });
    if (!payment) {
      throw new HttpException('Payment not found', HttpStatus.NOT_FOUND);
    }
    return payment;
  }

  async getPaymentByTrackingId(trackingId: string) {
    const payment = await this.paymentRepository.findOne({ where: { trackingId } });
    if (!payment) {
      throw new HttpException('Tracking ID not found', HttpStatus.NOT_FOUND);
    }
    return payment;
  }

  async getPaymentsByUserId(userId: number) {
    const payments = await this.paymentRepository.find({ where: { userId } });
    if (!payments.length) {
      throw new HttpException('No payments found for this user', HttpStatus.NOT_FOUND);
    }
    return payments;
  }

  async handleWebhook(event: Stripe.Event) {
    try {
      switch (event.type) {
        case 'payment_intent.succeeded':
          const paymentIntent = event.data.object as Stripe.PaymentIntent;
          await this.paymentRepository.update({ transactionId: paymentIntent.id }, { status: 'completed' });
          break;
        case 'payment_intent.payment_failed':
          const failedIntent = event.data.object as Stripe.PaymentIntent;
          await this.paymentRepository.update({ transactionId: failedIntent.id }, { status: 'failed' });
          break;
        case 'charge.refunded':
          const refund = event.data.object as unknown as Stripe.Refund;
          await this.paymentRepository.update({ transactionId: refund.payment_intent as string }, { status: 'refunded' });
          break;
        default:
          this.logger.warn(`Unhandled event type: ${event.type}`);
      }
    } catch (error) {
      this.logger.error('Webhook processing failed', error);
      throw new HttpException('Webhook processing failed', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}

export function generateUniqueCode(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * chars.length);
    result += chars[randomIndex];
  }
  return result;
}
