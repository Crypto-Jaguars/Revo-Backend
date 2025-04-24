import { Test, TestingModule } from '@nestjs/testing';
import { OrderController } from './order.controller';
import { OrderService } from '../services/order.service';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';

describe('Sales Report API', () => {
  let app: INestApplication;

  // Mock OrderService
  const mockOrderService = {
    getSalesReport: jest.fn().mockResolvedValue({
      totalSales: 5000,
      totalOrders: 100,
    }),
  };

  beforeAll(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [OrderController], // Your controller that handles the endpoint
      providers: [
        {
          provide: OrderService,
          useValue: mockOrderService, // Mock the OrderService
        },
      ],
    }).compile();

    app = module.createNestApplication();
    await app.init();
  });

  it('should return correct sales data for a given date range', async () => {
    const result = await request
      .default(app.getHttpServer())
      .get('/orders/sales-report?startDate=2025-01-01&endDate=2025-01-31')
      .expect(200);

    expect(result.body).toEqual(
      expect.objectContaining({
        totalSales: expect.any(Number),
        totalOrders: expect.any(Number),
      }),
    );
  });

  afterAll(async () => {
    await app.close();
  });
});
