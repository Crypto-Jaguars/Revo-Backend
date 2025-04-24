import { Test, TestingModule } from '@nestjs/testing';
import { Repository } from 'typeorm';
import { Payment } from '../entities/payment.entity';
import { PaymentDto } from '../dtos/payment.dto';
import { getRepositoryToken } from '@nestjs/typeorm';
import { ConfigService } from '@nestjs/config';
import Stripe from 'stripe';
import { HttpException } from '@nestjs/common';
import { PaymentService } from '../services/payment.service';

const mockPaymentRepository = {
  create: jest.fn(),
  save: jest.fn(),
  findOne: jest.fn(),
  find: jest.fn(),
  update: jest.fn(),
};

const mockConfigService = {
  get: jest.fn().mockReturnValue('test-secret-key'),
};

describe('PaymentService', () => {
  let service: PaymentService;
  let paymentRepository: Repository<Payment>;
  let stripeInstance: Stripe;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        PaymentService,
        { provide: getRepositoryToken(Payment), useValue: mockPaymentRepository },
        { provide: ConfigService, useValue: mockConfigService },
      ],
    }).compile();

    service = module.get<PaymentService>(PaymentService);
    paymentRepository = module.get<Repository<Payment>>(getRepositoryToken(Payment));
    stripeInstance = (service as any).stripe;
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('processPayment', () => {
    it('should throw an error for invalid payment amount', async () => {
      const paymentDto: PaymentDto = { userId: 1, orderId: 1, amount: 0, currency: 'USD' };
      await expect(service.processPayment(paymentDto)).rejects.toThrow(HttpException);
    });

    it('should create a payment successfully', async () => {
      const paymentDto: PaymentDto = { userId: 1, orderId: 1, amount: 100, currency: 'USD' };
      jest.spyOn(stripeInstance.paymentIntents, 'create').mockResolvedValue({ id: 'pi_test' } as any);
      mockPaymentRepository.create.mockReturnValue({ ...paymentDto, transactionId: 'pi_test', status: 'pending' });
      mockPaymentRepository.save.mockResolvedValue({ ...paymentDto, transactionId: 'pi_test', status: 'pending' });
      
      const result = await service.processPayment(paymentDto);
      expect(result).toHaveProperty('transactionId', 'pi_test');
    });
  });

  describe('refundPayment', () => {
    it('should process a refund successfully', async () => {
      jest.spyOn(stripeInstance.refunds, 'create').mockResolvedValue({ id: 're_test' } as any);
      mockPaymentRepository.update.mockResolvedValue({});
      
      const result = await service.refundPayment('pi_test');
      expect(result).toHaveProperty('id', 're_test');
    });

    it('should throw an error if refund fails', async () => {
      jest.spyOn(stripeInstance.refunds, 'create').mockRejectedValue(new Error('Refund error'));
      await expect(service.refundPayment('pi_test')).rejects.toThrow(HttpException);
    });
  });

  describe('getPaymentStatus', () => {
    it('should return payment details', async () => {
      const payment = { transactionId: 'pi_test', status: 'completed' };
      mockPaymentRepository.findOne.mockResolvedValue(payment);
      
      const result = await service.getPaymentStatus('pi_test');
      expect(result).toEqual(payment);
    });

    it('should throw an error if payment not found', async () => {
      mockPaymentRepository.findOne.mockResolvedValue(null);
      await expect(service.getPaymentStatus('pi_test')).rejects.toThrow(HttpException);
    });
  });

  describe('getPaymentsByUserId', () => {
    it('should return payments for a user', async () => {
      const payments = [{ userId: 1, amount: 100, status: 'completed' }];
      mockPaymentRepository.find.mockResolvedValue(payments);
      
      const result = await service.getPaymentsByUserId(1);
      expect(result).toEqual(payments);
    });

    it('should throw an error if no payments found', async () => {
      mockPaymentRepository.find.mockResolvedValue([]);
      await expect(service.getPaymentsByUserId(1)).rejects.toThrow(HttpException);
    });
  });
});