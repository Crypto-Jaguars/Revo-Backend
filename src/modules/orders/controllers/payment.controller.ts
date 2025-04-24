import { Controller, Post, Get, Body, Param, Req } from '@nestjs/common';
import { PaymentService } from '../services/payment.service';
import { Request } from 'express';
import Stripe from 'stripe';
import { PaymentDto } from '../dtos/payment.dto';

@Controller('payments')
export class PaymentController {
  constructor(private readonly paymentService: PaymentService) {}

  @Post()
  async processPayment(@Body() paymentDto: PaymentDto) {
    return this.paymentService.processPayment(paymentDto);
  }

  @Post('refund/:transactionId')
  async refundPayment(@Param('transactionId') transactionId: string) {
    return this.paymentService.refundPayment(transactionId);
  }

  @Get(':transactionId')
  async getPaymentStatus(@Param('transactionId') transactionId: string) {
    return this.paymentService.getPaymentStatus(transactionId);
  }

  @Get('track/:trackingId')
  async getPaymentByTrackingId(@Param('trackingId') trackingId: string) {
    return this.paymentService.getPaymentByTrackingId(trackingId);
  }

  @Get('user/:userId')
  async getPaymentsByUserId(@Param('userId') userId: number) {
    return this.paymentService.getPaymentsByUserId(userId);
  }

  @Post('webhook')
  async handleWebhook(@Req() request: Request) {
    const event: Stripe.Event = request.body;
    return this.paymentService.handleWebhook(event);
  }
}
